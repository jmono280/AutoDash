from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, Index, Integer, Numeric, String, func

from .base import Base, TimestampMixin


class IdmsInventory(TimestampMixin, Base):
    """Snapshot vivo del inventario de IDMS (búsqueda nativa /Inventory/_Lookup).

    No es una serie histórica: cada sync borra la tabla y recarga la foto actual
    del inventario disponible, igual que work_in_progress.

    Estructura ligada al layout "Marketing (wip)" de la grilla de IDMS
    (QueueDataSourceId 20, ícono Layout Settings) — un valor por celda, ver
    IDMS_REPORTS.md.
    """

    __tablename__ = "idms_inventory"

    snapshot_date = Column(Date, nullable=False)
    inventory_id = Column(String(50), nullable=True)
    dealer_id = Column(String(50), nullable=True)

    stock_number = Column(String(50), nullable=True)
    vehicle_year = Column(String(10), nullable=True)
    vin_last6 = Column(String(20), nullable=True)
    inventory_flags = Column(String(200), nullable=True)
    make = Column(String(100), nullable=True)
    model_trim = Column(String(150), nullable=True)
    exterior_color = Column(String(60), nullable=True)

    acq_date = Column(Date, nullable=True)
    dol = Column(Integer, nullable=True)  # days on lot

    status = Column(String(60), nullable=True)
    alternate_lot = Column(String(80), nullable=True)

    price = Column(Numeric(12, 2), nullable=False, default=0)  # Asking Price
    wholesale_price = Column(Numeric(12, 2), nullable=False, default=0)

    mileage = Column(Integer, nullable=True)

    imported_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_idms_inventory_snapshot", "snapshot_date"),
        Index("ix_idms_inventory_inventory_id", "inventory_id"),
        Index("ix_idms_inventory_make", "make"),
    )
