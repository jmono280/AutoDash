from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_admin, get_current_user
from app.database import get_db
from app.models.user import User
from app.repositories.call_analytics_repo import CallAnalyticsRepository
from app.schemas.call_analytics import (
    CallAnalyticsByExtensionOut,
    CallAnalyticsKpisOut,
    CallAnalyticsOut,
    FetchRequest,
    FetchResultOut,
)
from app.services.call_analytics_service import CallAnalyticsService
from app.services.rc_service import fetch_analytics

router = APIRouter()


def _service() -> CallAnalyticsService:
    return CallAnalyticsService()


def _default_from() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _default_to() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(hour=23, minute=59, second=59, microsecond=0)


@router.get("/", response_model=list[CallAnalyticsOut])
async def list_calls(
    date_from: datetime | None        = Query(default=None, alias="from"),
    date_to:   datetime | None        = Query(default=None, alias="to"),
    extension: str | None             = Query(default=None),
    db:        AsyncSession           = Depends(get_db),
    service:   CallAnalyticsService   = Depends(_service),
    _:         User                   = Depends(get_current_user),
) -> list[CallAnalyticsOut]:
    return await service.list_range(
        db,
        date_from or _default_from(),
        date_to   or _default_to(),
        extension,
    )


@router.get("/kpis", response_model=CallAnalyticsKpisOut)
async def get_kpis(
    date_from: datetime | None        = Query(default=None, alias="from"),
    date_to:   datetime | None        = Query(default=None, alias="to"),
    db:        AsyncSession           = Depends(get_db),
    service:   CallAnalyticsService   = Depends(_service),
    _:         User                   = Depends(get_current_user),
) -> CallAnalyticsKpisOut:
    return await service.get_kpis(
        db,
        date_from or _default_from(),
        date_to   or _default_to(),
    )


@router.get("/by-extension", response_model=list[CallAnalyticsByExtensionOut])
async def get_by_extension(
    date_from: datetime | None        = Query(default=None, alias="from"),
    date_to:   datetime | None        = Query(default=None, alias="to"),
    db:        AsyncSession           = Depends(get_db),
    service:   CallAnalyticsService   = Depends(_service),
    _:         User                   = Depends(get_current_user),
) -> list[CallAnalyticsByExtensionOut]:
    return await service.get_by_extension(
        db,
        date_from or _default_from(),
        date_to   or _default_to(),
    )


@router.post("/fetch", response_model=FetchResultOut, status_code=201)
async def fetch_from_ringcentral(
    body: FetchRequest,
    db:   AsyncSession = Depends(get_db),
    _:    User         = Depends(get_current_admin),
) -> FetchResultOut:
    time_from_iso = body.time_from.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    time_to_iso   = body.time_to.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    loop = asyncio.get_event_loop()
    try:
        rows = await loop.run_in_executor(
            None, lambda: fetch_analytics(time_from_iso, time_to_iso)
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    repo = CallAnalyticsRepository()
    await repo.upsert_run(db, rows, body.time_from, body.time_to)
    return FetchResultOut(rows_saved=len(rows), time_from=body.time_from, time_to=body.time_to)
