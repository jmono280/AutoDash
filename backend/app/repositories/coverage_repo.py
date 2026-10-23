from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call_analytics import CallAnalytics
from app.models.daily_sales import DailySales
from app.models.hours_summary import HoursSummary
from app.models.payment_transaction import PaymentTransaction
from app.models.technician_hours import TechnicianHours
from app.models.work_in_progress import WorkInProgress


class CoverageRepository:
    """Date ranges available per data source, so callers know which periods have data."""

    async def get_coverage(self, db: AsyncSession) -> list[dict[str, Any]]:
        sources = [
            ("daily_sales", DailySales, DailySales.date, DailySales.date),
            ("hours_summary", HoursSummary, HoursSummary.period_start, HoursSummary.period_end),
            ("technician_hours", TechnicianHours, TechnicianHours.period_start, TechnicianHours.period_end),
            ("payments", PaymentTransaction, PaymentTransaction.period_start, PaymentTransaction.period_end),
            ("call_analytics", CallAnalytics, func.date(CallAnalytics.time_from), func.date(CallAnalytics.time_to)),
        ]
        out: list[dict[str, Any]] = []
        for name, model, start_col, end_col in sources:
            row = (
                await db.execute(
                    select(func.min(start_col), func.max(end_col), func.count())
                    .select_from(model)
                    .where(model.deleted_at.is_(None))
                )
            ).one()
            out.append({"source": name, "from_date": row[0], "to_date": row[1], "rows": row[2]})

        wip_rows = (
            await db.execute(
                select(func.count())
                .select_from(WorkInProgress)
                .where(WorkInProgress.deleted_at.is_(None))
            )
        ).scalar_one()
        out.append({"source": "work_in_progress", "from_date": None, "to_date": None, "rows": wip_rows})
        return out
