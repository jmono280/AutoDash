from __future__ import annotations

from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, Enum as SQLEnum, String

from .base import Base, TimestampMixin


class UserRole(PyEnum):
    admin = "admin"
    viewer = "viewer"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(SQLEnum(UserRole, name="user_role"), nullable=False, default=UserRole.viewer)
    is_active = Column(Boolean, nullable=False, default=True)
