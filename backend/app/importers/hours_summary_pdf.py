from __future__ import annotations

import io
import re
from datetime import date, datetime, timezone
from decimal import Decimal

import pdfplumber

# Period format in this PDF: "4/1/2026 - 4/28/2026" (single-digit month/day)
_PERIOD = re.compile(r"(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})")


def _parse_date(s: str) -> date:
    return datetime.strptime(s.strip(), "%m/%d/%Y").date()


def _money(s: str) -> Decimal:
    return Decimal(s.lstrip("$").replace(",", ""))


def _pct(s: str) -> Decimal:
    return Decimal(s.rstrip("%"))


def _pct_or_null(s: str) -> Decimal | None:
    return None if s.strip() == "N/A" else _pct(s)


def parse_hours_summary(file_bytes: bytes) -> tuple[list[dict], date, date]:
    """Parse the 'Hours Report' summary table from hours_*.pdf.

    Data row format (page 2):
      Automania $36,977.05 385.20 475.00 0.00 81.09% 1,094.53 43.40% 0.00% N/A
    Columns: shop  labor$  hours_sold  hours_paid  actual_hours
             advisor_eff%  hours_worked  tech_prof%  tech_prod%  tech_eff
    """
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    m = _PERIOD.search(full_text)
    if not m:
        raise ValueError("Period dates not found in PDF")
    period_start = _parse_date(m.group(1))
    period_end = _parse_date(m.group(2))
    imported_at = datetime.now(timezone.utc)

    rows: list[dict] = []
    for line in full_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Skip aggregate/header lines
        if stripped.startswith("Company Totals") or stripped.startswith("Shop"):
            continue
        parts = stripped.split()
        # Data rows: 10 tokens where token[1] starts with '$'
        if len(parts) == 10 and parts[1].startswith("$"):
            rows.append(
                {
                    "shop_name": parts[0],
                    "labor_dollars": _money(parts[1]),
                    "hours_sold": Decimal(parts[2]),
                    "hours_paid": Decimal(parts[3]),
                    "actual_hours": Decimal(parts[4]),
                    "advisor_efficiency": _pct(parts[5]),
                    "hours_worked": Decimal(parts[6].replace(",", "")),
                    "technician_proficiency": _pct(parts[7]),
                    "technician_productivity": _pct(parts[8]),
                    "technician_efficiency": _pct_or_null(parts[9]),
                    "period_start": period_start,
                    "period_end": period_end,
                    "imported_at": imported_at,
                }
            )

    if not rows:
        raise ValueError("No shop data rows found in PDF")
    return rows, period_start, period_end
