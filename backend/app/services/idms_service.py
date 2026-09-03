from __future__ import annotations

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.importers.idms_client import IdmsClient, MfaRequired
from app.importers.idms_parsers import (
    IDMS_CHARGE_OFF_REPORT_ID,
    IDMS_MONTH_END_REPORT_ID,
    IDMS_SALES_REPORT_ID,
    parse_aa_month_end,
    parse_aa_sales_manual,
    parse_report,
)
from app.repositories.idms_repo import IdmsRepository
from app.schemas.idms import IdmsSyncOut


class IdmsService:
    def __init__(self, repo: IdmsRepository | None = None):
        self.repo = repo or IdmsRepository()

    # ------------------------------------------------------------------
    # Session / login
    # ------------------------------------------------------------------
    def check_session(self) -> dict:
        client = IdmsClient()
        if client.load_session() and client.is_authenticated():
            return {"authenticated": True, "message": "Sesión activa"}
        return {"authenticated": False, "message": "Sin sesión activa"}

    def login(self, otp_code: str | None = None) -> dict:
        client = IdmsClient()
        try:
            client.login(otp_code=otp_code)
        except MfaRequired as exc:
            return {"authenticated": False, "mfa_required": True, "message": exc.message}
        return {"authenticated": True, "message": "Sesión iniciada"}

    # ------------------------------------------------------------------
    # Charge Offs
    # ------------------------------------------------------------------
    async def sync_charge_offs(
        self, db: AsyncSession, year: int
    ) -> IdmsSyncOut:
        client = IdmsClient()
        client.login()
        raw = client.export_csv(IDMS_CHARGE_OFF_REPORT_ID, export_type="csv")
        rows = parse_report(IDMS_CHARGE_OFF_REPORT_ID, raw)
        # Se sincronizan solo los años presentes en el reporte descargado,
        # preservando los históricos cargados desde Excel.
        inserted = await self.repo.sync_charge_off_years(db, rows)
        return IdmsSyncOut(
            report_id=IDMS_CHARGE_OFF_REPORT_ID,
            year=year,
            rows_inserted=inserted,
            message=f"{inserted} charge offs sincronizados",
        )

    async def import_charge_off_historical(
        self, db: AsyncSession, file_bytes: bytes
    ) -> IdmsSyncOut:
        from app.importers.idms_chargeoff_excel import parse_chargeoff_historical_excel

        rows = parse_chargeoff_historical_excel(file_bytes)
        inserted = await self.repo.sync_all_charge_offs(db, rows)
        return IdmsSyncOut(
            report_id="manual-pull",
            year=0,
            rows_inserted=inserted,
            message=f"{inserted} charge offs históricos importados",
        )

    async def get_charge_offs(self, db: AsyncSession, year: int):
        return await self.repo.list_charge_offs(db, report_year=year)

    async def get_charge_off_kpis(self, db: AsyncSession, year: int):
        return await self.repo.get_charge_off_kpis(db, report_year=year)

    async def get_charge_off_monthly(self, db: AsyncSession, year: int):
        return await self.repo.get_charge_off_monthly(db, report_year=year)

    async def get_available_years(self, db: AsyncSession) -> list[int]:
        return await self.repo.get_available_years(db)

    async def get_charge_off_overview(self, db: AsyncSession, year: int):
        return await self.repo.get_charge_off_overview(db, year)

    async def get_charge_off_monthly_detail(self, db: AsyncSession, year: int):
        return await self.repo.get_charge_off_monthly_detail(db, year)

    # ------------------------------------------------------------------
    # Month End (snapshot de cartera)
    # ------------------------------------------------------------------
    async def sync_month_end(self, db: AsyncSession) -> IdmsSyncOut:
        """Toma la foto de la cartera de hoy y la guarda como el mes corriente."""
        snapshot = date.today()
        client = IdmsClient()
        client.login()
        raw = client.export_csv(IDMS_MONTH_END_REPORT_ID, export_type="csv")
        rows = parse_aa_month_end(raw, snapshot)
        inserted = await self.repo.sync_month_end(
            db, rows, year=snapshot.year, month=snapshot.month
        )
        return IdmsSyncOut(
            report_id=IDMS_MONTH_END_REPORT_ID,
            year=snapshot.year,
            rows_inserted=inserted,
            message=(
                f"{inserted} cuentas en el snapshot de "
                f"{snapshot.strftime('%m/%Y')}"
            ),
        )

    # ------------------------------------------------------------------
    # Sales
    # ------------------------------------------------------------------
    async def sync_sales(
        self, db: AsyncSession, year: int
    ) -> IdmsSyncOut:
        client = IdmsClient()
        client.login()
        raw = client.export_csv(IDMS_SALES_REPORT_ID, export_type="csv")
        rows = parse_report(IDMS_SALES_REPORT_ID, raw)
        inserted = await self.repo.sync_sales(db, rows)
        return IdmsSyncOut(
            report_id=IDMS_SALES_REPORT_ID,
            year=year,
            rows_inserted=inserted,
            message=f"{inserted} ventas sincronizadas",
        )

    async def import_sales_historical(
        self, db: AsyncSession, file_bytes: bytes
    ) -> IdmsSyncOut:
        rows = parse_aa_sales_manual(file_bytes)
        inserted = await self.repo.sync_all_sales(db, rows)
        return IdmsSyncOut(
            report_id="manual-pull",
            year=0,
            rows_inserted=inserted,
            message=f"{inserted} ventas históricas importadas",
        )

    async def get_sales(self, db: AsyncSession, year: int):
        return await self.repo.list_sales(db, report_year=year)

    async def get_sales_kpis(self, db: AsyncSession, year: int):
        return await self.repo.get_sales_kpis(db, report_year=year)

    async def get_sales_monthly(self, db: AsyncSession, year: int):
        return await self.repo.get_sales_monthly(db, report_year=year)

    async def get_sales_years(self, db: AsyncSession) -> list[int]:
        return await self.repo.get_sales_years(db)

    async def get_sales_by_salesperson(self, db: AsyncSession, year: int):
        return await self.repo.get_sales_by_salesperson(db, report_year=year)

    async def get_sales_by_vehicle(self, db: AsyncSession, year: int):
        return await self.repo.get_sales_by_vehicle(db, report_year=year)
