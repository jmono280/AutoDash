from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, Numeric, String, func

from .base import Base, TimestampMixin


class HoursSummary(TimestampMixin, Base):
    __tablename__ = "hours_summary"

    shop_name = Column(String(100), nullable=False)
    labor_dollars = Column(Numeric(10, 2), nullable=False)
    hours_sold = Column(Numeric(8, 2), nullable=False)
    hours_paid = Column(Numeric(8, 2), nullable=False)
    hours_worked = Column(Numeric(8, 2), nullable=False)
    actual_hours = Column(Numeric(8, 2), nullable=False)
    advisor_efficiency = Column(Numeric(5, 2), nullable=False)
    technician_proficiency = Column(Numeric(5, 2), nullable=False)
    technician_productivity = Column(Numeric(5, 2), nullable=False)
    technician_efficiency = Column(Numeric(5, 2), nullable=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    imported_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
