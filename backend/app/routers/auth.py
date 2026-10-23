from __future__ import annotations

from typing import Literal, cast

from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    PasswordChangeRequest,
    SessionTokens,
    TokenResponse,
    UserOut,
)
from app.core.config import settings
from app.core.security import refresh_token_max_age
from app.services.auth_service import AuthService

router = APIRouter()


def _service() -> AuthService:
    return AuthService()


def _set_refresh_cookie(response: Response, tokens: SessionTokens) -> TokenResponse:
    """Store the refresh token in an httpOnly cookie and return only the access token.

    Without "remember me" it is a session cookie, dropped when the browser closes.
    """
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=tokens.refresh_token,
        max_age=refresh_token_max_age(remember=True) if tokens.remember else None,
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=cast(Literal["lax", "strict", "none"], settings.REFRESH_COOKIE_SAMESITE),
        path="/",
    )
    return TokenResponse(access_token=tokens.access_token)


@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(_service),
) -> TokenResponse:
    return _set_refresh_cookie(response, await service.login(db, req))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=settings.REFRESH_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(_service),
) -> TokenResponse:
    return _set_refresh_cookie(response, await service.refresh(db, refresh_token))


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=cast(Literal["lax", "strict", "none"], settings.REFRESH_COOKIE_SAMESITE),
    )
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserOut)
async def me(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(_service),
) -> UserOut:
    return service.get_me(current_user)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    req: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(_service),
) -> MessageResponse:
    return await service.change_password(
        db,
        current_user,
        req.current_password,
        req.new_password,
    )
