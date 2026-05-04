from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_sales import DailySales


class DailySalesRepository:
    async def get_range(
        self, db: AsyncSession, start: date, end: date
    ) -> list[DailySales]:
        result = await db.execute(
            select(DailySales)
            .where(DailySales.date.between(start, end), DailySales.deleted_at.is_(None))
            .order_by(DailySales.date)
        )
        return list(result.scalars().all())

    async def get_kpis(self, db: AsyncSession, start: date, end: date) -> dict:
        result = await db.execute(
            select(
                func.sum(DailySales.total_cars).label("total_cars"),
                func.sum(DailySales.gross_sales).label("total_gross"),
                func.sum(DailySales.net_sales).label("total_net"),
                func.avg(DailySales.ticket_average).label("avg_ticket"),
                func.sum(DailySales.cost_of_goods).label("total_cogs"),
                func.sum(DailySales.gross_profit).label("total_profit"),
                func.max(DailySales.imported_at).label("imported_at"),
            ).where(
                DailySales.date.between(start, end),
                DailySales.deleted_at.is_(None),
            )
        )
        row = result.one()
        total_gross = row.total_gross or Decimal("0")
        total_cogs = row.total_cogs or Decimal("0")
        total_profit = row.total_profit or Decimal("0")
        profit_pct = (total_profit / total_gross * 100) if total_gross else Decimal("0")
        cogs_pct = (total_cogs / total_gross * 100) if total_gross else Decimal("0")
        return {
            "total_cars": row.total_cars or 0,
            "total_gross": total_gross,
            "total_net": row.total_net or Decimal("0"),
            "avg_ticket": row.avg_ticket or Decimal("0"),
            "total_cogs": total_cogs,
            "total_profit": total_profit,
            "profit_pct": profit_pct,
            "cogs_pct": cogs_pct,
            "imported_at": row.imported_at,
        }

    async def get_trend(self, db: AsyncSession, start: date, end: date) -> list[dict]:
        result = await db.execute(
            select(
                DailySales.date,
                DailySales.gross_sales,
                DailySales.net_sales,
                DailySales.gross_profit.label("profit"),
            )
            .where(DailySales.date.between(start, end), DailySales.deleted_at.is_(None))
            .order_by(DailySales.date)
        )
        return [row._asdict() for row in result.all()]

    async def get_by_day_of_week(
        self, db: AsyncSession, start: date, end: date
    ) -> list[dict]:
        result = await db.execute(
            select(
                DailySales.day_of_week,
                func.avg(DailySales.total_cars).label("avg_cars"),
                func.avg(DailySales.gross_sales).label("avg_gross"),
                func.count(DailySales.id).label("count_days"),
            )
            .where(DailySales.date.between(start, end), DailySales.deleted_at.is_(None))
            .group_by(DailySales.day_of_week)
            .order_by(DailySales.day_of_week)
        )
        return [row._asdict() for row in result.all()]

    async def upsert_period(
        self,
        db: AsyncSession,
        rows: list[dict],
        period_start: date,
        period_end: date,
    ) -> None:
        await db.execute(
            delete(DailySales).where(DailySales.date.between(period_start, period_end))
        )
        await db.execute(insert(DailySales), rows)
        await db.commit()
