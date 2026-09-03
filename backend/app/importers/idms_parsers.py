"""Parseadores de CSV exportados por Exago/IDMS a filas para PostgreSQL."""

from __future__ import annotations

import csv
import io
from datetime import date, datetime
from typing import Any, Dict, List, Optional


IDMS_CHARGE_OFF_REPORT_ID = "2159268"
IDMS_SALES_REPORT_ID = "2159264"
IDMS_COLLECTIONS_REPORT_ID = "2160337"
IDMS_MONTH_END_REPORT_ID = "2159272"


def _parse_date(value: str) -> Optional[date]:
    value = value.strip()
    for fmt in ("%m/%d/%Y", "%m/%d/%Y %I:%M %p", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _format_date(value: str) -> str:
    d = _parse_date(value)
    return d.strftime("%m/%d/%Y") if d else value.strip()


def _clean_money(value: str) -> float:
    if not value:
        return 0.0
    s = value.replace("$", "").replace(",", "").replace("(", "-").replace(")", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


def _clean_int(value: str) -> Optional[int]:
    if not value:
        return None
    s = value.replace(",", "").strip()
    try:
        return int(float(s))
    except ValueError:
        return None


def _read_csv_rows(content: bytes) -> List[List[str]]:
    text = content.decode("utf-8", errors="replace")
    return list(csv.reader(io.StringIO(text)))


def _find_header_row(rows: List[List[str]]) -> int:
    """Encuentra la fila de encabezados (normalmente la tercera en Exago)."""
    for i, row in enumerate(rows):
        if row and row[0] and not row[0].startswith("Auto Analytix") and row[0] != "Page 1":
            return i
    return 0


def parse_aa_chargeoffs(content: bytes) -> List[Dict[str, Any]]:
    """Parsea 'Auto Analytix - Charge Offs (MySQL)' (ID 2159268) a filas de BD."""
    rows = _read_csv_rows(content)
    header_idx = _find_header_row(rows)
    if header_idx >= len(rows):
        return []

    header = [h.strip() for h in rows[header_idx]]
    data_rows = rows[header_idx + 1 :]

    def get(row: List[str], name: str) -> str:
        try:
            return row[header.index(name)].strip()
        except (ValueError, IndexError):
            return ""

    # Agrupar por Acct ID para evitar duplicados (mismo monto = cuenta única).
    # Se guarda el año real del charge_off_date para poder filtrar en BD.
    by_acct: Dict[str, Dict[str, Any]] = {}
    for row in data_rows:
        if not row or not row[0].strip():
            continue
        acct_id = get(row, "Acct ID")
        if not acct_id:
            continue
        if acct_id in by_acct:
            continue

        date_sold = _parse_date(get(row, "Date Sold"))
        charge_off_date = _parse_date(get(row, "Charge Off Date"))
        report_year = charge_off_date.year if charge_off_date else None

        by_acct[acct_id] = {
            "report_year": report_year,
            "acct_id": acct_id,
            "borrower": get(row, "Borrower 1 Listing Name") or None,
            "date_sold": date_sold,
            "charge_off_date": charge_off_date,
            "vin": get(row, "Collateral VIN") or None,
            "year": get(row, "Year") or None,
            "make": get(row, "Make") or None,
            "model": get(row, "Model") or None,
            "original_balance": _clean_money(get(row, "Original Charge Off Balance")),
            "original_total_balance": _clean_money(get(row, "Charge Off Orig Total Balance")),
            "total_recovery": _clean_money(get(row, "Total_Charge_Off_Recovery")),
            # AutoAnalytix llama "Recovery ACV" a esta columna; es la que alimenta
            # el Recovery Ratio. "Total_Charge_Off_Recovery" viene casi siempre en 0.
            "recovery_acv": _clean_money(get(row, "Charge Off ACV Adjusted")),
            "current_balance": _clean_money(get(row, "Charge Off Current Balance")),
            "total_adjusted": _clean_money(get(row, "Total Charge Off Adjusted")),
            "repo_method": get(row, "Last Repo Method Desc") or None,
            "status": get(row, "Acct Status Desc") or None,
            "acct_flags": get(row, "Acct Record Flags") or None,
        }

    return list(by_acct.values())


def parse_aa_month_end(content: bytes, snapshot: date) -> List[Dict[str, Any]]:
    """Parsea 'Auto Analytix - Month End (MySQL)' (ID 2159272) a filas de BD.

    El reporte es un snapshot vivo de la cartera, así que el período lo define la
    fecha en que se toma, no el contenido del archivo.
    """
    rows = _read_csv_rows(content)
    header_idx = _find_header_row(rows)
    if header_idx >= len(rows):
        return []

    header = [h.strip() for h in rows[header_idx]]
    data_rows = rows[header_idx + 1 :]

    if "Acct ID" not in header:
        raise ValueError(
            f"El reporte Month End no trae la columna 'Acct ID'. Recibidas: {header}"
        )

    def get(row: List[str], name: str) -> str:
        try:
            return row[header.index(name)].strip()
        except (ValueError, IndexError):
            return ""

    by_acct: Dict[str, Dict[str, Any]] = {}
    for row in data_rows:
        if not row:
            continue
        acct_id = get(row, "Acct ID")
        if not acct_id or acct_id in by_acct:
            continue

        by_acct[acct_id] = {
            "period_year": snapshot.year,
            "period_month": snapshot.month,
            "snapshot_date": snapshot,
            "acct_id": acct_id,
            "stock_number": get(row, "Collateral Stock Number") or None,
            "borrower": get(row, "Borrower 1 Listing Name") or None,
            "contract_date": _parse_date(get(row, "Primary Loan Contract Date")),
            "vin": get(row, "Collateral VIN") or None,
            "year": get(row, "Collateral Year") or None,
            "make": get(row, "Make") or None,
            "model": get(row, "Model") or None,
            "mileage": _clean_int(get(row, "Collateral Mileage")),
            "cur_prin_bal": _clean_money(get(row, "Primary Loan Cur Prin Bal")),
            "cur_prin_bal_plus_tax": _clean_money(
                get(row, "Primary Loan Cur Total Prin Bal Plus Sales Tax")
            ),
            "cur_int_bal": _clean_money(get(row, "PL Cur Total Int Bal")),
            "cur_sales_tax_bal": _clean_money(get(row, "PL Cur Sales Tax Bal")),
            "cur_non_earning_prin_bal": _clean_money(
                get(row, "Primary Loan Cur Non Earning Prin Bal")
            ),
            "cur_note_bal": _clean_money(get(row, "Primary Loan Cur Note Bal")),
            "days_past_due": _clean_int(get(row, "Filtered # Days Past Due")),
            "payment_recency": _clean_int(get(row, "Primary Loan Payment Recency")),
            "acct_status": get(row, "Acct Status") or None,
        }

    return list(by_acct.values())


def parse_report(report_id: str, content: bytes) -> List[Dict[str, Any]]:
    """Dispatcher de parsers."""
    if report_id in (IDMS_CHARGE_OFF_REPORT_ID, "2120017"):
        return parse_aa_chargeoffs(content)
    raise ValueError(f"Reporte IDMS no soportado: {report_id}")
