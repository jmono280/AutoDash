from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class WipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    shop_number: int
    ro_number: str
    op_code: str
    supplier: str | None
    advisor: str | None
    opened: datetime
    days_open: int
    customer: str
    stock_other_id: str | None
    vehicle: str
    vin: str
    estimated: Decimal | None
    category: str
    cog: Decimal
    col: Decimal
    imported_at: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class WipKpisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_ros: int
    total_estimated: Decimal
    total_cog: Decimal
    total_col: Decimal
    avg_days_open: Decimal
    oldest_ro_days: int
    imported_at: datetime | None = None


class AgingBucket(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bucket: str
    count: int
    total_estimated: Decimal


class CategoryGroup(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: str
    count: int
    total_cog: Decimal
    total_estimated: Decimal


class AdvisorGroup(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    advisor: str | None
    count: int
    total_estimated: Decimal
    avg_days_open: Decimal


class Page(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    items: list[T]
    total: int
    page: int
    limit: int
    pages: int
