from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, Index, Integer, Numeric, String, func

from app.models.base import Base, TimestampMixin


class CollectionStat(TimestampMixin, Base):
    __tablename__ = "collection_stats"

    period_start       = Column(Date, nullable=False)
    period_end         = Column(Date, nullable=False)
    collector          = Column(String(150), nullable=False)
    payments_count     = Column(Integer, nullable=False, default=0)
    payments_amount    = Column(Numeric(10, 2), nullable=False, default=0)
    autopay_created    = Column(Integer, nullable=False, default=0)
    promise_sent       = Column(Integer, nullable=False, default=0)
    promise_confirmed  = Column(Integer, nullable=False, default=0)
    messages_sent      = Column(Integer, nullable=False, default=0)
    notes_count        = Column(Integer, nullable=False, default=0)
    waived_fees_count  = Column(Integer, nullable=False, default=0)
    waived_fees_amount = Column(Numeric(10, 2), nullable=False, default=0)
    worked             = Column(Integer, nullable=False, default=0)
    imported_at        = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_collection_stat_period", "period_start", "period_end"),
    )
