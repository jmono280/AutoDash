from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole


class UserRepository:
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalars().first()

    async def get_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> User | None:
        result = await db.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        return result.scalars().first()

    async def create(
        self,
        db: AsyncSession,
        *,
        email: str,
        hashed_password: str,
        full_name: str,
        role: UserRole = UserRole.viewer,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
