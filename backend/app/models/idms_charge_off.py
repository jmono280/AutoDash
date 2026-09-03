from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, Index, Integer, Numeric, String, func

from .base import Base, TimestampMixin


class IdmsChargeOff(TimestampMixin, Base):
    __tablename__ = "idms_charge_offs"

    report_year = Column(Integer, nullable=False)
    acct_id = Column(String(50), nullable=False)
    borrower = Column(String(200), nullable=True)
    date_sold = Column(Date, nullable=True)
    charge_off_date = Column(Date, nullable=True)
    vin = Column(String(50), nullable=True)
    year = Column(String(20), nullable=True)
    make = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    original_balance = Column(Numeric(12, 2), nullable=False, default=0)
    original_total_balance = Column(Numeric(12, 2), nullable=False, default=0)
    total_recovery = Column(Numeric(12, 2), nullable=False, default=0)
    # "Recovery ACV" de AutoAnalytix. Sale de "Charge Off ACV Adjusted", no de
    # "Total Charge Off Recovery", que en el reporte viene casi siempre en cero.
    recovery_acv = Column(Numeric(12, 2), nullable=False, default=0)
    current_balance = Column(Numeric(12, 2), nullable=False, default=0)
    total_adjusted = Column(Numeric(12, 2), nullable=False, default=0)
    repo_method = Column(String(100), nullable=True)
    status = Column(String(100), nullable=True)
    acct_flags = Column(String(200), nullable=True)
    imported_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_idms_charge_off_year", "report_year"),
        Index("ix_idms_charge_off_acct", "acct_id"),
        Index("ix_idms_charge_off_co_date", "charge_off_date"),
    )
