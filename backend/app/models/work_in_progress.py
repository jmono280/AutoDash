from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, Numeric, String, func

from .base import Base, TimestampMixin


class WorkInProgress(TimestampMixin, Base):
    __tablename__ = "work_in_progress"

    shop_number = Column(Integer, nullable=False)
    ro_number = Column(String(20), nullable=False)
    op_code = Column(String(50), nullable=False)
    supplier = Column(String(100), nullable=True)
    advisor = Column(String(50), nullable=True)
    opened = Column(DateTime(timezone=True), nullable=False)
    days_open = Column(Integer, nullable=False)
    customer = Column(String(150), nullable=False)
    stock_other_id = Column(String(50), nullable=True)
    vehicle = Column(String(150), nullable=False)
    vin = Column(String(20), nullable=False)
    estimated = Column(Numeric(10, 2), nullable=True)
    category = Column(String(100), nullable=False)
    cog = Column(Numeric(10, 2), nullable=False)
    col = Column(Numeric(10, 2), nullable=False)
    imported_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
