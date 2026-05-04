from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, Index, Integer, Numeric, String, func

from .base import Base, TimestampMixin


class DailySales(TimestampMixin, Base):
    __tablename__ = "daily_sales"

    date = Column(Date, nullable=False)
    day_of_week = Column(String(10), nullable=False)
    total_cars = Column(Integer, nullable=False)
    gross_sales = Column(Numeric(10, 2), nullable=False)
    net_sales = Column(Numeric(10, 2), nullable=False)
    sales = Column(Numeric(10, 2), nullable=False)
    ticket_average = Column(Numeric(10, 2), nullable=False)
    cost_of_goods = Column(Numeric(10, 2), nullable=False)
    cogs_percent = Column(Numeric(5, 2), nullable=False)
    gross_profit = Column(Numeric(10, 2), nullable=False)
    gross_profit_pct = Column(Numeric(5, 2), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    imported_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (Index("ix_daily_sales_date", "date"),)
