from __future__ import annotations

import io
from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd


_COL_MAP = {
    "Shop #": "shop_number",
    "RO #": "ro_number",
    "Op Code": "op_code",
    "Supplier": "supplier",
    "Advisor": "advisor",
    "Opened": "opened",
    "Days": "days_open",
    "Customer": "customer",
    "Stk/Other ID#": "stock_other_id",
    "Vehicle": "vehicle",
    "VIN": "vin",
    "Estimated": "estimated",
    "Category": "category",
    "COG": "cog",
    "COL": "col",
}

_NULLABLE = {"supplier", "advisor", "stock_other_id", "estimated"}


def _to_decimal_or_none(val) -> Decimal | None:
    if pd.isna(val):
        return None
    return Decimal(str(val))


def _to_decimal(val) -> Decimal:
    return Decimal(str(val))


def _to_aware_dt(val) -> datetime:
    """Convert pandas Timestamp (no tz) → UTC-aware datetime."""
    if isinstance(val, pd.Timestamp):
        return val.to_pydatetime().replace(tzinfo=timezone.utc)
    return val


def parse_wip_excel(file_bytes: bytes) -> list[dict]:
    df = pd.read_excel(io.BytesIO(file_bytes))

    missing = set(_COL_MAP) - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    imported_at = datetime.now(timezone.utc)
    rows: list[dict] = []

    for _, row in df.iterrows():
        rows.append(
            {
                "shop_number": int(row["Shop #"]),
                "ro_number": str(int(row["RO #"])),
                "op_code": str(row["Op Code"]).strip(),
                "supplier": None if pd.isna(row["Supplier"]) else str(row["Supplier"]).strip(),
                "advisor": None if pd.isna(row["Advisor"]) else str(row["Advisor"]).strip(),
                "opened": _to_aware_dt(row["Opened"]),
                "days_open": int(row["Days"]),
                "customer": str(row["Customer"]).strip(),
                "stock_other_id": None if pd.isna(row["Stk/Other ID#"]) else str(row["Stk/Other ID#"]).strip(),
                "vehicle": str(row["Vehicle"]).strip(),
                "vin": str(row["VIN"]).strip(),
                "estimated": _to_decimal_or_none(row["Estimated"]),
                "category": str(row["Category"]).strip(),
                "cog": _to_decimal(row["COG"]),
                "col": _to_decimal(row["COL"]),
                "imported_at": imported_at,
            }
        )

    if not rows:
        raise ValueError("No rows found in Excel file")
    return rows
