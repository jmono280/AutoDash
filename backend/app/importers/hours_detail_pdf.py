from __future__ import annotations

import io
import re
from datetime import date, datetime, timezone
from decimal import Decimal

import pdfplumber

_PERIOD = re.compile(r"(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})")

# Lines that look like tech names but are not
_SKIP_NAMES = {"automania", "hours details report", "hours hours"}

# A valid tech name: only letters, spaces, parentheses, hyphens, apostrophes
_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z\s\(\)\-\']+$")


def _parse_date(s: str) -> date:
    return datetime.strptime(s.strip(), "%m/%d/%Y").date()


def _is_valid_name(s: str) -> bool:
    if not s or s.lower() in _SKIP_NAMES:
        return False
    if re.search(r"\d", s):  # dates, RO numbers, part numbers — all have digits
        return False
    return bool(_NAME_RE.match(s))


def parse_hours_detail(file_bytes: bytes) -> tuple[list[dict], date, date]:
    """Parse per-technician totals from hours_detail_*.pdf.

    Strategy: technician names always appear on the line IMMEDIATELY before
    the 'Hours Hours' column-header line. We track `pending_name` and promote
    it to `current_tech` when we hit that marker.

    This report only exposes Hours Paid and Hours Sold per tech.
    labor_dollars, hours_worked, and actual_hours are stored as 0.
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
    current_tech: str | None = None
    pending_name: str | None = None

    for line in full_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        # "Hours Hours" marks the start of a technician's column header.
        # The line IMMEDIATELY before it is the technician's name.
        if stripped == "Hours Hours":
            if pending_name and _is_valid_name(pending_name):
                current_tech = pending_name
            pending_name = None
            continue

        # Skip the detailed column header line
        if stripped.startswith("Est/RO #"):
            pending_name = None
            continue

        # Tech Total: "Tech Total <hours_paid> <hours_sold>"
        if stripped.lower().startswith("tech total "):
            if current_tech is not None:
                parts = stripped.split()
                if len(parts) != 4:
                    raise ValueError(f"Unexpected Tech Total format: {stripped!r}")
                rows.append(
                    {
                        "technician_name": current_tech,
                        "labor_dollars": Decimal("0"),
                        "hours_sold": Decimal(parts[3]),
                        "hours_paid": Decimal(parts[2]),
                        "hours_worked": Decimal("0"),
                        "actual_hours": Decimal("0"),
                        "technician_proficiency": None,
                        "technician_productivity": None,
                        "period_start": period_start,
                        "period_end": period_end,
                        "imported_at": imported_at,
                    }
                )
            current_tech = None
            pending_name = None
            continue

        if stripped.lower().startswith("shop total"):
            continue

        # Track every other line as a potential pending name
        pending_name = stripped

    if not rows:
        raise ValueError("No technician totals found in PDF")
    return rows, period_start, period_end
