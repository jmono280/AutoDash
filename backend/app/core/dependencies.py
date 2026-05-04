from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.database import get_db
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_401 = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
_403 = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(token)
    if payload is None:
        raise _401
    email: str | None = payload.get("sub")
    if email is None:
        raise _401
    result = await db.execute(
        select(User).where(User.email == email, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise _401
    return user


async def get_current_admin(
    user: User = Depends(get_current_user),
) -> User:
    if user.role != UserRole.admin:
        raise _403
    return user
