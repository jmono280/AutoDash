from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CallAnalyticsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    time_from:        datetime
    time_to:          datetime
    extension_number: str
    extension_name:   str
    total_calls:      int
    inbound:          int
    outbound:         int
    direct:           int
    from_queue:       int
    transferred:      int
    portal_equiv:     int
    duration_seconds: int
    external:         int
    internal:         int
    answered:         int
    not_answered:     int
    completed:        int
    abandoned:        int
    voicemail:        int


class CallAnalyticsOut(CallAnalyticsBase):
    id:         uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class CallAnalyticsKpisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_calls:            int
    total_inbound:          int
    total_outbound:         int
    total_answered:         int
    total_not_answered:     int
    total_completed:        int
    total_abandoned:        int
    total_voicemail:        int
    total_duration_seconds: int
    extension_count:        int


class CallAnalyticsByExtensionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    extension_number: str
    extension_name:   str
    total_calls:      int
    inbound:          int
    outbound:         int
    answered:         int
    not_answered:     int
    completed:        int
    abandoned:        int
    voicemail:        int
    duration_seconds: int


class FetchRequest(BaseModel):
    time_from: datetime
    time_to:   datetime


class FetchResultOut(BaseModel):
    rows_saved: int
    time_from:  datetime
    time_to:    datetime
