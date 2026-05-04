from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.technician_repo import TechnicianRepository
from app.schemas.technician import TechnicianOut, TechnicianRankingItem

_VALID_METRICS = {"labor_dollars", "hours_sold", "proficiency"}


class TechnicianService:
    def __init__(self, repo: TechnicianRepository | None = None):
        self.repo = repo or TechnicianRepository()

    async def list_all(
        self, db: AsyncSession, start: date, end: date
    ) -> list[TechnicianOut]:
        rows = await self.repo.get_range(db, start, end)
        return [TechnicianOut.model_validate(r) for r in rows]

    async def get_ranking(
        self,
        db: AsyncSession,
        start: date,
        end: date,
        metric: str = "labor_dollars",
    ) -> list[TechnicianRankingItem]:
        if metric not in _VALID_METRICS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"metric must be one of {sorted(_VALID_METRICS)}",
            )
        rows = await self.repo.get_ranking(db, start, end, metric)
        return [TechnicianRankingItem.model_validate(r) for r in rows]

    async def get_detail(
        self, db: AsyncSession, name: str, start: date, end: date
    ) -> list[TechnicianOut]:
        rows = await self.repo.get_by_name(db, name, start, end)
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Technician '{name}' not found in the given period",
            )
        return [TechnicianOut.model_validate(r) for r in rows]
