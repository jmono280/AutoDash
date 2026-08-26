"""Parsea el Excel histórico de Charge Offs (Manual Pull) a filas de BD."""

from __future__ import annotations

import io
from datetime import date
from typing import Any

import pandas as pd


def _to_str(value) -> str | None:
    if pd.isna(value):
        return None
    s = str(value).strip()
    return s if s else None


def _to_date(value) -> date | None:
    if pd.isna(value):
        return None
    try:
        return pd.to_datetime(value).date()
    except (ValueError, TypeError):
        return None


def _to_float(value) -> float:
    if pd.isna(value):
        return 0.0
    s = str(value).replace("$", "").replace(",", "").replace("(", "-").replace(")", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_chargeoff_historical_excel(file_bytes: bytes) -> list[dict[str, Any]]:
    """
    Parsea el Excel histórico de Charge Offs.
    El header real está en la tercera fila (índice 2).
    """
    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0, header=2)

    by_acct: dict[str, dict[str, Any]] = {}
    for _, row in df.iterrows():
        acct_id = _to_str(row.get("Acct ID"))
        if not acct_id or acct_id in by_acct:
            continue

        charge_off_date = _to_date(row.get("Charge Off Date"))
        report_year = charge_off_date.year if charge_off_date else None

        by_acct[acct_id] = {
            "report_year": report_year,
            "acct_id": acct_id,
            "borrower": _to_str(row.get("Borrower 1 Listing Name")),
            "date_sold": _to_date(row.get("Date Sold")),
            "charge_off_date": charge_off_date,
            "vin": _to_str(row.get("Collateral VIN")),
            "year": _to_str(row.get("Year")),
            "make": _to_str(row.get("Make")),
            "model": _to_str(row.get("Model")),
            "original_balance": _to_float(row.get("Original Charge Off Balance")),
            "original_total_balance": _to_float(row.get("Charge Off Orig Total Balance")),
            "total_recovery": _to_float(row.get("Total Charge Off Recovery")),
            "current_balance": 0.0,
            "total_adjusted": 0.0,
            "repo_method": _to_str(row.get("Last Repo Method Desc")),
            "status": _to_str(row.get("Acct Status Desc")),
            "acct_flags": _to_str(row.get("Acct Record Flags")),
        }

    return list(by_acct.values())
