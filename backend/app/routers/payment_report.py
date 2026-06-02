from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.payment_report import (
    CollectionStatOut,
    PaymentByCollectorOut,
    PaymentByMethodOut,
    PaymentKpisOut,
    PaymentTransactionOut,
)
from app.schemas.work_in_progress import Page
from app.services.payment_service import PaymentService

router = APIRouter()


def _service() -> PaymentService:
    return PaymentService()


@router.get("/transactions", response_model=Page[PaymentTransactionOut])
async def list_transactions(
    from_date: date = Query(..., alias="from"),
    to_date:   date = Query(..., alias="to"),
    collector: str | None = Query(default=None),
    page:      int = Query(default=1, ge=1),
    limit:     int = Query(default=20, ge=1, le=200),
    db:        AsyncSession = Depends(get_db),
    service:   PaymentService = Depends(_service),
    _:         User = Depends(get_current_user),
) -> Page[PaymentTransactionOut]:
    return await service.list_transactions(
        db, from_date=from_date, to_date=to_date,
        collector=collector, page=page, limit=limit,
    )


@router.get("/transactions/kpis", response_model=PaymentKpisOut)
async def get_kpis(
    from_date: date = Query(..., alias="from"),
    to_date:   date = Query(..., alias="to"),
    db:        AsyncSession = Depends(get_db),
    service:   PaymentService = Depends(_service),
    _:         User = Depends(get_current_user),
) -> PaymentKpisOut:
    return await service.get_kpis(db, from_date=from_date, to_date=to_date)


@router.get("/transactions/by-collector", response_model=list[PaymentByCollectorOut])
async def get_by_collector(
    from_date: date = Query(..., alias="from"),
    to_date:   date = Query(..., alias="to"),
    db:        AsyncSession = Depends(get_db),
    service:   PaymentService = Depends(_service),
    _:         User = Depends(get_current_user),
) -> list[PaymentByCollectorOut]:
    return await service.get_by_collector(db, from_date=from_date, to_date=to_date)


@router.get("/transactions/by-method", response_model=list[PaymentByMethodOut])
async def get_by_method(
    from_date: date = Query(..., alias="from"),
    to_date:   date = Query(..., alias="to"),
    db:        AsyncSession = Depends(get_db),
    service:   PaymentService = Depends(_service),
    _:         User = Depends(get_current_user),
) -> list[PaymentByMethodOut]:
    return await service.get_by_method(db, from_date=from_date, to_date=to_date)


@router.get("/collection-stats", response_model=list[CollectionStatOut])
async def list_collection_stats(
    from_date: date = Query(..., alias="from"),
    to_date:   date = Query(..., alias="to"),
    db:        AsyncSession = Depends(get_db),
    service:   PaymentService = Depends(_service),
    _:         User = Depends(get_current_user),
) -> list[CollectionStatOut]:
    return await service.list_collection_stats(db, from_date=from_date, to_date=to_date)
