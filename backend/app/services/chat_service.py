from __future__ import annotations

import json
from collections.abc import AsyncGenerator

from openai import APIConnectionError, APIStatusError, APITimeoutError, AsyncOpenAI, RateLimitError

from app.core.config import settings
from app.schemas.chat import ChatChunk, ChatMessage, ChatRequest, ChatResponse


class ChatService:
    _SYSTEM_BASE = (
        "Eres un asistente de análisis para Automania, taller mecánico. "
        "Ayudas a interpretar métricas operativas y financieras. "
        "Responde de forma concisa y práctica."
    )

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

    def _build_messages(
        self, messages: list[ChatMessage], context: str | None
    ) -> list[dict[str, str]]:
        if len(messages) > settings.OPENROUTER_MAX_HISTORY:
            messages = messages[-settings.OPENROUTER_MAX_HISTORY :]

        system = self._SYSTEM_BASE
        if context:
            truncated = context[: settings.OPENROUTER_MAX_CONTEXT_CHARS]
            system += f"\n\nDatos actuales del dashboard:\n{truncated}"

        return [{"role": "system", "content": system}] + [
            {"role": m.role, "content": m.content} for m in messages
        ]

    async def complete(self, req: ChatRequest) -> ChatResponse:
        try:
            response = await self._client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=self._build_messages(req.messages, req.context),
                max_tokens=settings.OPENROUTER_MAX_TOKENS_OUT,
                stream=False,
            )
        except RateLimitError as exc:
            raise _http_error(429, "Rate limit exceeded") from exc
        except APITimeoutError as exc:
            raise _http_error(504, "OpenRouter timeout") from exc
        except APIStatusError as exc:
            raise _http_error(exc.status_code, exc.message) from exc
        except APIConnectionError as exc:
            raise _http_error(503, "OpenRouter unreachable") from exc

        choice = response.choices[0]
        return ChatResponse(
            message=ChatMessage(role="assistant", content=choice.message.content or ""),
            model=response.model,
        )

    async def stream(self, req: ChatRequest) -> AsyncGenerator[str, None]:
        try:
            async with await self._client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=self._build_messages(req.messages, req.context),
                max_tokens=settings.OPENROUTER_MAX_TOKENS_OUT,
                stream=True,
            ) as stream_response:
                async for chunk in stream_response:
                    delta = chunk.choices[0].delta.content
                    if delta is not None:
                        yield f"data: {ChatChunk(delta=delta).model_dump_json()}\n\n"
        except RateLimitError as exc:
            yield f"data: {json.dumps({'error': 'rate_limit', 'detail': str(exc)})}\n\n"
        except APIStatusError as exc:
            yield f"data: {json.dumps({'error': 'api_error', 'status': exc.status_code, 'detail': exc.message})}\n\n"
        except (APIConnectionError, APITimeoutError) as exc:
            yield f"data: {json.dumps({'error': 'connection_error', 'detail': str(exc)})}\n\n"
        finally:
            yield f"data: {ChatChunk(delta='', done=True).model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"


def _http_error(status_code: int, detail: str) -> Exception:
    from fastapi import HTTPException
    return HTTPException(status_code=status_code, detail=f"OpenRouter: {detail}")
