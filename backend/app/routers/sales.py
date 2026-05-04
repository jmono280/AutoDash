from __future__ import annotations

import calendar
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.daily_sales import DailySalesOut, DayOfWeekStats, SalesKpisOut, TrendPoint
from app.services.sales_service import SalesService

router = APIRouter()


def _service() -> SalesService:
    return SalesService()


def _month_start() -> date:
    today = date.today()
    return today.replace(day=1)


def _month_end() -> date:
    today = date.today()
    return today.replace(day=calendar.monthrange(today.year, today.month)[1])


@router.get("/", response_model=list[DailySalesOut])
async def list_range(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: AsyncSession = Depends(get_db),
    service: SalesService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[DailySalesOut]:
    return await service.list_range(db, from_date or _month_start(), to_date or _month_end())


@router.get("/kpis", response_model=SalesKpisOut)
async def get_kpis(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: AsyncSession = Depends(get_db),
    service: SalesService = Depends(_service),
    _: User = Depends(get_current_user),
) -> SalesKpisOut:
    return await service.get_kpis(db, from_date or _month_start(), to_date or _month_end())


@router.get("/trend", response_model=list[TrendPoint])
async def get_trend(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: AsyncSession = Depends(get_db),
    service: SalesService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[TrendPoint]:
    return await service.get_trend(db, from_date or _month_start(), to_date or _month_end())


@router.get("/by-day-of-week", response_model=list[DayOfWeekStats])
async def get_by_day_of_week(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: AsyncSession = Depends(get_db),
    service: SalesService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[DayOfWeekStats]:
    return await service.get_by_day_of_week(
        db, from_date or _month_start(), to_date or _month_end()
    )
