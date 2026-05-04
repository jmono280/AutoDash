from __future__ import annotations

import math
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.wip_repo import WipRepository
from app.schemas.work_in_progress import (
    AdvisorGroup,
    AgingBucket,
    CategoryGroup,
    Page,
    WipKpisOut,
    WipOut,
)


@dataclass
class WipFilters:
    advisor: str | None = field(default=None)
    category: str | None = field(default=None)
    min_days: int | None = field(default=None)
    max_days: int | None = field(default=None)


class WipService:
    def __init__(self, repo: WipRepository | None = None):
        self.repo = repo or WipRepository()

    async def list(
        self,
        db: AsyncSession,
        filters: WipFilters,
        page: int = 1,
        limit: int = 50,
    ) -> Page[WipOut]:
        filter_kwargs = {
            "advisor": filters.advisor,
            "category": filters.category,
            "min_days": filters.min_days,
            "max_days": filters.max_days,
        }
        total = await self.repo.count(db, **filter_kwargs)
        items = await self.repo.list(db, **filter_kwargs, page=page, limit=limit)
        pages = math.ceil(total / limit) if total > 0 else 1
        return Page(
            items=[WipOut.model_validate(r) for r in items],
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )

    async def get_kpis(self, db: AsyncSession) -> WipKpisOut:
        data = await self.repo.get_kpis(db)
        return WipKpisOut(**data)

    async def get_aging(self, db: AsyncSession) -> list[AgingBucket]:
        rows = await self.repo.get_aging(db)
        return [AgingBucket(**r) for r in rows]

    async def get_by_category(self, db: AsyncSession) -> list[CategoryGroup]:
        rows = await self.repo.get_by_category(db)
        return [CategoryGroup(**r) for r in rows]

    async def get_by_advisor(self, db: AsyncSession) -> list[AdvisorGroup]:
        rows = await self.repo.get_by_advisor(db)
        return [AdvisorGroup(**r) for r in rows]
