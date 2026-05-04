from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.work_in_progress import (
    AdvisorGroup,
    AgingBucket,
    CategoryGroup,
    Page,
    WipKpisOut,
    WipOut,
)
from app.services.wip_service import WipFilters, WipService

router = APIRouter()


def _service() -> WipService:
    return WipService()


@router.get("/", response_model=Page[WipOut])
async def list_wip(
    advisor: str | None = Query(default=None),
    category: str | None = Query(default=None),
    min_days: int | None = Query(default=None, ge=0),
    max_days: int | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    service: WipService = Depends(_service),
    _: User = Depends(get_current_user),
) -> Page[WipOut]:
    filters = WipFilters(
        advisor=advisor,
        category=category,
        min_days=min_days,
        max_days=max_days,
    )
    return await service.list(db, filters, page=page, limit=limit)


@router.get("/kpis", response_model=WipKpisOut)
async def get_kpis(
    db: AsyncSession = Depends(get_db),
    service: WipService = Depends(_service),
    _: User = Depends(get_current_user),
) -> WipKpisOut:
    return await service.get_kpis(db)


@router.get("/aging", response_model=list[AgingBucket])
async def get_aging(
    db: AsyncSession = Depends(get_db),
    service: WipService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[AgingBucket]:
    return await service.get_aging(db)


@router.get("/by-category", response_model=list[CategoryGroup])
async def get_by_category(
    db: AsyncSession = Depends(get_db),
    service: WipService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[CategoryGroup]:
    return await service.get_by_category(db)


@router.get("/by-advisor", response_model=list[AdvisorGroup])
async def get_by_advisor(
    db: AsyncSession = Depends(get_db),
    service: WipService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[AdvisorGroup]:
    return await service.get_by_advisor(db)
