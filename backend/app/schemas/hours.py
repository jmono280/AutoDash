from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class HoursSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    shop_name: str
    labor_dollars: Decimal
    hours_sold: Decimal
    hours_paid: Decimal
    hours_worked: Decimal
    actual_hours: Decimal
    advisor_efficiency: Decimal
    technician_proficiency: Decimal
    technician_productivity: Decimal
    technician_efficiency: Decimal | None
    period_start: date
    period_end: date
    imported_at: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class HoursKpisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    labor_dollars: Decimal
    hours_sold: Decimal
    hours_paid: Decimal
    hours_worked: Decimal
    actual_hours: Decimal
    advisor_efficiency: Decimal
    technician_proficiency: Decimal
    technician_productivity: Decimal
    technician_efficiency: Decimal | None
    imported_at: datetime | None = None
