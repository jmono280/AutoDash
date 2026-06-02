from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, Index, Integer, Numeric, String, Text, func

from app.models.base import Base, TimestampMixin


class PaymentTransaction(TimestampMixin, Base):
    __tablename__ = "payment_transactions"

    period_start        = Column(Date, nullable=False)
    period_end          = Column(Date, nullable=False)
    payment_date        = Column(DateTime(timezone=True), nullable=False)
    account_id          = Column(Integer, nullable=True)
    customer_name       = Column(String(200), nullable=False)
    payment_method      = Column(String(50), nullable=True)
    card_last_4         = Column(Integer, nullable=True)
    amount              = Column(Numeric(10, 2), nullable=False)
    convenience_fee     = Column(Numeric(10, 2), nullable=False)
    status              = Column(String(50), nullable=True)
    reason_code         = Column(String(100), nullable=True)
    payment_origin      = Column(String(100), nullable=True)
    collector           = Column(String(150), nullable=True)
    reference_number    = Column(String(100), nullable=True)
    notes               = Column(Text, nullable=True)
    refund_amount       = Column(Numeric(10, 2), nullable=True)
    refund_date         = Column(DateTime(timezone=True), nullable=True)
    refund_initiated_by = Column(String(200), nullable=True)
    imported_at         = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_payment_tx_period", "period_start", "period_end"),
        Index("ix_payment_tx_collector", "collector"),
    )
