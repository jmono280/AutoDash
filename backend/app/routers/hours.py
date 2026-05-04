from __future__ import annotations

import calendar
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.hours import HoursKpisOut, HoursSummaryOut
from app.services.hours_service import HoursService

router = APIRouter()


def _service() -> HoursService:
    return HoursService()


def _month_start() -> date:
    today = date.today()
    return today.replace(day=1)


def _month_end() -> date:
    today = date.today()
    return today.replace(day=calendar.monthrange(today.year, today.month)[1])


@router.get("/", response_model=list[HoursSummaryOut])
async def list_range(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: AsyncSession = Depends(get_db),
    service: HoursService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[HoursSummaryOut]:
    return await service.list_range(db, from_date or _month_start(), to_date or _month_end())


@router.get("/kpis", response_model=HoursKpisOut)
async def get_kpis(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: AsyncSession = Depends(get_db),
    service: HoursService = Depends(_service),
    _: User = Depends(get_current_user),
) -> HoursKpisOut:
    return await service.get_kpis(db, from_date or _month_start(), to_date or _month_end())
