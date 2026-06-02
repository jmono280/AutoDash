from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.call_analytics_repo import CallAnalyticsRepository
from app.schemas.call_analytics import (
    CallAnalyticsByExtensionOut,
    CallAnalyticsKpisOut,
    CallAnalyticsOut,
)


class CallAnalyticsService:
    def __init__(self, repo: CallAnalyticsRepository | None = None) -> None:
        self.repo = repo or CallAnalyticsRepository()

    async def list_range(
        self,
        db: AsyncSession,
        date_from: datetime,
        date_to: datetime,
        extension: str | None = None,
    ) -> list[CallAnalyticsOut]:
        rows = await self.repo.get_range(db, date_from, date_to, extension)
        return [CallAnalyticsOut.model_validate(r) for r in rows]

    async def get_kpis(
        self,
        db: AsyncSession,
        date_from: datetime,
        date_to: datetime,
    ) -> CallAnalyticsKpisOut:
        data = await self.repo.get_kpis(db, date_from, date_to)
        return CallAnalyticsKpisOut(**data)

    async def get_by_extension(
        self,
        db: AsyncSession,
        date_from: datetime,
        date_to: datetime,
    ) -> list[CallAnalyticsByExtensionOut]:
        rows = await self.repo.get_by_extension(db, date_from, date_to)
        return [CallAnalyticsByExtensionOut(**r) for r in rows]
