from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Charge Offs
# ---------------------------------------------------------------------------


class IdmsChargeOffBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    report_year: int
    acct_id: str
    borrower: str | None
    date_sold: date | None
    charge_off_date: date | None
    vin: str | None
    year: str | None
    make: str | None
    model: str | None
    original_balance: Decimal
    original_total_balance: Decimal
    total_recovery: Decimal
    current_balance: Decimal
    total_adjusted: Decimal
    repo_method: str | None
    status: str | None
    acct_flags: str | None
    imported_at: datetime


class IdmsChargeOffOut(IdmsChargeOffBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class IdmsChargeOffMonthlyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    year: int
    month: int
    month_name: str
    count: int
    original_balance: Decimal
    current_balance: Decimal
    total_recovery: Decimal
    total_adjusted: Decimal


class IdmsChargeOffKpisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    year: int
    count: int
    total_original_balance: Decimal
    total_current_balance: Decimal
    total_recovery: Decimal
    total_adjusted: Decimal
    imported_at: datetime | None


# ---------------------------------------------------------------------------
# Charge Off Overview (estilo AutoAnalytix)
# ---------------------------------------------------------------------------


class IdmsDeltaOut(BaseModel):
    """Variación contra el mismo rango de meses del año anterior."""

    value: Decimal
    pct: Decimal


class IdmsChargeOffOverviewOut(BaseModel):
    year: int
    months_with_data: list[int]

    ytd_count: int
    ytd_total_charge_off: Decimal
    ytd_avg_prin_bal: Decimal

    delta_count: IdmsDeltaOut
    delta_total_charge_off: IdmsDeltaOut
    delta_avg_prin_bal: IdmsDeltaOut

    mtd_count: int
    mtd_total_charge_off: Decimal
    mtd_avg_prin_bal: Decimal

    recovery_ratio: Decimal
    gross_co_ratio: Decimal
    annualized_co_ratio: Decimal
    # False mientras no haya snapshots de cartera para el rango: sin ellos,
    # Gross C/O y Annualized no se pueden calcular.
    has_portfolio_data: bool


class IdmsChargeOffMonthlyDetailOut(BaseModel):
    year: int
    month: int
    month_name: str
    principal_balance: Decimal | None
    original_balance: Decimal
    count: int
    current_balance: Decimal
    recovery_acv: Decimal
    recovery_ratio: Decimal
    gross_co_ratio: Decimal | None
    months_on_book: Decimal | None


# ---------------------------------------------------------------------------
# Sync / status
# ---------------------------------------------------------------------------


class IdmsSyncIn(BaseModel):
    year: int


class IdmsSyncOut(BaseModel):
    report_id: str
    year: int
    rows_inserted: int
    message: str


class IdmsSessionStatusOut(BaseModel):
    authenticated: bool
    mfa_required: bool = False
    message: str = ""
