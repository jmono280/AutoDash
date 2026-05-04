"""Create a viewer (read-only) user.

Usage:
    python -m app.scripts.seed_viewer
    python -m app.scripts.seed_viewer viewer@automania.com viewer123
    python -m app.scripts.seed_viewer custom@email.com mypassword "Full Name"
"""
from __future__ import annotations

import asyncio
import sys

from app.core.security import hash_password
from app.database import AsyncSessionLocal
from app.models.user import UserRole
from app.repositories.user_repo import UserRepository


async def _seed(email: str, password: str, full_name: str) -> None:
    repo = UserRepository()
    async with AsyncSessionLocal() as db:
        existing = await repo.get_by_email(db, email)
        if existing:
            print(f"User already exists: {existing.email} (role={existing.role.value})")
            return
        user = await repo.create(
            db,
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=UserRole.viewer,
        )
        print(f"Viewer created: {user.email} (id={user.id})")


def main() -> None:
    email = sys.argv[1] if len(sys.argv) > 1 else "viewer@automania.com"
    password = sys.argv[2] if len(sys.argv) > 2 else "viewer123"
    full_name = sys.argv[3] if len(sys.argv) > 3 else "Viewer"
    asyncio.run(_seed(email, password, full_name))


if __name__ == "__main__":
    main()
