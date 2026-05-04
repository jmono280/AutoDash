from __future__ import annotations

from datetime import date

from sqlalchemy import Column, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.technician_hours import TechnicianHours

_METRIC_COL: dict[str, Column] = {
    "labor_dollars": TechnicianHours.labor_dollars,
    "hours_sold": TechnicianHours.hours_sold,
    "proficiency": TechnicianHours.technician_proficiency,
}


class TechnicianRepository:
    async def get_range(
        self, db: AsyncSession, start: date, end: date
    ) -> list[TechnicianHours]:
        result = await db.execute(
            select(TechnicianHours)
            .where(
                TechnicianHours.period_start >= start,
                TechnicianHours.period_end <= end,
                TechnicianHours.deleted_at.is_(None),
            )
            .order_by(TechnicianHours.technician_name)
        )
        return list(result.scalars().all())

    async def get_ranking(
        self,
        db: AsyncSession,
        start: date,
        end: date,
        metric: str = "labor_dollars",
    ) -> list[TechnicianHours]:
        order_col = _METRIC_COL.get(metric, TechnicianHours.labor_dollars)
        result = await db.execute(
            select(TechnicianHours)
            .where(
                TechnicianHours.period_start >= start,
                TechnicianHours.period_end <= end,
                TechnicianHours.deleted_at.is_(None),
            )
            .order_by(order_col.desc().nulls_last())
        )
        return list(result.scalars().all())

    async def get_by_name(
        self, db: AsyncSession, name: str, start: date, end: date
    ) -> list[TechnicianHours]:
        result = await db.execute(
            select(TechnicianHours)
            .where(
                TechnicianHours.technician_name == name,
                TechnicianHours.period_start >= start,
                TechnicianHours.period_end <= end,
                TechnicianHours.deleted_at.is_(None),
            )
            .order_by(TechnicianHours.period_start)
        )
        return list(result.scalars().all())

    async def upsert_period(
        self,
        db: AsyncSession,
        rows: list[dict],
        period_start: date,
        period_end: date,
    ) -> None:
        await db.execute(
            delete(TechnicianHours).where(
                TechnicianHours.period_start == period_start,
                TechnicianHours.period_end == period_end,
            )
        )
        await db.execute(insert(TechnicianHours), rows)
        await db.commit()
