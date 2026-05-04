from __future__ import annotations

from decimal import Decimal

from sqlalchemy import case, delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.work_in_progress import WorkInProgress


class WipRepository:
    async def list(
        self,
        db: AsyncSession,
        *,
        advisor: str | None = None,
        category: str | None = None,
        min_days: int | None = None,
        max_days: int | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> list[WorkInProgress]:
        q = select(WorkInProgress).where(WorkInProgress.deleted_at.is_(None))
        if advisor is not None:
            q = q.where(WorkInProgress.advisor == advisor)
        if category is not None:
            q = q.where(WorkInProgress.category == category)
        if min_days is not None:
            q = q.where(WorkInProgress.days_open >= min_days)
        if max_days is not None:
            q = q.where(WorkInProgress.days_open <= max_days)
        q = q.order_by(WorkInProgress.days_open.desc()).offset((page - 1) * limit).limit(limit)
        result = await db.execute(q)
        return list(result.scalars().all())

    async def count(
        self,
        db: AsyncSession,
        *,
        advisor: str | None = None,
        category: str | None = None,
        min_days: int | None = None,
        max_days: int | None = None,
    ) -> int:
        q = select(func.count(WorkInProgress.id)).where(WorkInProgress.deleted_at.is_(None))
        if advisor is not None:
            q = q.where(WorkInProgress.advisor == advisor)
        if category is not None:
            q = q.where(WorkInProgress.category == category)
        if min_days is not None:
            q = q.where(WorkInProgress.days_open >= min_days)
        if max_days is not None:
            q = q.where(WorkInProgress.days_open <= max_days)
        result = await db.execute(q)
        return result.scalar_one()

    async def get_kpis(self, db: AsyncSession) -> dict:
        result = await db.execute(
            select(
                func.count(WorkInProgress.id).label("total_ros"),
                func.coalesce(func.sum(WorkInProgress.estimated), 0).label("total_estimated"),
                func.sum(WorkInProgress.cog).label("total_cog"),
                func.sum(WorkInProgress.col).label("total_col"),
                func.avg(WorkInProgress.days_open).label("avg_days_open"),
                func.max(WorkInProgress.days_open).label("oldest_ro_days"),
                func.max(WorkInProgress.imported_at).label("imported_at"),
            ).where(WorkInProgress.deleted_at.is_(None))
        )
        row = result.one()
        return {
            "total_ros": row.total_ros or 0,
            "total_estimated": row.total_estimated or Decimal("0"),
            "total_cog": row.total_cog or Decimal("0"),
            "total_col": row.total_col or Decimal("0"),
            "avg_days_open": row.avg_days_open or Decimal("0"),
            "oldest_ro_days": row.oldest_ro_days or 0,
            "imported_at": row.imported_at,
        }

    async def get_aging(self, db: AsyncSession) -> list[dict]:
        bucket_col = case(
            (WorkInProgress.days_open <= 7, "0-7d"),
            (WorkInProgress.days_open <= 14, "8-14d"),
            (WorkInProgress.days_open <= 30, "15-30d"),
            (WorkInProgress.days_open <= 60, "31-60d"),
            else_="60+d",
        ).label("bucket")
        # Order by the minimum days in each bucket to preserve 0-7 → 8-14 → 15-30 → 31-60 → 60+ sequence
        result = await db.execute(
            select(
                bucket_col,
                func.count(WorkInProgress.id).label("count"),
                func.coalesce(func.sum(WorkInProgress.estimated), 0).label("total_estimated"),
            )
            .where(WorkInProgress.deleted_at.is_(None))
            .group_by(bucket_col)
            .order_by(func.min(WorkInProgress.days_open))
        )
        return [row._asdict() for row in result.all()]

    async def get_by_category(self, db: AsyncSession) -> list[dict]:
        result = await db.execute(
            select(
                WorkInProgress.category,
                func.count(WorkInProgress.id).label("count"),
                func.sum(WorkInProgress.cog).label("total_cog"),
                func.coalesce(func.sum(WorkInProgress.estimated), 0).label("total_estimated"),
            )
            .where(WorkInProgress.deleted_at.is_(None))
            .group_by(WorkInProgress.category)
            .order_by(func.count(WorkInProgress.id).desc())
        )
        return [row._asdict() for row in result.all()]

    async def get_by_advisor(self, db: AsyncSession) -> list[dict]:
        result = await db.execute(
            select(
                WorkInProgress.advisor,
                func.count(WorkInProgress.id).label("count"),
                func.coalesce(func.sum(WorkInProgress.estimated), 0).label("total_estimated"),
                func.avg(WorkInProgress.days_open).label("avg_days_open"),
            )
            .where(WorkInProgress.deleted_at.is_(None))
            .group_by(WorkInProgress.advisor)
            .order_by(func.count(WorkInProgress.id).desc())
        )
        return [row._asdict() for row in result.all()]

    async def replace_all(self, db: AsyncSession, rows: list[dict]) -> None:
        await db.execute(delete(WorkInProgress))
        await db.execute(insert(WorkInProgress), rows)
        await db.commit()
