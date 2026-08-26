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
