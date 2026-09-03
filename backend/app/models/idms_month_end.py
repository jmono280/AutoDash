from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, Index, Integer, Numeric, String, func

from .base import Base, TimestampMixin


class IdmsMonthEnd(TimestampMixin, Base):
    """Snapshot mensual de la cartera activa (reporte IDMS 2159272).

    El reporte es una foto del momento, no una serie histórica: IDMS no guarda
    los saldos de meses cerrados. Por eso se persiste un snapshot por período,
    que es lo que permite calcular Gross C/O Ratio y Months On Book.
    """

    __tablename__ = "idms_month_end"

    period_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=False)
    snapshot_date = Column(Date, nullable=False)
    acct_id = Column(String(50), nullable=False)
    stock_number = Column(String(50), nullable=True)
    borrower = Column(String(200), nullable=True)
    contract_date = Column(Date, nullable=True)
    vin = Column(String(50), nullable=True)
    year = Column(String(20), nullable=True)
    make = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    mileage = Column(Integer, nullable=True)
    cur_prin_bal = Column(Numeric(12, 2), nullable=False, default=0)
    cur_prin_bal_plus_tax = Column(Numeric(12, 2), nullable=False, default=0)
    cur_int_bal = Column(Numeric(12, 2), nullable=False, default=0)
    cur_sales_tax_bal = Column(Numeric(12, 2), nullable=False, default=0)
    cur_non_earning_prin_bal = Column(Numeric(12, 2), nullable=False, default=0)
    cur_note_bal = Column(Numeric(12, 2), nullable=False, default=0)
    days_past_due = Column(Integer, nullable=True)
    payment_recency = Column(Integer, nullable=True)
    acct_status = Column(String(20), nullable=True)
    imported_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_idms_month_end_period", "period_year", "period_month"),
        Index("ix_idms_month_end_acct", "acct_id"),
    )
