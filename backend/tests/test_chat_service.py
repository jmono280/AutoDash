import json
from types import SimpleNamespace as NS

import httpx
import pytest
from mcp.server import MCPServer
from openai import RateLimitError

from app.core.config import settings
from app.schemas.chat import ChatChunk, ChatMessage, ChatRequest
from app.services.chat_service import ChatService

fake_mcp = MCPServer("test")


@fake_mcp.tool()
async def get_wip_kpis() -> dict:
    """WIP KPIs."""
    return {"total_ros": 256}


@fake_mcp.tool()
async def broken_tool() -> dict:
    """Always fails."""
    raise ValueError("db down")


def _content(text):
    return NS(choices=[NS(delta=NS(content=text, tool_calls=None))])


def _tool_delta(index, id=None, name=None, arguments=None):
    tc = NS(index=index, id=id, function=NS(name=name, arguments=arguments))
    return NS(choices=[NS(delta=NS(content=None, tool_calls=[tc]))])


class _Stream:
    def __init__(self, chunks):
        self._chunks = iter(chunks)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._chunks)
        except StopIteration:
            raise StopAsyncIteration


class FakeOpenAI:
    """Replays one scripted stream per completion call and records the requests."""

    def __init__(self, rounds):
        self._rounds = iter(rounds)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    async def _create(self, **kwargs):
        self.calls.append(json.loads(json.dumps(kwargs)))
        item = next(self._rounds)
        if isinstance(item, Exception):
            raise item
        return _Stream(item)


def _request(text="¿Cuántas ROs abiertas hay?"):
    return ChatRequest(messages=[ChatMessage(role="user", content=text)])


async def _collect(service, req):
    return [chunk async for chunk in service._run(req)]


@pytest.mark.anyio
async def test_runs_requested_tool_and_feeds_result_back_to_the_model():
    client = FakeOpenAI([
        [  # tool call split across deltas, as providers stream it
            _tool_delta(0, id="call_1", name="get_wip", arguments=""),
            _tool_delta(0, name="_kpis", arguments="{}"),
        ],
        [_content("Hay 256 "), _content("ROs abiertas.")],
    ])
    service = ChatService(client=client, mcp_server=fake_mcp)

    chunks = await _collect(service, _request())

    assert chunks == [
        ChatChunk(tool="get_wip_kpis"),
        ChatChunk(delta="Hay 256 "),
        ChatChunk(delta="ROs abiertas."),
    ]
    first, second = client.calls
    assert {t["function"]["name"] for t in first["tools"]} == {"get_wip_kpis", "broken_tool"}
    assert first["messages"][0]["role"] == "system"
    assistant, tool = second["messages"][-2:]
    assert assistant["tool_calls"][0]["function"] == {"name": "get_wip_kpis", "arguments": "{}"}
    assert tool["role"] == "tool" and tool["tool_call_id"] == "call_1"
    assert json.loads(tool["content"]) == {"total_ros": 256}


@pytest.mark.anyio
async def test_tool_failure_is_returned_to_the_model_instead_of_aborting():
    client = FakeOpenAI([
        [_tool_delta(0, id="c1", name="broken_tool", arguments="{}")],
        [_content("No pude obtener los datos.")],
    ])
    service = ChatService(client=client, mcp_server=fake_mcp)

    chunks = await _collect(service, _request())

    assert chunks[-1] == ChatChunk(delta="No pude obtener los datos.")
    tool_msg = client.calls[1]["messages"][-1]
    assert "error" in json.loads(tool_msg["content"])


@pytest.mark.anyio
async def test_stops_offering_tools_after_max_iterations(monkeypatch):
    monkeypatch.setattr(settings, "CHAT_MAX_TOOL_ITERATIONS", 2)
    looping = [_tool_delta(0, id="c", name="get_wip_kpis", arguments="{}")]
    client = FakeOpenAI([looping, looping, [_content("Resumen final.")]])
    service = ChatService(client=client, mcp_server=fake_mcp)

    chunks = await _collect(service, _request())

    assert len(client.calls) == 3
    assert "tools" in client.calls[0] and "tools" in client.calls[1]
    assert "tools" not in client.calls[2]
    assert chunks[-1] == ChatChunk(delta="Resumen final.")


@pytest.mark.anyio
async def test_history_is_trimmed_to_max_history(monkeypatch):
    monkeypatch.setattr(settings, "OPENROUTER_MAX_HISTORY", 2)
    client = FakeOpenAI([[_content("ok")]])
    service = ChatService(client=client, mcp_server=fake_mcp)
    req = ChatRequest(messages=[
        ChatMessage(role="user", content="uno"),
        ChatMessage(role="assistant", content="dos"),
        ChatMessage(role="user", content="tres"),
    ])

    await _collect(service, req)

    sent = client.calls[0]["messages"]
    assert [m["content"] for m in sent[1:]] == ["dos", "tres"]


@pytest.mark.anyio
async def test_complete_returns_full_answer():
    client = FakeOpenAI([[_content("Hola "), _content("mundo")]])
    service = ChatService(client=client, mcp_server=fake_mcp)

    response = await service.complete(_request())

    assert response.message.content == "Hola mundo"
    assert response.model == settings.OPENROUTER_MODEL


@pytest.mark.anyio
async def test_stream_emits_sse_events_and_reports_provider_errors():
    request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
    rate_limited = RateLimitError(
        "slow down", response=httpx.Response(429, request=request), body=None
    )
    client = FakeOpenAI([
        [_tool_delta(0, id="c", name="get_wip_kpis", arguments="{}")],
        rate_limited,
    ])
    service = ChatService(client=client, mcp_server=fake_mcp)

    events = [e async for e in service.stream(_request())]

    assert events[0] == 'data: {"delta":"","done":false,"tool":"get_wip_kpis"}\n\n'
    assert json.loads(events[1][6:])["error"] == "rate_limit"
    assert events[-2] == 'data: {"delta":"","done":true}\n\n'
    assert events[-1] == "data: [DONE]\n\n"
