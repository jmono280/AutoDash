from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    context: str | None = None
    stream: bool = False


class ChatChunk(BaseModel):
    delta: str
    done: bool = False


class ChatResponse(BaseModel):
    message: ChatMessage
    model: str
