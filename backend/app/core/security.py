from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


ACCESS = "access"
REFRESH = "refresh"


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {**data, "type": ACCESS, "exp": datetime.now(timezone.utc) + delta}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def refresh_token_max_age(remember: bool) -> int:
    """Lifetime in seconds of a refresh token (and of its cookie when remembered)."""
    days = settings.REMEMBER_ME_EXPIRE_DAYS if remember else settings.REFRESH_TOKEN_EXPIRE_DAYS
    return days * 86400


def create_refresh_token(data: dict, remember: bool) -> str:
    delta = timedelta(seconds=refresh_token_max_age(remember))
    payload = {
        **data,
        "type": REFRESH,
        "remember": remember,
        "exp": datetime.now(timezone.utc) + delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str, token_type: str) -> dict | None:
    """Decode a JWT and require it to be of the given type (access or refresh)."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
    if payload.get("type") != token_type:
        return None
    return payload
