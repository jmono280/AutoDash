from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, Index, Integer, Numeric, String, func

from .base import Base, TimestampMixin


class IdmsSales(TimestampMixin, Base):
    """Ventas de IDMS (reporte Auto Analytix - Sales, ID 2159264)."""

    __tablename__ = "idms_sales"

    report_year = Column(Integer, nullable=False)
    acct_id = Column(String(50), nullable=False)
    acct_type = Column(String(100), nullable=True)
    borrower = Column(String(200), nullable=True)
    booked_date = Column(Date, nullable=True)
    contract_date = Column(Date, nullable=True)
    vin = Column(String(50), nullable=True)

    sales_price = Column(Numeric(12, 2), nullable=False, default=0)
    cur_total_prin_bal_plus_tax = Column(Numeric(12, 2), nullable=False, default=0)
    cash_down = Column(Numeric(12, 2), nullable=False, default=0)
    deferred_down = Column(Numeric(12, 2), nullable=False, default=0)
    trade_in_acv = Column(Numeric(12, 2), nullable=False, default=0)
    trade_in_payoff = Column(Numeric(12, 2), nullable=False, default=0)

    year_model = Column(String(20), nullable=True)
    make = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    mileage = Column(Integer, nullable=True)

    inventory_cost = Column(Numeric(12, 2), nullable=False, default=0)
    cost_with_pack_fee = Column(Numeric(12, 2), nullable=False, default=0)
    total_expenses = Column(Numeric(12, 2), nullable=False, default=0)

    orig_payments = Column(Integer, nullable=True)
    orig_term_months = Column(Integer, nullable=True)
    regz_apr = Column(Numeric(8, 6), nullable=True)
    payment_frequency = Column(String(20), nullable=True)
    amount_financed = Column(Numeric(12, 2), nullable=False, default=0)
    finance_charge = Column(Numeric(12, 2), nullable=False, default=0)
    total_of_payments = Column(Numeric(12, 2), nullable=False, default=0)
    reg_payment = Column(Numeric(12, 2), nullable=False, default=0)
    monthly_payment = Column(Numeric(12, 2), nullable=False, default=0)

    sales_location = Column(String(100), nullable=True)
    salesperson = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(20), nullable=True)
    zipcode = Column(String(20), nullable=True)
    referral = Column(String(100), nullable=True)

    gross_profit = Column(Numeric(12, 2), nullable=False, default=0)
    inventory_type = Column(String(50), nullable=True)
    days_on_lot = Column(Integer, nullable=True)
    status = Column(String(50), nullable=True)
    acct_flags = Column(String(200), nullable=True)
    udf_text_value1 = Column(String(50), nullable=True)

    # Columnas extra del reporte MySQL
    branch_name = Column(String(100), nullable=True)
    branch_desc = Column(String(100), nullable=True)
    portfolio_name = Column(String(100), nullable=True)
    source_name = Column(String(100), nullable=True)
    lender_name = Column(String(100), nullable=True)

    imported_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_idms_sales_year", "report_year"),
        Index("ix_idms_sales_booked_date", "booked_date"),
        Index("ix_idms_sales_acct", "acct_id"),
        Index("ix_idms_sales_salesperson", "salesperson"),
        Index("ix_idms_sales_make", "make"),
    )
