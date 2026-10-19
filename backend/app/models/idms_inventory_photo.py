from __future__ import annotations

from sqlalchemy import Column, Date, Index, Integer, String

from .base import Base, TimestampMixin


class IdmsInventoryPhoto(TimestampMixin, Base):
    """Fotos de cada vehículo (hasta 10), traídas de IDMS solo cuando el sync
    de inventario corre con el checkbox "incluir fotos" activado.

    Snapshot vivo, igual que idms_inventory: cada sync-con-fotos borra y
    recarga. No lleva FK a idms_inventory.id — se relaciona por inventory_id
    (string de IDMS), mismo criterio que el resto del módulo.
    """

    __tablename__ = "idms_inventory_photos"

    snapshot_date = Column(Date, nullable=False)
    inventory_id = Column(String(50), nullable=False)
    dealer_id = Column(String(50), nullable=True)
    position = Column(Integer, nullable=False)
    thumbnail_url = Column(String(300), nullable=False)
    image_url = Column(String(300), nullable=False)

    __table_args__ = (
        Index("ix_idms_inventory_photo_inventory_id", "inventory_id"),
    )
