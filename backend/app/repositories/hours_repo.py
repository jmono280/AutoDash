from __future__ import annotations

from datetime import date

from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hours_summary import HoursSummary


class HoursSummaryRepository:
    async def get_range(
        self, db: AsyncSession, start: date, end: date
    ) -> list[HoursSummary]:
        result = await db.execute(
            select(HoursSummary)
            .where(
                HoursSummary.period_start >= start,
                HoursSummary.period_end <= end,
                HoursSummary.deleted_at.is_(None),
            )
            .order_by(HoursSummary.period_start)
        )
        return list(result.scalars().all())

    async def get_latest(self, db: AsyncSession) -> HoursSummary | None:
        result = await db.execute(
            select(HoursSummary)
            .where(HoursSummary.deleted_at.is_(None))
            .order_by(HoursSummary.period_end.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def get_kpis(self, db: AsyncSession, start: date, end: date) -> dict:
        result = await db.execute(
            select(
                func.sum(HoursSummary.labor_dollars).label("labor_dollars"),
                func.sum(HoursSummary.hours_sold).label("hours_sold"),
                func.sum(HoursSummary.hours_paid).label("hours_paid"),
                func.sum(HoursSummary.hours_worked).label("hours_worked"),
                func.sum(HoursSummary.actual_hours).label("actual_hours"),
                func.avg(HoursSummary.advisor_efficiency).label("advisor_efficiency"),
                func.avg(HoursSummary.technician_proficiency).label("technician_proficiency"),
                func.avg(HoursSummary.technician_productivity).label("technician_productivity"),
                func.avg(HoursSummary.technician_efficiency).label("technician_efficiency"),
                func.max(HoursSummary.imported_at).label("imported_at"),
            ).where(
                HoursSummary.period_start >= start,
                HoursSummary.period_end <= end,
                HoursSummary.deleted_at.is_(None),
            )
        )
        row = result.one()
        return row._asdict()

    async def upsert_period(
        self,
        db: AsyncSession,
        rows: list[dict],
        period_start: date,
        period_end: date,
    ) -> None:
        await db.execute(
            delete(HoursSummary).where(
                HoursSummary.period_start == period_start,
                HoursSummary.period_end == period_end,
            )
        )
        await db.execute(insert(HoursSummary), rows)
        await db.commit()
