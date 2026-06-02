from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentTransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                  uuid.UUID
    period_start:        date
    period_end:          date
    payment_date:        datetime
    account_id:          int | None
    customer_name:       str
    payment_method:      str | None
    card_last_4:         int | None
    amount:              Decimal
    convenience_fee:     Decimal
    status:              str | None
    reason_code:         str | None
    payment_origin:      str | None
    collector:           str | None
    reference_number:    str | None
    notes:               str | None
    refund_amount:       Decimal | None
    refund_date:         datetime | None
    refund_initiated_by: str | None
    imported_at:         datetime
    created_at:          datetime
    updated_at:          datetime


class PaymentKpisOut(BaseModel):
    total_payments:     int
    total_amount:       Decimal
    total_fees:         Decimal
    total_collected:    Decimal
    total_refunds:      Decimal
    avg_payment_amount: Decimal


class CollectionStatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                uuid.UUID
    period_start:      date
    period_end:        date
    collector:         str
    payments_count:    int
    payments_amount:   Decimal
    autopay_created:   int
    promise_sent:      int
    promise_confirmed: int
    messages_sent:     int
    notes_count:       int
    waived_fees_count: int
    waived_fees_amount:Decimal
    worked:            int
    imported_at:       datetime


class PaymentByCollectorOut(BaseModel):
    collector:    str
    count:        int
    total_amount: Decimal


class PaymentByMethodOut(BaseModel):
    payment_method: str
    count:          int
    total_amount:   Decimal
