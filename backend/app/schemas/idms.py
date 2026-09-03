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


# ---------------------------------------------------------------------------
# Sales
# ---------------------------------------------------------------------------


class IdmsSalesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    report_year: int
    acct_id: str
    acct_type: str | None
    borrower: str | None
    booked_date: date | None
    contract_date: date | None
    vin: str | None
    sales_price: Decimal
    cur_total_prin_bal_plus_tax: Decimal
    cash_down: Decimal
    deferred_down: Decimal
    trade_in_acv: Decimal
    trade_in_payoff: Decimal
    year_model: str | None
    make: str | None
    model: str | None
    mileage: int | None
    inventory_cost: Decimal
    cost_with_pack_fee: Decimal
    total_expenses: Decimal
    orig_payments: int | None
    orig_term_months: int | None
    regz_apr: Decimal | None
    payment_frequency: str | None
    amount_financed: Decimal
    finance_charge: Decimal
    total_of_payments: Decimal
    reg_payment: Decimal
    monthly_payment: Decimal
    sales_location: str | None
    salesperson: str | None
    city: str | None
    state: str | None
    zipcode: str | None
    referral: str | None
    gross_profit: Decimal
    inventory_type: str | None
    days_on_lot: int | None
    status: str | None
    acct_flags: str | None
    udf_text_value1: str | None
    branch_name: str | None
    branch_desc: str | None
    portfolio_name: str | None
    source_name: str | None
    lender_name: str | None
    imported_at: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class IdmsSalesKpisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    year: int
    count: int
    total_sales_price: Decimal
    total_gross_profit: Decimal
    total_cash_down: Decimal
    total_amount_financed: Decimal
    avg_gross_profit: Decimal
    imported_at: datetime | None


class IdmsSalesMonthlyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    year: int
    month: int
    month_name: str
    count: int
    sales_price: Decimal
    gross_profit: Decimal
    amount_financed: Decimal


class IdmsSalesBySalespersonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    salesperson: str
    count: int
    sales_price: Decimal
    gross_profit: Decimal


class IdmsSalesByVehicleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    make: str
    model: str
    count: int
    sales_price: Decimal
    gross_profit: Decimal


class IdmsSessionStatusOut(BaseModel):
    authenticated: bool
    mfa_required: bool = False
    message: str = ""
