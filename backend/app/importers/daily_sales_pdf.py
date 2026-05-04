from __future__ import annotations

import io
import re
from datetime import date, datetime, timezone
from decimal import Decimal

import pdfplumber

_DATE_ROW = re.compile(r"^\d{2}/\d{2}/\d{4}\s")
_WEEKDAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
_PERIOD = re.compile(r"(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})")


def _parse_date(s: str) -> date:
    for fmt in ("%m/%d/%Y", "%m/%d/%Y"):
        return datetime.strptime(s.strip(), fmt).date()


def _money(s: str) -> Decimal:
    return Decimal(s.lstrip("$").replace(",", ""))


def _pct(s: str) -> Decimal:
    return Decimal(s.rstrip("%"))


def parse_daily_sales(file_bytes: bytes) -> tuple[list[dict], date, date]:
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    m = _PERIOD.search(full_text)
    if not m:
        raise ValueError("Period dates not found in PDF header")
    period_start = _parse_date(m.group(1))
    period_end = _parse_date(m.group(2))
    imported_at = datetime.now(timezone.utc)

    rows: list[dict] = []
    for line in full_text.splitlines():
        if not _DATE_ROW.match(line):
            continue
        parts = line.split()
        if len(parts) < 2 or parts[1] not in _WEEKDAYS:
            continue
        if len(parts) != 11:
            raise ValueError(f"Unexpected row format ({len(parts)} tokens): {line!r}")
        rows.append(
            {
                "date": _parse_date(parts[0]),
                "day_of_week": parts[1],
                "total_cars": int(parts[2]),
                "gross_sales": _money(parts[3]),
                "net_sales": _money(parts[4]),
                "sales": _money(parts[5]),
                "ticket_average": _money(parts[6]),
                "cost_of_goods": _money(parts[7]),
                "cogs_percent": _pct(parts[8]),
                "gross_profit": _money(parts[9]),
                "gross_profit_pct": _pct(parts[10]),
                "period_start": period_start,
                "period_end": period_end,
                "imported_at": imported_at,
            }
        )

    if not rows:
        raise ValueError("No data rows found in PDF")
    return rows, period_start, period_end
