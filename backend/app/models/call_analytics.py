from __future__ import annotations

from sqlalchemy import Column, DateTime, Index, Integer, String

from .base import Base, TimestampMixin


class CallAnalytics(TimestampMixin, Base):
    __tablename__ = "call_analytics"

    time_from        = Column(DateTime(timezone=True), nullable=False)
    time_to          = Column(DateTime(timezone=True), nullable=False)
    extension_number = Column(String(20),  nullable=False)
    extension_name   = Column(String(150), nullable=False)

    # Tabla 1 — dirección y tipo
    total_calls      = Column(Integer, nullable=False, default=0)
    inbound          = Column(Integer, nullable=False, default=0)
    outbound         = Column(Integer, nullable=False, default=0)
    direct           = Column(Integer, nullable=False, default=0)
    from_queue       = Column(Integer, nullable=False, default=0)
    transferred      = Column(Integer, nullable=False, default=0)
    portal_equiv     = Column(Integer, nullable=False, default=0)
    duration_seconds = Column(Integer, nullable=False, default=0)

    # Tabla 2 — origen y resultado
    external         = Column(Integer, nullable=False, default=0)
    internal         = Column(Integer, nullable=False, default=0)
    answered         = Column(Integer, nullable=False, default=0)
    not_answered     = Column(Integer, nullable=False, default=0)
    completed        = Column(Integer, nullable=False, default=0)
    abandoned        = Column(Integer, nullable=False, default=0)
    voicemail        = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("ix_call_analytics_time_from",        "time_from"),
        Index("ix_call_analytics_extension_number", "extension_number"),
        Index("ix_call_analytics_range_ext",        "time_from", "time_to", "extension_number"),
    )
