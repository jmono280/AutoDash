from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


def _service() -> ChatService:
    return ChatService()


@router.post("/completions", response_model=ChatResponse)
async def chat_completions(
    req: ChatRequest,
    service: ChatService = Depends(_service),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ChatResponse | StreamingResponse:
    if req.stream:
        return StreamingResponse(
            service.stream(req, db),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )
    return await service.complete(req, db)
