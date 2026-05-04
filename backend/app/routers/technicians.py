from __future__ import annotations

import calendar
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.technician import TechnicianOut, TechnicianRankingItem
from app.services.technician_service import TechnicianService

router = APIRouter()

# "labor" is accepted as a short alias for "labor_dollars"
_METRIC_ALIAS: dict[str, str] = {"labor": "labor_dollars"}


def _service() -> TechnicianService:
    return TechnicianService()


def _month_start() -> date:
    today = date.today()
    return today.replace(day=1)


def _month_end() -> date:
    today = date.today()
    return today.replace(day=calendar.monthrange(today.year, today.month)[1])


@router.get("/", response_model=list[TechnicianOut])
async def list_all(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: AsyncSession = Depends(get_db),
    service: TechnicianService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[TechnicianOut]:
    return await service.list_all(db, from_date or _month_start(), to_date or _month_end())


@router.get("/ranking", response_model=list[TechnicianRankingItem])
async def get_ranking(
    metric: str = Query(default="labor_dollars"),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: AsyncSession = Depends(get_db),
    service: TechnicianService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[TechnicianRankingItem]:
    normalized = _METRIC_ALIAS.get(metric, metric)
    return await service.get_ranking(
        db, from_date or _month_start(), to_date or _month_end(), normalized
    )


@router.get("/{name}", response_model=list[TechnicianOut])
async def get_detail(
    name: str,
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: AsyncSession = Depends(get_db),
    service: TechnicianService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[TechnicianOut]:
    return await service.get_detail(
        db, name, from_date or _month_start(), to_date or _month_end()
    )
