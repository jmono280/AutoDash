from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TechnicianOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    technician_name: str
    labor_dollars: Decimal
    hours_sold: Decimal
    hours_paid: Decimal
    hours_worked: Decimal
    actual_hours: Decimal
    technician_proficiency: Decimal | None
    technician_productivity: Decimal | None
    period_start: date
    period_end: date
    imported_at: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class TechnicianRankingItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    technician_name: str
    labor_dollars: Decimal
    hours_sold: Decimal
    hours_paid: Decimal
    hours_worked: Decimal
    actual_hours: Decimal
    technician_proficiency: Decimal | None
    technician_productivity: Decimal | None
