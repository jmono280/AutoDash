from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idms_charge_off import IdmsChargeOff


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
        month_names = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ]
        for r in result.all():
            year = int(r.year)
            month = int(r.month)
            rows.append({
                "year": year,
                "month": month,
                "month_name": f"{month_names[month - 1]} {year}",
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
