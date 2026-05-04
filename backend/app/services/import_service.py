from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.importers.daily_sales_pdf import parse_daily_sales
from app.importers.hours_detail_pdf import parse_hours_detail
from app.importers.hours_summary_pdf import parse_hours_summary
from app.importers.wip_excel import parse_wip_excel
from app.repositories.daily_sales_repo import DailySalesRepository
from app.repositories.hours_repo import HoursSummaryRepository
from app.repositories.technician_repo import TechnicianRepository
from app.repositories.wip_repo import WipRepository
from app.schemas.imports import ImportResultOut


class ImportService:
    def __init__(
        self,
        sales_repo: DailySalesRepository | None = None,
        hours_repo: HoursSummaryRepository | None = None,
        tech_repo: TechnicianRepository | None = None,
        wip_repo: WipRepository | None = None,
    ):
        self.sales_repo = sales_repo or DailySalesRepository()
        self.hours_repo = hours_repo or HoursSummaryRepository()
        self.tech_repo = tech_repo or TechnicianRepository()
        self.wip_repo = wip_repo or WipRepository()

    async def import_daily_sales(
        self, db: AsyncSession, file_bytes: bytes
    ) -> ImportResultOut:
        try:
            rows, period_start, period_end = parse_daily_sales(file_bytes)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        await self.sales_repo.upsert_period(db, rows, period_start, period_end)
        return ImportResultOut(
            rows_inserted=len(rows),
            rows_updated=0,
            period_start=period_start,
            period_end=period_end,
            file_type="daily_sales",
            message=f"Imported {len(rows)} daily sales rows for {period_start} – {period_end}",
        )

    async def import_hours_summary(
        self, db: AsyncSession, file_bytes: bytes
    ) -> ImportResultOut:
        try:
            rows, period_start, period_end = parse_hours_summary(file_bytes)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        await self.hours_repo.upsert_period(db, rows, period_start, period_end)
        return ImportResultOut(
            rows_inserted=len(rows),
            rows_updated=0,
            period_start=period_start,
            period_end=period_end,
            file_type="hours_summary",
            message=f"Imported {len(rows)} hours summary rows for {period_start} – {period_end}",
        )

    async def import_hours_detail(
        self, db: AsyncSession, file_bytes: bytes
    ) -> ImportResultOut:
        try:
            rows, period_start, period_end = parse_hours_detail(file_bytes)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        await self.tech_repo.upsert_period(db, rows, period_start, period_end)
        return ImportResultOut(
            rows_inserted=len(rows),
            rows_updated=0,
            period_start=period_start,
            period_end=period_end,
            file_type="hours_detail",
            message=f"Imported {len(rows)} technician rows for {period_start} – {period_end}",
        )

    async def import_wip(
        self, db: AsyncSession, file_bytes: bytes
    ) -> ImportResultOut:
        try:
            rows = parse_wip_excel(file_bytes)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        await self.wip_repo.replace_all(db, rows)
        return ImportResultOut(
            rows_inserted=len(rows),
            rows_updated=0,
            period_start=None,
            period_end=None,
            file_type="work_in_progress",
            message=f"Replaced WIP snapshot with {len(rows)} rows",
        )
