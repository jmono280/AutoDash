from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class ImportResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rows_inserted: int
    rows_updated: int
    period_start: date | None
    period_end: date | None
    file_type: str
    message: str
