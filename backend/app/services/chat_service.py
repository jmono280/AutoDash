from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from datetime import date
from typing import Any

from fastapi import HTTPException
from mcp import Client
from mcp.server import MCPServer
from openai import APIConnectionError, APIStatusError, APITimeoutError, AsyncOpenAI, RateLimitError

from app.core.config import settings
from app.mcp.server import server as default_mcp_server
from app.schemas.chat import ChatChunk, ChatMessage, ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

_MAX_TOOL_RESULT_CHARS = 12_000


class ChatService:
    """Agent loop: the LLM requests data through the MCP tools until it can answer."""

    _SYSTEM_BASE = (
        "Eres un asistente de análisis para Automania, taller mecánico y concesionario. "
        "Ayudas a interpretar métricas operativas y financieras. "
        "Responde de forma concisa y práctica en español.\n"
        "Reglas:\n"
        "- Usa SIEMPRE las herramientas para obtener datos; nunca inventes cifras.\n"
        "- Si el usuario no indica período, llama primero a get_data_coverage y usa el período "
        "más reciente con datos.\n"
        "- Indica en la respuesta el período o año que usaste.\n"
        "- Si una herramienta devuelve un error o no hay datos, dilo claramente.\n"
        "- No anuncies qué herramientas vas a usar; responde directamente con el resultado."
    )

    def __init__(
        self,
        client: AsyncOpenAI | None = None,
        mcp_server: MCPServer = default_mcp_server,
    ) -> None:
        self._client = client or AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        self._mcp_server = mcp_server

    def _build_messages(self, messages: list[ChatMessage]) -> list[dict[str, Any]]:
        if len(messages) > settings.OPENROUTER_MAX_HISTORY:
            messages = messages[-settings.OPENROUTER_MAX_HISTORY :]

        system = self._SYSTEM_BASE + f"\nFecha de hoy: {date.today().isoformat()}."
        return [{"role": "system", "content": system}] + [
            {"role": m.role, "content": m.content} for m in messages
        ]

    @staticmethod
    async def _openai_tools(mcp: Client) -> list[dict[str, Any]]:
        result = await mcp.list_tools()
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": t.input_schema,
                },
            }
            for t in result.tools
        ]

    @staticmethod
    async def _call_tool(mcp: Client, name: str, raw_args: str) -> str:
        try:
            args = json.loads(raw_args) if raw_args else {}
            result = await mcp.call_tool(name, args)
        except Exception as exc:
            logger.exception("Chat tool %s failed", name)
            return json.dumps({"error": f"{type(exc).__name__}: {exc}"})

        text = "\n".join(getattr(c, "text", "") for c in result.content)
        if result.is_error:
            logger.warning("Chat tool %s returned an error: %s", name, text)
            return json.dumps({"error": text})
        return text[:_MAX_TOOL_RESULT_CHARS]

    async def _run(self, req: ChatRequest) -> AsyncGenerator[ChatChunk, None]:
        """Yield tool notifications and answer deltas. OpenAI errors propagate to the caller."""
        messages = self._build_messages(req.messages)
        failure: Exception | None = None

        async with Client(self._mcp_server) as mcp:
            # Errors raised inside the client's task group would surface wrapped in an
            # ExceptionGroup; capture them and re-raise once the client is closed.
            try:
                async for chunk in self._agent_loop(mcp, messages):
                    yield chunk
            except Exception as exc:
                failure = exc

        if failure is not None:
            raise failure

    async def _agent_loop(
        self, mcp: Client, messages: list[dict[str, Any]]
    ) -> AsyncGenerator[ChatChunk, None]:
        max_rounds = settings.CHAT_MAX_TOOL_ITERATIONS
        tools = await self._openai_tools(mcp)

        for round_no in range(max_rounds + 1):
            # Last round goes without tools to force a final answer.
            use_tools = round_no < max_rounds
            kwargs: dict[str, Any] = {"tools": tools} if use_tools else {}
            stream = await self._client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=messages,
                max_tokens=settings.OPENROUTER_MAX_TOKENS_OUT,
                stream=True,
                **kwargs,
            )

            content = ""
            calls: dict[int, dict[str, str]] = {}
            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta.content:
                    content += delta.content
                    yield ChatChunk(delta=delta.content)
                for tc in delta.tool_calls or []:
                    call = calls.setdefault(tc.index, {"id": "", "name": "", "arguments": ""})
                    call["id"] += tc.id or ""
                    if tc.function:
                        call["name"] += tc.function.name or ""
                        call["arguments"] += tc.function.arguments or ""

            if not calls:
                return

            ordered = [calls[i] for i in sorted(calls)]
            messages.append(
                {
                    "role": "assistant",
                    "content": content or None,
                    "tool_calls": [
                        {
                            "id": c["id"],
                            "type": "function",
                            "function": {"name": c["name"], "arguments": c["arguments"]},
                        }
                        for c in ordered
                    ],
                }
            )
            for c in ordered:
                yield ChatChunk(tool=c["name"])
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": c["id"],
                        "content": await self._call_tool(mcp, c["name"], c["arguments"]),
                    }
                )

    async def complete(self, req: ChatRequest) -> ChatResponse:
        content = ""
        try:
            async for chunk in self._run(req):
                content += chunk.delta
        except RateLimitError as exc:
            raise _http_error(429, "Rate limit exceeded") from exc
        except APITimeoutError as exc:
            raise _http_error(504, "OpenRouter timeout") from exc
        except APIStatusError as exc:
            raise _http_error(exc.status_code, exc.message) from exc
        except APIConnectionError as exc:
            raise _http_error(503, "OpenRouter unreachable") from exc

        return ChatResponse(
            message=ChatMessage(role="assistant", content=content),
            model=settings.OPENROUTER_MODEL,
        )

    async def stream(self, req: ChatRequest) -> AsyncGenerator[str, None]:
        try:
            async for chunk in self._run(req):
                yield _sse(chunk)
        except RateLimitError as exc:
            yield _sse(ChatChunk(error="rate_limit", detail=str(exc)))
        except APIStatusError as exc:
            yield _sse(ChatChunk(error="api_error", detail=f"{exc.status_code}: {exc.message}"))
        except (APIConnectionError, APITimeoutError) as exc:
            yield _sse(ChatChunk(error="connection_error", detail=str(exc)))
        except Exception as exc:
            logger.exception("Chat stream failed")
            yield _sse(ChatChunk(error="internal_error", detail=type(exc).__name__))
        finally:
            yield _sse(ChatChunk(done=True))
            yield "data: [DONE]\n\n"


def _sse(chunk: ChatChunk) -> str:
    return f"data: {chunk.model_dump_json(exclude_none=True)}\n\n"


def _http_error(status_code: int, detail: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail=f"OpenRouter: {detail}")
