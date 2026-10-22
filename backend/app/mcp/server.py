"""MCP server exposing read-only Automania data as tools.

Every tool delegates to an existing service/repository and returns JSON-serializable data.
The chat service consumes it in-memory; it can later be exposed over HTTP for external clients.
"""
from __future__ import annotations

from calendar import monthrange
from collections.abc import Awaitable, Callable
from datetime import date, datetime, time, timezone
from typing import Annotated, Any, Literal, TypeVar

from fastapi import HTTPException
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.repositories.coverage_repo import CoverageRepository
from app.schemas.idms import (
    IdmsChargeOffKpisOut,
    IdmsChargeOffMonthlyDetailOut,
    IdmsChargeOffMonthlyOut,
    IdmsChargeOffOut,
    IdmsChargeOffOverviewOut,
    IdmsInventoryAgingOut,
    IdmsInventoryKpisOut,
    IdmsInventoryOut,
    IdmsSalesBySalespersonOut,
    IdmsSalesByVehicleOut,
    IdmsSalesKpisOut,
    IdmsSalesMonthlyOut,
    IdmsSalesOut,
)
from app.services.call_analytics_service import CallAnalyticsService
from app.services.hours_service import HoursService
from app.services.idms_service import IdmsService
from app.services.payment_service import PaymentService
from app.services.sales_service import SalesService
from app.services.technician_service import TechnicianService
from app.services.wip_service import WipFilters, WipService

server = MCPServer("automania")

T = TypeVar("T")

FromDate = Annotated[
    date | None, Field(description="Start date (YYYY-MM-DD). Defaults to the first day of the current month.")
]
ToDate = Annotated[
    date | None, Field(description="End date (YYYY-MM-DD). Defaults to the last day of the current month.")
]
Year = Annotated[int | None, Field(description="Report year, e.g. 2026. Defaults to the current year.")]


def _range(from_date: date | None, to_date: date | None) -> tuple[date, date]:
    today = date.today()
    start = from_date or today.replace(day=1)
    end = to_date or today.replace(day=monthrange(today.year, today.month)[1])
    if start > end:
        raise ToolError("from_date must be before or equal to to_date")
    return start, end


def _dump(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_dump(v) for v in value]
    if isinstance(value, dict):
        return {k: _dump(v) for k, v in value.items()}
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


async def _run(fn: Callable[[AsyncSession], Awaitable[T]]) -> Any:
    """Run a query in its own session and translate API errors into readable tool errors."""
    async with AsyncSessionLocal() as db:
        try:
            return _dump(await fn(db))
        except HTTPException as exc:
            raise ToolError(str(exc.detail)) from exc


# --- Coverage --------------------------------------------------------------


@server.tool()
async def get_data_coverage() -> Any:
    """List which date ranges have data for each source (sales, hours, technicians, payments,
    calls) and the WIP snapshot size, plus the available IDMS report years.
    Call this first when the user does not specify a period."""

    async def q(db: AsyncSession) -> dict[str, Any]:
        idms = IdmsService()
        return {
            "today": date.today(),
            "sources": await CoverageRepository().get_coverage(db),
            "idms_charge_off_years": await idms.get_available_years(db),
            "idms_sales_years": await idms.get_sales_years(db),
        }

    return await _run(q)


# --- Shop sales (daily_sales) ----------------------------------------------


@server.tool()
async def get_sales_kpis(from_date: FromDate = None, to_date: ToDate = None) -> Any:
    """Shop sales KPIs for a period: total cars, gross/net sales, average ticket, COGS, gross profit and %."""
    start, end = _range(from_date, to_date)
    return await _run(lambda db: SalesService().get_kpis(db, start, end))


@server.tool()
async def get_sales_trend(from_date: FromDate = None, to_date: ToDate = None) -> Any:
    """Daily shop sales series (one point per day) for a period."""
    start, end = _range(from_date, to_date)
    return await _run(lambda db: SalesService().get_trend(db, start, end))


@server.tool()
async def get_sales_by_day_of_week(from_date: FromDate = None, to_date: ToDate = None) -> Any:
    """Shop sales grouped by day of the week for a period."""
    start, end = _range(from_date, to_date)
    return await _run(lambda db: SalesService().get_by_day_of_week(db, start, end))


# --- Hours / technicians -----------------------------------------------------


@server.tool()
async def get_hours_kpis(from_date: FromDate = None, to_date: ToDate = None) -> Any:
    """Shop hours KPIs: labor dollars, hours sold/paid/worked, advisor efficiency, technician proficiency."""
    start, end = _range(from_date, to_date)
    return await _run(lambda db: HoursService().get_kpis(db, start, end))


@server.tool()
async def get_technician_ranking(
    metric: Literal["hours_sold", "labor_dollars", "proficiency"] = "hours_sold",
    from_date: FromDate = None,
    to_date: ToDate = None,
) -> Any:
    """Technicians ranked by the given metric for a period."""
    start, end = _range(from_date, to_date)
    return await _run(lambda db: TechnicianService().get_ranking(db, start, end, metric))


@server.tool()
async def get_technician_detail(
    name: Annotated[str, Field(description="Exact technician name, e.g. 'Joe Davis'.")],
    from_date: FromDate = None,
    to_date: ToDate = None,
) -> Any:
    """Hours records of a single technician for a period."""
    start, end = _range(from_date, to_date)
    return await _run(lambda db: TechnicianService().get_detail(db, name, start, end))


# --- Work in progress (live snapshot, no dates) ------------------------------


@server.tool()
async def get_wip_kpis() -> Any:
    """Current work-in-progress snapshot KPIs: open ROs, estimated, COG, COL, average and oldest days open."""
    return await _run(lambda db: WipService().get_kpis(db))


@server.tool()
async def get_wip_aging() -> Any:
    """Open ROs grouped by age bucket (0-7d, 8-14d, 15-30d, 31-60d, 60+d)."""
    return await _run(lambda db: WipService().get_aging(db))


@server.tool()
async def get_wip_by_category() -> Any:
    """Open ROs grouped by repair category."""
    return await _run(lambda db: WipService().get_by_category(db))


@server.tool()
async def get_wip_by_advisor() -> Any:
    """Open ROs grouped by service advisor."""
    return await _run(lambda db: WipService().get_by_advisor(db))


@server.tool()
async def list_wip(
    advisor: str | None = None,
    category: str | None = None,
    min_days: Annotated[int | None, Field(ge=0)] = None,
    max_days: Annotated[int | None, Field(ge=0)] = None,
    limit: Annotated[int, Field(ge=1, le=50)] = 20,
) -> Any:
    """List open RO lines from the WIP snapshot, optionally filtered. Returns at most 50 rows plus the total count."""
    filters = WipFilters(advisor=advisor, category=category, min_days=min_days, max_days=max_days)
    return await _run(lambda db: WipService().list(db, filters, page=1, limit=limit))


# --- Payments / calls ----------------------------------------------------------


@server.tool()
async def get_payment_kpis(from_date: FromDate = None, to_date: ToDate = None) -> Any:
    """Payment/collection KPIs for a period: number of payments, total amount, fees, refunds."""
    start, end = _range(from_date, to_date)
    return await _run(lambda db: PaymentService().get_kpis(db, from_date=start, to_date=end))


@server.tool()
async def get_payments_by_collector(from_date: FromDate = None, to_date: ToDate = None) -> Any:
    """Payments grouped by collector for a period."""
    start, end = _range(from_date, to_date)
    return await _run(lambda db: PaymentService().get_by_collector(db, from_date=start, to_date=end))


@server.tool()
async def get_payments_by_method(from_date: FromDate = None, to_date: ToDate = None) -> Any:
    """Payments grouped by payment method for a period."""
    start, end = _range(from_date, to_date)
    return await _run(lambda db: PaymentService().get_by_method(db, from_date=start, to_date=end))


@server.tool()
async def get_call_kpis(from_date: FromDate = None, to_date: ToDate = None) -> Any:
    """Phone call KPIs for a period: total, inbound, outbound, answered, abandoned, duration."""
    start, end = _range(from_date, to_date)
    dt_from = datetime.combine(start, time.min, tzinfo=timezone.utc)
    dt_to = datetime.combine(end, time.max, tzinfo=timezone.utc)
    return await _run(lambda db: CallAnalyticsService().get_kpis(db, dt_from, dt_to))


# --- IDMS (dealership) -----------------------------------------------------------


def _year(year: int | None) -> int:
    return year or date.today().year


@server.tool()
async def get_idms_chargeoff_kpis(year: Year = None) -> Any:
    """IDMS charge-off KPIs for a report year."""

    async def q(db: AsyncSession) -> IdmsChargeOffKpisOut:
        return IdmsChargeOffKpisOut(**await IdmsService().get_charge_off_kpis(db, year=_year(year)))

    return await _run(q)


@server.tool()
async def get_idms_chargeoff_monthly(year: Year = None) -> Any:
    """IDMS charge-offs aggregated by month for a report year."""

    async def q(db: AsyncSession) -> list[IdmsChargeOffMonthlyOut]:
        rows = await IdmsService().get_charge_off_monthly(db, year=_year(year))
        return [IdmsChargeOffMonthlyOut(**r) for r in rows]

    return await _run(q)


@server.tool()
async def get_idms_sales_kpis(year: Year = None) -> Any:
    """IDMS vehicle sales KPIs for a report year."""

    async def q(db: AsyncSession) -> IdmsSalesKpisOut:
        return IdmsSalesKpisOut(**await IdmsService().get_sales_kpis(db, year=_year(year)))

    return await _run(q)


@server.tool()
async def get_idms_sales_monthly(year: Year = None) -> Any:
    """IDMS vehicle sales aggregated by month for a report year."""

    async def q(db: AsyncSession) -> list[IdmsSalesMonthlyOut]:
        rows = await IdmsService().get_sales_monthly(db, year=_year(year))
        return [IdmsSalesMonthlyOut(**r) for r in rows]

    return await _run(q)


@server.tool()
async def get_idms_sales_by_salesperson(year: Year = None) -> Any:
    """IDMS vehicle sales grouped by salesperson for a report year."""

    async def q(db: AsyncSession) -> list[IdmsSalesBySalespersonOut]:
        rows = await IdmsService().get_sales_by_salesperson(db, year=_year(year))
        return [IdmsSalesBySalespersonOut(**r) for r in rows]

    return await _run(q)


@server.tool()
async def get_idms_inventory_kpis() -> Any:
    """Current IDMS vehicle inventory KPIs."""

    async def q(db: AsyncSession) -> IdmsInventoryKpisOut:
        return IdmsInventoryKpisOut(**await IdmsService().get_inventory_kpis(db))

    return await _run(q)


@server.tool()
async def get_idms_inventory_aging() -> Any:
    """Current IDMS vehicle inventory grouped by age bucket."""

    async def q(db: AsyncSession) -> list[IdmsInventoryAgingOut]:
        rows = await IdmsService().get_inventory_aging(db)
        return [IdmsInventoryAgingOut(**r) for r in rows]

    return await _run(q)


# --- IDMS detail lists ---------------------------------------------------------
# The tabs list every row; tools return a filtered, sorted, trimmed page so results fit the
# model context. Only the fields useful for answering questions are kept.

ListLimit = Annotated[int, Field(ge=1, le=50, description="Max rows to return (1-50).")]
Month = Annotated[int | None, Field(ge=1, le=12, description="Month number (1-12) to filter by.")]

_CHARGE_OFF_FIELDS = (
    "acct_id", "borrower", "date_sold", "charge_off_date", "vin", "year", "make", "model",
    "original_balance", "total_recovery", "current_balance", "total_adjusted",
    "repo_method", "status",
)
_SALES_FIELDS = (
    "acct_id", "borrower", "contract_date", "vin", "year_model", "make", "model", "mileage",
    "sales_price", "cash_down", "amount_financed", "inventory_cost", "total_expenses",
    "gross_profit", "salesperson", "days_on_lot", "regz_apr", "orig_term_months", "status",
)
_INVENTORY_FIELDS = (
    "stock_number", "vehicle_year", "make", "model_trim", "exterior_color", "vin_last6",
    "acq_date", "dol", "status", "price", "wholesale_price", "mileage", "snapshot_date",
)


def _contains(value: str | None, needle: str | None) -> bool:
    return needle is None or (value is not None and needle.lower() in value.lower())


def _page(items: list[BaseModel], fields: tuple[str, ...], limit: int) -> dict[str, Any]:
    return {
        "total": len(items),
        "returned": min(len(items), limit),
        "items": [item.model_dump(mode="json", include=set(fields)) for item in items[:limit]],
    }


@server.tool()
async def get_idms_chargeoff_overview(year: Year = None) -> Any:
    """IDMS charge-off overview for a report year: YTD and MTD count/total/average principal,
    deltas vs the previous year, recovery ratio, gross and annualized charge-off ratios."""

    async def q(db: AsyncSession) -> IdmsChargeOffOverviewOut:
        return IdmsChargeOffOverviewOut(**await IdmsService().get_charge_off_overview(db, year=_year(year)))

    return await _run(q)


@server.tool()
async def get_idms_chargeoff_monthly_detail(year: Year = None) -> Any:
    """IDMS charge-off detail per month for a report year: principal and original balance,
    count, current balance, recovery ACV, recovery and gross charge-off ratios, months on book."""

    async def q(db: AsyncSession) -> list[IdmsChargeOffMonthlyDetailOut]:
        rows = await IdmsService().get_charge_off_monthly_detail(db, year=_year(year))
        return [IdmsChargeOffMonthlyDetailOut(**r) for r in rows]

    return await _run(q)


@server.tool()
async def list_idms_charge_offs(
    year: Year = None,
    month: Month = None,
    borrower: Annotated[str | None, Field(description="Case-insensitive substring of the borrower name.")] = None,
    make: str | None = None,
    sort_by: Literal["current_balance", "original_balance", "charge_off_date"] = "current_balance",
    limit: ListLimit = 20,
) -> Any:
    """List individual IDMS charge-off accounts for a report year, filtered and sorted (descending).
    Returns the total matching count and up to `limit` rows."""

    async def q(db: AsyncSession) -> dict[str, Any]:
        rows = await IdmsService().get_charge_offs(db, year=_year(year))
        items = [
            r for r in (IdmsChargeOffOut.model_validate(x) for x in rows)
            if (month is None or (r.charge_off_date is not None and r.charge_off_date.month == month))
            and _contains(r.borrower, borrower)
            and _contains(r.make, make)
        ]
        items.sort(key=lambda r: (getattr(r, sort_by) is not None, getattr(r, sort_by) or 0), reverse=True)
        return _page(items, _CHARGE_OFF_FIELDS, limit)

    return await _run(q)


@server.tool()
async def get_idms_sales_by_vehicle(year: Year = None) -> Any:
    """IDMS vehicle sales grouped by make/model for a report year: units, sales price, gross profit."""

    async def q(db: AsyncSession) -> list[IdmsSalesByVehicleOut]:
        rows = await IdmsService().get_sales_by_vehicle(db, year=_year(year))
        return [IdmsSalesByVehicleOut(**r) for r in rows]

    return await _run(q)


@server.tool()
async def list_idms_sales(
    year: Year = None,
    month: Month = None,
    salesperson: Annotated[str | None, Field(description="Case-insensitive substring of the salesperson.")] = None,
    make: str | None = None,
    model: str | None = None,
    sort_by: Literal["contract_date", "sales_price", "gross_profit", "days_on_lot"] = "contract_date",
    limit: ListLimit = 20,
) -> Any:
    """List individual IDMS vehicle sales (deals) for a report year, filtered and sorted (descending).
    Returns the total matching count and up to `limit` rows."""

    async def q(db: AsyncSession) -> dict[str, Any]:
        rows = await IdmsService().get_sales(db, year=_year(year))
        items = [
            r for r in (IdmsSalesOut.model_validate(x) for x in rows)
            if (month is None or (r.contract_date is not None and r.contract_date.month == month))
            and _contains(r.salesperson, salesperson)
            and _contains(r.make, make)
            and _contains(r.model, model)
        ]
        items.sort(key=lambda r: (getattr(r, sort_by) is not None, getattr(r, sort_by) or 0), reverse=True)
        return _page(items, _SALES_FIELDS, limit)

    return await _run(q)


@server.tool()
async def list_idms_inventory(
    make: str | None = None,
    model: Annotated[str | None, Field(description="Case-insensitive substring of model/trim.")] = None,
    status: str | None = None,
    min_days: Annotated[int | None, Field(ge=0, description="Minimum days on lot.")] = None,
    max_days: Annotated[int | None, Field(ge=0, description="Maximum days on lot.")] = None,
    sort_by: Literal["dol", "price", "acq_date"] = "dol",
    limit: ListLimit = 20,
) -> Any:
    """List vehicles in the current IDMS inventory, filtered and sorted (descending).
    `dol` is days on lot. Returns the total matching count and up to `limit` rows."""

    async def q(db: AsyncSession) -> dict[str, Any]:
        rows = await IdmsService().get_inventory(db)
        items = [
            r for r in (IdmsInventoryOut.model_validate(x) for x in rows)
            if _contains(r.make, make)
            and _contains(r.model_trim, model)
            and _contains(r.status, status)
            and (min_days is None or (r.dol is not None and r.dol >= min_days))
            and (max_days is None or (r.dol is not None and r.dol <= max_days))
        ]
        items.sort(key=lambda r: (getattr(r, sort_by) is not None, getattr(r, sort_by) or 0), reverse=True)
        return _page(items, _INVENTORY_FIELDS, limit)

    return await _run(q)
