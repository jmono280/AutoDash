from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call_analytics import CallAnalytics


class CallAnalyticsRepository:

    async def get_range(
        self,
        db: AsyncSession,
        date_from: datetime,
        date_to: datetime,
        extension: str | None = None,
    ) -> list[CallAnalytics]:
        q = (
            select(CallAnalytics)
            .where(
                CallAnalytics.time_from <= date_to,
                CallAnalytics.time_to   >= date_from,
                CallAnalytics.deleted_at.is_(None),
            )
            .order_by(CallAnalytics.time_from, CallAnalytics.extension_number)
        )
        if extension is not None:
            q = q.where(CallAnalytics.extension_number == extension)
        result = await db.execute(q)
        return list(result.scalars().all())

    async def get_kpis(
        self,
        db: AsyncSession,
        date_from: datetime,
        date_to: datetime,
    ) -> dict:
        result = await db.execute(
            select(
                func.coalesce(func.sum(CallAnalytics.total_calls),      0).label("total_calls"),
                func.coalesce(func.sum(CallAnalytics.inbound),          0).label("total_inbound"),
                func.coalesce(func.sum(CallAnalytics.outbound),         0).label("total_outbound"),
                func.coalesce(func.sum(CallAnalytics.answered),         0).label("total_answered"),
                func.coalesce(func.sum(CallAnalytics.not_answered),     0).label("total_not_answered"),
                func.coalesce(func.sum(CallAnalytics.completed),        0).label("total_completed"),
                func.coalesce(func.sum(CallAnalytics.abandoned),        0).label("total_abandoned"),
                func.coalesce(func.sum(CallAnalytics.voicemail),        0).label("total_voicemail"),
                func.coalesce(func.sum(CallAnalytics.duration_seconds), 0).label("total_duration_seconds"),
                func.count(func.distinct(CallAnalytics.extension_number)).label("extension_count"),
            ).where(
                CallAnalytics.time_from <= date_to,
                CallAnalytics.time_to   >= date_from,
                CallAnalytics.deleted_at.is_(None),
            )
        )
        row = result.one()
        return row._asdict()

    async def get_by_extension(
        self,
        db: AsyncSession,
        date_from: datetime,
        date_to: datetime,
    ) -> list[dict]:
        result = await db.execute(
            select(
                CallAnalytics.extension_number,
                func.max(CallAnalytics.extension_name).label("extension_name"),
                func.sum(CallAnalytics.total_calls).label("total_calls"),
                func.sum(CallAnalytics.inbound).label("inbound"),
                func.sum(CallAnalytics.outbound).label("outbound"),
                func.sum(CallAnalytics.answered).label("answered"),
                func.sum(CallAnalytics.not_answered).label("not_answered"),
                func.sum(CallAnalytics.completed).label("completed"),
                func.sum(CallAnalytics.abandoned).label("abandoned"),
                func.sum(CallAnalytics.voicemail).label("voicemail"),
                func.sum(CallAnalytics.duration_seconds).label("duration_seconds"),
            )
            .where(
                CallAnalytics.time_from <= date_to,
                CallAnalytics.time_to   >= date_from,
                CallAnalytics.deleted_at.is_(None),
            )
            .group_by(CallAnalytics.extension_number)
            .order_by(CallAnalytics.extension_number)
        )
        return [row._asdict() for row in result.all()]

    async def upsert_run(
        self,
        db: AsyncSession,
        rows: list[dict],
        time_from: datetime,
        time_to: datetime,
    ) -> None:
        await db.execute(
            delete(CallAnalytics).where(
                CallAnalytics.time_from == time_from,
                CallAnalytics.time_to   == time_to,
            )
        )
        if rows:
            await db.execute(insert(CallAnalytics), rows)
        await db.commit()
