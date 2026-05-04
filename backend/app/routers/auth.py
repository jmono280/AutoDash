from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserOut
from app.services.auth_service import AuthService

router = APIRouter()


def _service() -> AuthService:
    return AuthService()


@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(_service),
) -> TokenResponse:
    return await service.login(db, req)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    req: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(_service),
) -> TokenResponse:
    return await service.refresh(db, req)


@router.post("/logout")
async def logout() -> dict[str, str]:
    # Stateless JWT — token invalidation is handled client-side
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserOut)
async def me(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(_service),
) -> UserOut:
    return service.get_me(current_user)
