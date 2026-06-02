from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection_stat import CollectionStat
from app.models.payment_transaction import PaymentTransaction


class PaymentRepository:
    async def list_transactions(
        self,
        db: AsyncSession,
        *,
        from_date: date,
        to_date: date,
        collector: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> list[PaymentTransaction]:
        q = (
            select(PaymentTransaction)
            .where(
                PaymentTransaction.deleted_at.is_(None),
                PaymentTransaction.period_start >= from_date,
                PaymentTransaction.period_end <= to_date,
            )
            .order_by(PaymentTransaction.payment_date.desc())
        )
        if collector:
            q = q.where(PaymentTransaction.collector == collector)
        q = q.offset((page - 1) * limit).limit(limit)
        result = await db.execute(q)
        return list(result.scalars().all())

    async def count_transactions(
        self,
        db: AsyncSession,
        *,
        from_date: date,
        to_date: date,
        collector: str | None = None,
    ) -> int:
        q = select(func.count(PaymentTransaction.id)).where(
            PaymentTransaction.deleted_at.is_(None),
            PaymentTransaction.period_start >= from_date,
            PaymentTransaction.period_end <= to_date,
        )
        if collector:
            q = q.where(PaymentTransaction.collector == collector)
        result = await db.execute(q)
        return result.scalar_one()

    async def get_kpis(self, db: AsyncSession, *, from_date: date, to_date: date) -> dict:
        result = await db.execute(
            select(
                func.count(PaymentTransaction.id).label("total_payments"),
                func.coalesce(func.sum(PaymentTransaction.amount), 0).label("total_amount"),
                func.coalesce(func.sum(PaymentTransaction.convenience_fee), 0).label("total_fees"),
                func.coalesce(func.sum(PaymentTransaction.amount + PaymentTransaction.convenience_fee), 0).label("total_collected"),
                func.coalesce(func.sum(PaymentTransaction.refund_amount), 0).label("total_refunds"),
                func.coalesce(func.avg(PaymentTransaction.amount), 0).label("avg_payment_amount"),
            ).where(
                PaymentTransaction.deleted_at.is_(None),
                PaymentTransaction.period_start >= from_date,
                PaymentTransaction.period_end <= to_date,
            )
        )
        row = result.one()
        return {
            "total_payments":     row.total_payments or 0,
            "total_amount":       row.total_amount or Decimal("0"),
            "total_fees":         row.total_fees or Decimal("0"),
            "total_collected":    row.total_collected or Decimal("0"),
            "total_refunds":      row.total_refunds or Decimal("0"),
            "avg_payment_amount": row.avg_payment_amount or Decimal("0"),
        }

    async def get_by_collector(
        self, db: AsyncSession, *, from_date: date, to_date: date
    ) -> list[dict]:
        result = await db.execute(
            select(
                PaymentTransaction.collector,
                func.count(PaymentTransaction.id).label("count"),
                func.coalesce(func.sum(PaymentTransaction.amount), 0).label("total_amount"),
            )
            .where(
                PaymentTransaction.deleted_at.is_(None),
                PaymentTransaction.period_start >= from_date,
                PaymentTransaction.period_end <= to_date,
                PaymentTransaction.collector.isnot(None),
            )
            .group_by(PaymentTransaction.collector)
            .order_by(func.sum(PaymentTransaction.amount).desc())
        )
        return [row._asdict() for row in result.all()]

    async def get_by_method(
        self, db: AsyncSession, *, from_date: date, to_date: date
    ) -> list[dict]:
        result = await db.execute(
            select(
                PaymentTransaction.payment_method,
                func.count(PaymentTransaction.id).label("count"),
                func.coalesce(func.sum(PaymentTransaction.amount), 0).label("total_amount"),
            )
            .where(
                PaymentTransaction.deleted_at.is_(None),
                PaymentTransaction.period_start >= from_date,
                PaymentTransaction.period_end <= to_date,
                PaymentTransaction.payment_method.isnot(None),
            )
            .group_by(PaymentTransaction.payment_method)
            .order_by(func.count(PaymentTransaction.id).desc())
        )
        return [row._asdict() for row in result.all()]

    async def list_collection_stats(
        self, db: AsyncSession, *, from_date: date, to_date: date
    ) -> list[CollectionStat]:
        result = await db.execute(
            select(CollectionStat)
            .where(
                CollectionStat.deleted_at.is_(None),
                CollectionStat.period_start >= from_date,
                CollectionStat.period_end <= to_date,
            )
            .order_by(CollectionStat.payments_amount.desc())
        )
        return list(result.scalars().all())

    async def upsert_period(
        self,
        db: AsyncSession,
        transactions: list[dict],
        stats: list[dict],
        period_start: date,
        period_end: date,
    ) -> None:
        await db.execute(
            delete(PaymentTransaction).where(
                PaymentTransaction.period_start == period_start,
                PaymentTransaction.period_end == period_end,
            )
        )
        await db.execute(
            delete(CollectionStat).where(
                CollectionStat.period_start == period_start,
                CollectionStat.period_end == period_end,
            )
        )
        if transactions:
            await db.execute(insert(PaymentTransaction), transactions)
        if stats:
            await db.execute(insert(CollectionStat), stats)
        await db.commit()
