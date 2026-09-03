from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idms_charge_off import IdmsChargeOff
from app.models.idms_month_end import IdmsMonthEnd

MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def _ratio(num: Decimal, den: Decimal) -> Decimal:
    """Porcentaje seguro: devuelve 0 si el denominador es 0."""
    if not den:
        return Decimal("0")
    return (Decimal(num) / Decimal(den)) * 100


class IdmsRepository:
    async def sync_charge_offs(
        self, db: AsyncSession, rows: list[dict], report_year: int
    ) -> int:
        await db.execute(
            delete(IdmsChargeOff).where(IdmsChargeOff.report_year == report_year)
        )
        if rows:
            await db.execute(insert(IdmsChargeOff), rows)
        await db.commit()
        return len(rows)

    async def sync_all_charge_offs(
        self, db: AsyncSession, rows: list[dict]
    ) -> int:
        await db.execute(delete(IdmsChargeOff))
        if rows:
            await db.execute(insert(IdmsChargeOff), rows)
        await db.commit()
        return len(rows)

    async def sync_charge_off_years(
        self, db: AsyncSession, rows: list[dict]
    ) -> int:
        """Borra e inserta solo los años presentes en rows, preservando históricos."""
        years = {r["report_year"] for r in rows if r.get("report_year")}
        if years:
            await db.execute(
                delete(IdmsChargeOff).where(IdmsChargeOff.report_year.in_(years))
            )
        if rows:
            await db.execute(insert(IdmsChargeOff), rows)
        await db.commit()
        return len(rows)

    async def list_charge_offs(
        self, db: AsyncSession, report_year: int
    ) -> list[IdmsChargeOff]:
        result = await db.execute(
            select(IdmsChargeOff)
            .where(
                IdmsChargeOff.report_year == report_year,
                IdmsChargeOff.deleted_at.is_(None),
            )
            .order_by(IdmsChargeOff.charge_off_date)
        )
        return list(result.scalars().all())

    async def get_charge_off_kpis(
        self, db: AsyncSession, report_year: int
    ) -> dict:
        result = await db.execute(
            select(
                func.count(IdmsChargeOff.id).label("count"),
                func.coalesce(func.sum(IdmsChargeOff.original_balance), Decimal("0")).label(
                    "total_original_balance"
                ),
                func.coalesce(func.sum(IdmsChargeOff.current_balance), Decimal("0")).label(
                    "total_current_balance"
                ),
                func.coalesce(func.sum(IdmsChargeOff.total_recovery), Decimal("0")).label(
                    "total_recovery"
                ),
                func.coalesce(func.sum(IdmsChargeOff.total_adjusted), Decimal("0")).label(
                    "total_adjusted"
                ),
                func.max(IdmsChargeOff.imported_at).label("imported_at"),
            ).where(
                IdmsChargeOff.report_year == report_year,
                IdmsChargeOff.deleted_at.is_(None),
            )
        )
        row = result.one()
        return {
            "year": report_year,
            "count": row.count or 0,
            "total_original_balance": row.total_original_balance or Decimal("0"),
            "total_current_balance": row.total_current_balance or Decimal("0"),
            "total_recovery": row.total_recovery or Decimal("0"),
            "total_adjusted": row.total_adjusted or Decimal("0"),
            "imported_at": row.imported_at,
        }

    async def get_charge_off_monthly(
        self, db: AsyncSession, report_year: int
    ) -> list[dict]:
        result = await db.execute(
            select(
                func.extract("year", IdmsChargeOff.charge_off_date).label("year"),
                func.extract("month", IdmsChargeOff.charge_off_date).label("month"),
                func.count(IdmsChargeOff.id).label("count"),
                func.coalesce(func.sum(IdmsChargeOff.original_balance), Decimal("0")).label(
                    "original_balance"
                ),
                func.coalesce(func.sum(IdmsChargeOff.current_balance), Decimal("0")).label(
                    "current_balance"
                ),
                func.coalesce(func.sum(IdmsChargeOff.total_recovery), Decimal("0")).label(
                    "total_recovery"
                ),
                func.coalesce(func.sum(IdmsChargeOff.total_adjusted), Decimal("0")).label(
                    "total_adjusted"
                ),
            )
            .where(
                IdmsChargeOff.report_year == report_year,
                IdmsChargeOff.deleted_at.is_(None),
                IdmsChargeOff.charge_off_date.isnot(None),
            )
            .group_by(
                func.extract("year", IdmsChargeOff.charge_off_date),
                func.extract("month", IdmsChargeOff.charge_off_date),
            )
            .order_by(
                func.extract("year", IdmsChargeOff.charge_off_date),
                func.extract("month", IdmsChargeOff.charge_off_date),
            )
        )
        rows = []
        for r in result.all():
            year = int(r.year)
            month = int(r.month)
            rows.append({
                "year": year,
                "month": month,
                "month_name": f"{MONTH_NAMES[month - 1]} {year}",
                "count": r.count,
                "original_balance": r.original_balance or Decimal("0"),
                "current_balance": r.current_balance or Decimal("0"),
                "total_recovery": r.total_recovery or Decimal("0"),
                "total_adjusted": r.total_adjusted or Decimal("0"),
            })
        return rows

    async def get_available_years(self, db: AsyncSession) -> list[int]:
        result = await db.execute(
            select(IdmsChargeOff.report_year)
            .where(IdmsChargeOff.deleted_at.is_(None))
            .distinct()
            .order_by(IdmsChargeOff.report_year.desc())
        )
        return [r[0] for r in result.all()]

    # ------------------------------------------------------------------
    # Month End (snapshot de cartera)
    # ------------------------------------------------------------------
    async def sync_month_end(
        self, db: AsyncSession, rows: list[dict], year: int, month: int
    ) -> int:
        """Reemplaza el snapshot del período. Re-sincronizar el mismo mes lo pisa."""
        await db.execute(
            delete(IdmsMonthEnd).where(
                IdmsMonthEnd.period_year == year,
                IdmsMonthEnd.period_month == month,
            )
        )
        if rows:
            await db.execute(insert(IdmsMonthEnd), rows)
        await db.commit()
        return len(rows)

    async def get_month_end_by_period(self, db: AsyncSession) -> dict[tuple[int, int], dict]:
        """Principal balance y months-on-book de la cartera, por período.

        Months On Book = antigüedad promedio (contrato → fecha del snapshot) de
        las cuentas vivas. Es una métrica de la cartera, no de los charge offs.
        """
        months_on_book = (
            (
                func.extract("year", IdmsMonthEnd.snapshot_date)
                - func.extract("year", IdmsMonthEnd.contract_date)
            )
            * 12
            + (
                func.extract("month", IdmsMonthEnd.snapshot_date)
                - func.extract("month", IdmsMonthEnd.contract_date)
            )
        )
        result = await db.execute(
            select(
                IdmsMonthEnd.period_year.label("year"),
                IdmsMonthEnd.period_month.label("month"),
                func.count(IdmsMonthEnd.id).label("accounts"),
                func.coalesce(func.sum(IdmsMonthEnd.cur_prin_bal), Decimal("0")).label(
                    "principal_balance"
                ),
                func.avg(months_on_book).label("months_on_book"),
                func.max(IdmsMonthEnd.snapshot_date).label("snapshot_date"),
            )
            .where(IdmsMonthEnd.deleted_at.is_(None))
            .group_by(IdmsMonthEnd.period_year, IdmsMonthEnd.period_month)
        )
        return {
            (int(r.year), int(r.month)): {
                "accounts": r.accounts,
                "principal_balance": r.principal_balance or Decimal("0"),
                "months_on_book": (
                    Decimal(str(round(float(r.months_on_book), 2)))
                    if r.months_on_book is not None
                    else None
                ),
                "snapshot_date": r.snapshot_date,
            }
            for r in result.all()
        }

    # ------------------------------------------------------------------
    # Charge Offs — Overview estilo AutoAnalytix
    # ------------------------------------------------------------------
    async def _charge_off_by_month(self, db: AsyncSession, year: int) -> dict[int, dict]:
        """Agregados de charge offs por mes del año indicado, indexados por mes."""
        result = await db.execute(
            select(
                func.extract("month", IdmsChargeOff.charge_off_date).label("month"),
                func.count(IdmsChargeOff.id).label("count"),
                func.coalesce(func.sum(IdmsChargeOff.original_balance), Decimal("0")).label(
                    "original_balance"
                ),
                func.coalesce(func.sum(IdmsChargeOff.current_balance), Decimal("0")).label(
                    "current_balance"
                ),
                func.coalesce(func.sum(IdmsChargeOff.recovery_acv), Decimal("0")).label(
                    "recovery_acv"
                ),
            )
            .where(
                IdmsChargeOff.report_year == year,
                IdmsChargeOff.deleted_at.is_(None),
                IdmsChargeOff.charge_off_date.isnot(None),
            )
            .group_by(func.extract("month", IdmsChargeOff.charge_off_date))
        )
        return {
            int(r.month): {
                "count": r.count,
                "original_balance": r.original_balance or Decimal("0"),
                "current_balance": r.current_balance or Decimal("0"),
                "recovery_acv": r.recovery_acv or Decimal("0"),
            }
            for r in result.all()
        }

    async def get_charge_off_overview(self, db: AsyncSession, year: int) -> dict:
        """Replica el 'Charge Off Overview' de AutoAnalytix para un año.

        YTD = meses del año con datos. La comparación contra el año anterior usa
        ese mismo rango de meses. MTD = último mes con datos.
        """
        current = await self._charge_off_by_month(db, year)
        prior = await self._charge_off_by_month(db, year - 1)
        portfolio = await self.get_month_end_by_period(db)

        months = sorted(current.keys())

        def acumular(datos: dict[int, dict], meses: list[int]) -> dict:
            sel = [datos[m] for m in meses if m in datos]
            count = sum(d["count"] for d in sel)
            original = sum((d["original_balance"] for d in sel), Decimal("0"))
            return {
                "count": count,
                "total_charge_off": original,
                "recovery_acv": sum((d["recovery_acv"] for d in sel), Decimal("0")),
                "avg_prin_bal": (original / count) if count else Decimal("0"),
            }

        ytd = acumular(current, months)
        ytd_prior = acumular(prior, months)
        mtd = acumular(current, months[-1:]) if months else acumular(current, [])

        def delta(actual: Decimal, previo: Decimal) -> dict:
            diff = Decimal(actual) - Decimal(previo)
            return {"value": diff, "pct": _ratio(diff, previo)}

        # El Gross C/O Ratio solo tiene sentido comparando el mismo rango de meses
        # en numerador y denominador. Como el principal balance solo existe desde
        # que se empezó a snapshotear la cartera, se restringe a esos meses; si no
        # hay ninguno, el ratio queda en 0 y has_portfolio_data avisa por qué.
        meses_con_cartera = [m for m in months if (year, m) in portfolio]
        principal_ytd = sum(
            (portfolio[(year, m)]["principal_balance"] for m in meses_con_cartera),
            Decimal("0"),
        )
        co_con_cartera = acumular(current, meses_con_cartera)
        gross_ratio = _ratio(co_con_cartera["total_charge_off"], principal_ytd)

        return {
            "year": year,
            "months_with_data": months,
            "ytd_count": ytd["count"],
            "ytd_total_charge_off": ytd["total_charge_off"],
            "ytd_avg_prin_bal": ytd["avg_prin_bal"],
            "delta_count": delta(ytd["count"], ytd_prior["count"]),
            "delta_total_charge_off": delta(
                ytd["total_charge_off"], ytd_prior["total_charge_off"]
            ),
            "delta_avg_prin_bal": delta(ytd["avg_prin_bal"], ytd_prior["avg_prin_bal"]),
            "mtd_count": mtd["count"],
            "mtd_total_charge_off": mtd["total_charge_off"],
            "mtd_avg_prin_bal": mtd["avg_prin_bal"],
            "recovery_ratio": _ratio(ytd["recovery_acv"], ytd["total_charge_off"]),
            "gross_co_ratio": gross_ratio,
            "annualized_co_ratio": gross_ratio * 12,
            "has_portfolio_data": principal_ytd > 0,
        }

    async def get_charge_off_monthly_detail(self, db: AsyncSession, year: int) -> list[dict]:
        """Tabla mensual del Overview, con las columnas de AutoAnalytix."""
        current = await self._charge_off_by_month(db, year)
        portfolio = await self.get_month_end_by_period(db)

        rows = []
        for month in sorted(current.keys()):
            d = current[month]
            port = portfolio.get((year, month))
            principal = port["principal_balance"] if port else None
            rows.append({
                "year": year,
                "month": month,
                "month_name": f"{MONTH_NAMES[month - 1]} {year}",
                "principal_balance": principal,
                "original_balance": d["original_balance"],
                "count": d["count"],
                "current_balance": d["current_balance"],
                "recovery_acv": d["recovery_acv"],
                "recovery_ratio": _ratio(d["recovery_acv"], d["original_balance"]),
                "gross_co_ratio": _ratio(d["original_balance"], principal) if principal else None,
                "months_on_book": port["months_on_book"] if port else None,
            })
        return rows
