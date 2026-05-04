from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.hours_repo import HoursSummaryRepository
from app.schemas.hours import HoursKpisOut, HoursSummaryOut


class HoursService:
    def __init__(self, repo: HoursSummaryRepository | None = None):
        self.repo = repo or HoursSummaryRepository()

    async def get_kpis(self, db: AsyncSession, start: date, end: date) -> HoursKpisOut:
        data = await self.repo.get_kpis(db, start, end)
        return HoursKpisOut(
            labor_dollars=data["labor_dollars"] or Decimal("0"),
            hours_sold=data["hours_sold"] or Decimal("0"),
            hours_paid=data["hours_paid"] or Decimal("0"),
            hours_worked=data["hours_worked"] or Decimal("0"),
            actual_hours=data["actual_hours"] or Decimal("0"),
            advisor_efficiency=data["advisor_efficiency"] or Decimal("0"),
            technician_proficiency=data["technician_proficiency"] or Decimal("0"),
            technician_productivity=data["technician_productivity"] or Decimal("0"),
            technician_efficiency=data["technician_efficiency"],
            imported_at=data.get("imported_at"),
        )

    async def list_range(
        self, db: AsyncSession, start: date, end: date
    ) -> list[HoursSummaryOut]:
        rows = await self.repo.get_range(db, start, end)
        return [HoursSummaryOut.model_validate(r) for r in rows]
