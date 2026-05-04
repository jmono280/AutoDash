from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DailySalesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    day_of_week: str
    total_cars: int
    gross_sales: Decimal
    net_sales: Decimal
    sales: Decimal
    ticket_average: Decimal
    cost_of_goods: Decimal
    cogs_percent: Decimal
    gross_profit: Decimal
    gross_profit_pct: Decimal
    period_start: date
    period_end: date
    imported_at: datetime


class DailySalesOut(DailySalesBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class SalesKpisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_cars: int
    total_gross: Decimal
    total_net: Decimal
    avg_ticket: Decimal
    total_cogs: Decimal
    total_profit: Decimal
    profit_pct: Decimal
    cogs_pct: Decimal
    imported_at: datetime | None = None


class TrendPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    gross_sales: Decimal
    net_sales: Decimal
    profit: Decimal


class DayOfWeekStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    day_of_week: str
    avg_cars: Decimal
    avg_gross: Decimal
    count_days: int
