from __future__ import annotations

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.daily_sales_repo import DailySalesRepository
from app.schemas.daily_sales import DailySalesOut, DayOfWeekStats, SalesKpisOut, TrendPoint


class SalesService:
    def __init__(self, repo: DailySalesRepository | None = None):
        self.repo = repo or DailySalesRepository()

    async def get_kpis(self, db: AsyncSession, start: date, end: date) -> SalesKpisOut:
        data = await self.repo.get_kpis(db, start, end)
        return SalesKpisOut(**data)

    async def get_trend(
        self, db: AsyncSession, start: date, end: date
    ) -> list[TrendPoint]:
        rows = await self.repo.get_trend(db, start, end)
        return [TrendPoint(**r) for r in rows]

    async def get_by_day_of_week(
        self, db: AsyncSession, start: date, end: date
    ) -> list[DayOfWeekStats]:
        rows = await self.repo.get_by_day_of_week(db, start, end)
        return [DayOfWeekStats(**r) for r in rows]

    async def list_range(
        self, db: AsyncSession, start: date, end: date
    ) -> list[DailySalesOut]:
        rows = await self.repo.get_range(db, start, end)
        return [DailySalesOut.model_validate(r) for r in rows]
