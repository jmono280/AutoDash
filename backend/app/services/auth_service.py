from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserOut


class AuthService:
    def __init__(self, repo: UserRepository | None = None):
        self.repo = repo or UserRepository()

    async def login(self, db: AsyncSession, req: LoginRequest) -> TokenResponse:
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
        payload = {"sub": user.email}
        return TokenResponse(
            access_token=create_access_token(payload),
            refresh_token=create_refresh_token(payload),
        )

    async def refresh(self, db: AsyncSession, req: RefreshRequest) -> TokenResponse:
        data = decode_token(req.refresh_token)
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
        payload = {"sub": user.email}
        return TokenResponse(
            access_token=create_access_token(payload),
            refresh_token=create_refresh_token(payload),
        )

    def get_me(self, current_user: User) -> UserOut:
        return UserOut.model_validate(current_user)

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
