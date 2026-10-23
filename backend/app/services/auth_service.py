from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepository
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    SessionTokens,
    UserOut,
)


class AuthService:
    def __init__(self, repo: UserRepository | None = None):
        self.repo = repo or UserRepository()

    async def login(self, db: AsyncSession, req: LoginRequest) -> SessionTokens:
        user = await self.repo.get_by_email(db, req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive",
            )
        return _issue(user.email, remember=req.remember_me)

    async def refresh(self, db: AsyncSession, refresh_token: str | None) -> SessionTokens:
        data = decode_token(refresh_token, REFRESH) if refresh_token else None
        if not data or "sub" not in data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
        user = await self.repo.get_by_email(db, data["sub"])
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        # Rotate the refresh token, keeping the persistence the user chose at login
        return _issue(user.email, remember=bool(data.get("remember", False)))

    def get_me(self, current_user: User) -> UserOut:
        return UserOut.model_validate(current_user)

    async def change_password(
        self,
        db: AsyncSession,
        current_user: User,
        current_password: str,
        new_password: str,
    ) -> MessageResponse:
        if not verify_password(current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta",
            )

        hashed = hash_password(new_password)
        await self.repo.update_password(db, current_user, hashed)
        return MessageResponse(message="Contraseña actualizada correctamente")

    async def register(
        self,
        db: AsyncSession,
        *,
        email: str,
        password: str,
        full_name: str,
        role: UserRole = UserRole.viewer,
    ) -> UserOut:
        existing = await self.repo.get_by_email(db, email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        user = await self.repo.create(
            db,
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=role,
        )
        return UserOut.model_validate(user)


def _issue(email: str, *, remember: bool) -> SessionTokens:
    payload = {"sub": email}
    return SessionTokens(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload, remember=remember),
        remember=remember,
    )
