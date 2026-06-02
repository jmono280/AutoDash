from __future__ import annotations

import math
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.payment_repo import PaymentRepository
from app.schemas.payment_report import (
    CollectionStatOut,
    PaymentByCollectorOut,
    PaymentByMethodOut,
    PaymentKpisOut,
    PaymentTransactionOut,
)
from app.schemas.work_in_progress import Page


class PaymentService:
    def __init__(self, repo: PaymentRepository | None = None):
        self.repo = repo or PaymentRepository()

    async def list_transactions(
        self,
        db: AsyncSession,
        *,
        from_date: date,
        to_date: date,
        collector: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> Page[PaymentTransactionOut]:
        total = await self.repo.count_transactions(
            db, from_date=from_date, to_date=to_date, collector=collector
        )
        items = await self.repo.list_transactions(
            db, from_date=from_date, to_date=to_date, collector=collector,
            page=page, limit=limit,
        )
        pages = math.ceil(total / limit) if total > 0 else 1
        return Page(
            items=[PaymentTransactionOut.model_validate(r) for r in items],
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )

    async def get_kpis(self, db: AsyncSession, *, from_date: date, to_date: date) -> PaymentKpisOut:
        data = await self.repo.get_kpis(db, from_date=from_date, to_date=to_date)
        return PaymentKpisOut(**data)

    async def get_by_collector(
        self, db: AsyncSession, *, from_date: date, to_date: date
    ) -> list[PaymentByCollectorOut]:
        rows = await self.repo.get_by_collector(db, from_date=from_date, to_date=to_date)
        return [PaymentByCollectorOut(**r) for r in rows]

    async def get_by_method(
        self, db: AsyncSession, *, from_date: date, to_date: date
    ) -> list[PaymentByMethodOut]:
        rows = await self.repo.get_by_method(db, from_date=from_date, to_date=to_date)
        return [PaymentByMethodOut(**r) for r in rows]

    async def list_collection_stats(
        self, db: AsyncSession, *, from_date: date, to_date: date
    ) -> list[CollectionStatOut]:
        rows = await self.repo.list_collection_stats(db, from_date=from_date, to_date=to_date)
        return [CollectionStatOut.model_validate(r) for r in rows]
