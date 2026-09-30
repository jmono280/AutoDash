"""Parseadores de CSV exportados por Exago/IDMS a filas para PostgreSQL."""

from __future__ import annotations

import csv
import io
import re
from datetime import date, datetime
from html import unescape
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


def parse_aa_sales(content: bytes) -> List[Dict[str, Any]]:
    """Parsea 'Auto Analytix - Sales (MySQL)' (ID 2159264) a filas de BD."""
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

    by_acct: Dict[str, Dict[str, Any]] = {}
    for row in data_rows:
        if not row or not row[0].strip():
            continue
        acct_id = get(row, "Acct ID")
        if not acct_id:
            continue
        if acct_id in by_acct:
            continue

        booked_date = _parse_date(get(row, "Booked Date"))
        report_year = booked_date.year if booked_date else None

        by_acct[acct_id] = {
            "report_year": report_year,
            "acct_id": acct_id,
            "acct_type": get(row, "Acct Type Desc") or None,
            "borrower": get(row, "Borrower 1 Full Name") or None,
            "booked_date": booked_date,
            "contract_date": _parse_date(get(row, "Contract_Date")),
            "vin": get(row, "Collateral VIN") or None,
            "sales_price": _clean_money(get(row, "Contract Sales Price")),
            "cur_total_prin_bal_plus_tax": _clean_money(
                get(row, "Primary Loan Cur Total Prin Bal Plus Sales Tax")
            ),
            "cash_down": _clean_money(get(row, "Contract Cash Down")),
            "deferred_down": _clean_money(get(row, "Contract Total Deferred Down")),
            "trade_in_acv": _clean_money(get(row, "Contract Total Trade In ACV")),
            "trade_in_payoff": _clean_money(get(row, "Contract Total Trade In Payoff")),
            "year_model": get(row, "Collateral Year Model") or None,
            "make": get(row, "Collateral Make") or None,
            "model": get(row, "Collateral Model") or None,
            "mileage": _clean_int(get(row, "Collateral Mileage")),
            "inventory_cost": _clean_money(get(row, "Contract Total Inventory Cost")),
            "cost_with_pack_fee": _clean_money(get(row, "Collateral Total Cost with Pack Fee")),
            "total_expenses": _clean_money(get(row, "Collateral Total Expenses")),
            "orig_payments": _clean_int(get(row, "Primary Loan CS Orig # Payments")),
            "orig_term_months": _clean_int(get(row, "Primary Loan Orig Term In Months")),
            "regz_apr": _clean_float(get(row, "Primary Loan RegZ APR")),
            "payment_frequency": get(row, "Primary Loan CS Payment Frequency") or None,
            "amount_financed": _clean_money(get(row, "Primary Loan Orig Amount Financed")),
            "finance_charge": _clean_money(get(row, "Contract Finance Charge")),
            "total_of_payments": _clean_money(get(row, "Contract Total Of Payments")),
            "reg_payment": _clean_money(get(row, "Primary Loan OS Reg Payment")),
            "monthly_payment": _clean_money(get(row, "Calc_MonthlyPaymentAmount")),
            "sales_location": get(row, "Sales Location Desc") or None,
            "salesperson": get(row, "Sales Group/Person 1 Name") or None,
            "city": get(row, "Borrower 1 City") or None,
            "state": get(row, "Borrower 1 State") or None,
            "zipcode": get(row, "Borrower 1 Zipcode") or None,
            "referral": get(row, "Account Deal Lead Referral Name") or None,
            "gross_profit": _clean_money(get(row, "Sales Gross Profit")),
            "inventory_type": get(row, "Collateral Inventory Type Desc") or None,
            "days_on_lot": _clean_int(get(row, "Collateral Days On Lot")),
            "status": get(row, "Acct Status") or None,
            "acct_flags": get(row, "Acct Record Flags") or None,
            "udf_text_value1": get(row, "UDF_Text_Value1") or None,
            "branch_name": get(row, "Branch Name") or None,
            "branch_desc": get(row, "Branch Desc") or None,
            "portfolio_name": get(row, "Portfolio Name") or None,
            "source_name": get(row, "Source Name") or None,
            "lender_name": get(row, "Lender Name") or None,
        }

    return list(by_acct.values())


def parse_aa_sales_manual(content: bytes) -> List[Dict[str, Any]]:
    """Parsea el CSV histórico manual de Sales (menos columnas)."""
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

    def has_col(name: str) -> bool:
        return name in header

    by_acct: Dict[str, Dict[str, Any]] = {}
    for row in data_rows:
        if not row or not row[0].strip():
            continue
        acct_id = get(row, "Acct ID")
        if not acct_id:
            continue
        if acct_id in by_acct:
            continue

        booked_date = _parse_date(get(row, "Booked Date"))
        report_year = booked_date.year if booked_date else None

        by_acct[acct_id] = {
            "report_year": report_year,
            "acct_id": acct_id,
            "acct_type": None,
            "borrower": get(row, "Borrower 1 Full Name") or None,
            "booked_date": booked_date,
            "contract_date": None,
            "vin": get(row, "Collateral VIN") or None,
            "sales_price": _clean_money(get(row, "Contract Sales Price"))
            if has_col("Contract Sales Price")
            else 0.0,
            "cur_total_prin_bal_plus_tax": 0.0,
            "cash_down": _clean_money(get(row, "Contract Cash Down"))
            if has_col("Contract Cash Down")
            else 0.0,
            "deferred_down": 0.0,
            "trade_in_acv": _clean_money(get(row, "Contract Total Trade In ACV"))
            if has_col("Contract Total Trade In ACV")
            else 0.0,
            "trade_in_payoff": _clean_money(get(row, "Contract Total Trade In Payoff"))
            if has_col("Contract Total Trade In Payoff")
            else 0.0,
            "year_model": get(row, "Collateral Year Model") or None,
            "make": get(row, "Collateral Make") or None,
            "model": get(row, "Collateral Model") or None,
            "mileage": _clean_int(get(row, "Collateral Mileage"))
            if has_col("Collateral Mileage")
            else None,
            "inventory_cost": _clean_money(get(row, "Contract Total Inventory Cost"))
            if has_col("Contract Total Inventory Cost")
            else 0.0,
            "cost_with_pack_fee": _clean_money(
                get(row, "Collateral Total Cost with Pack Fee")
            )
            if has_col("Collateral Total Cost with Pack Fee")
            else 0.0,
            "total_expenses": _clean_money(get(row, "Collateral Total Expenses"))
            if has_col("Collateral Total Expenses")
            else 0.0,
            "orig_payments": _clean_int(get(row, "Primary Loan CS Orig # Payments"))
            if has_col("Primary Loan CS Orig # Payments")
            else None,
            "orig_term_months": _clean_int(get(row, "Primary Loan Orig Term In Months"))
            if has_col("Primary Loan Orig Term In Months")
            else None,
            "regz_apr": _clean_float(get(row, "Primary Loan RegZ APR"))
            if has_col("Primary Loan RegZ APR")
            else None,
            "payment_frequency": get(row, "Primary Loan CS Payment Frequency")
            if has_col("Primary Loan CS Payment Frequency")
            else None,
            "amount_financed": _clean_money(
                get(row, "Primary Loan Orig Amount Financed")
            )
            if has_col("Primary Loan Orig Amount Financed")
            else 0.0,
            "finance_charge": _clean_money(get(row, "Contract Finance Charge"))
            if has_col("Contract Finance Charge")
            else 0.0,
            "total_of_payments": _clean_money(get(row, "Contract Total Of Payments"))
            if has_col("Contract Total Of Payments")
            else 0.0,
            "reg_payment": _clean_money(get(row, "Primary Loan OS Reg Payment"))
            if has_col("Primary Loan OS Reg Payment")
            else 0.0,
            "monthly_payment": _clean_money(get(row, "Calc_MonthlyPaymentAmount"))
            if has_col("Calc_MonthlyPaymentAmount")
            else 0.0,
            "sales_location": get(row, "Sales Location Desc")
            if has_col("Sales Location Desc")
            else None,
            "salesperson": get(row, "Sales Group/Person 1 Name")
            if has_col("Sales Group/Person 1 Name")
            else None,
            "city": get(row, "Borrower 1 City") if has_col("Borrower 1 City") else None,
            "state": get(row, "Borrower 1 State")
            if has_col("Borrower 1 State")
            else None,
            "zipcode": get(row, "Borrower 1 Zipcode")
            if has_col("Borrower 1 Zipcode")
            else None,
            "referral": get(row, "Account Deal Lead Referral Name")
            if has_col("Account Deal Lead Referral Name")
            else None,
            "gross_profit": _clean_money(get(row, "Sales Gross Profit"))
            if has_col("Sales Gross Profit")
            else 0.0,
            "inventory_type": get(row, "Collateral Inventory Type Desc")
            if has_col("Collateral Inventory Type Desc")
            else None,
            "days_on_lot": _clean_int(get(row, "Collateral Days On Lot"))
            if has_col("Collateral Days On Lot")
            else None,
            "status": get(row, "Acct Status") if has_col("Acct Status") else None,
            "acct_flags": get(row, "Acct Record Flags")
            if has_col("Acct Record Flags")
            else None,
            "udf_text_value1": None,
            "branch_name": None,
            "branch_desc": None,
            "portfolio_name": None,
            "source_name": None,
            "lender_name": None,
        }

    return list(by_acct.values())


def _clean_float(value: str) -> Optional[float]:
    if not value:
        return None
    s = value.replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Inventario (búsqueda nativa de IDMS — /Inventory/_Lookup, QueueDataSourceId=20)
# ---------------------------------------------------------------------------


def _cell_spans(cell_html: str) -> List[str]:
    """Texto de cada <span> de una celda (celdas multivalor separadas por <br/>).

    IDMS rellena las celdas vacías con `&nbsp;&nbsp;`, que aquí queda como "".
    """
    parts = re.findall(r"<span\b[^>]*>(.*?)</span>", cell_html, re.S | re.I)
    if not parts:
        txt = unescape(re.sub(r"<[^>]+>", " ", cell_html))
        txt = re.sub(r"\s+", " ", txt).strip()
        return [txt] if txt else [""]
    out = []
    for p in parts:
        t = unescape(re.sub(r"<[^>]+>", " ", p))
        out.append(re.sub(r"\s+", " ", t).strip())
    return out


def _span(spans: List[str], i: int) -> str:
    return spans[i] if i < len(spans) else ""


# Índice de columna -> texto que su encabezado debe contener en el layout
# "Marketing (wip)". Si IDMS cambia el layout activo de la cuenta (a mano o
# porque se reinició), la tabla vuelve a venir con otra estructura de celdas
# y este mapeo por índice ya no aplica — mejor fallar con un mensaje claro que
# insertar datos de columnas cruzadas en la base.
_EXPECTED_HEADER_HINTS = {
    0: "stock",
    1: "year",
    2: "make",
    3: "model",
    9: "status",
    13: "asking price",
    14: "wholesale",
    15: "inventory flags",
}


def _validate_inventory_layout(header_cells: List[str]) -> None:
    texts = [_span(_cell_spans(c), 0) for c in header_cells]
    problems = [
        f"columna {idx} ({hint!r} esperado): encontré {(texts[idx] if idx < len(texts) else '')!r}"
        for idx, hint in _EXPECTED_HEADER_HINTS.items()
        if hint not in (texts[idx].lower() if idx < len(texts) else "")
    ]
    if problems:
        raise ValueError(
            "El layout activo de inventario en IDMS no es 'Marketing (wip)' "
            "(cambió de estructura). Volvé a seleccionarlo en IDMS — ícono "
            "Layout Settings de la búsqueda de inventario — y sincronizá de "
            "nuevo. Detalle: " + "; ".join(problems)
        )


def parse_inventory(html: str, snapshot: Optional[date] = None) -> List[Dict[str, Any]]:
    """Parsea la tabla de la búsqueda de inventario de IDMS a filas de BD.

    Es un snapshot vivo: el período lo define la fecha en que se toma.
    Layout "Marketing (wip)" (QueueDataSourceId 20, ícono Layout Settings de
    IDMS) — un valor por celda; si IDMS cambia el layout activo, este mapeo por
    índice hay que revisarlo (ver IDMS_REPORTS.md). `_validate_inventory_layout`
    detecta el desajuste por el texto del encabezado antes de parsear filas.
    """
    snapshot = snapshot or date.today()
    m = re.search(r"<table\b.*?</table>", html, re.S | re.I)
    if not m:
        return []

    rows = re.findall(r"<tr\b([^>]*)>(.*?)</tr>", m.group(0), re.S | re.I)

    header_body = next((body for attrs, body in rows if "row_header" in attrs), None)
    if header_body is not None:
        header_cells = re.findall(r"<td\b[^>]*>(.*?)</td>", header_body, re.S | re.I)
        _validate_inventory_layout(header_cells)

    out: List[Dict[str, Any]] = []
    for attrs, body in rows:
        if "row_header" in attrs:
            continue
        cells = re.findall(r"<td\b[^>]*>(.*?)</td>", body, re.S | re.I)
        if len(cells) < 16:
            continue
        sp = [_cell_spans(c) for c in cells]

        # inventory_id / dealer_id del onclick: inv_takeAction(33,"10935053","104921",this)
        oc = re.search(r'inv_takeAction\(\s*\d+\s*,\s*"(\d+)"\s*,\s*"(\d+)"', attrs)

        out.append({
            "snapshot_date": snapshot,
            "inventory_id": oc.group(1) if oc else None,
            "dealer_id": oc.group(2) if oc else None,
            "stock_number": _span(sp[0], 0) or None,
            "vehicle_year": _span(sp[1], 0) or None,
            "make": _span(sp[2], 0) or None,
            "model_trim": _span(sp[3], 0) or None,
            "exterior_color": _span(sp[4], 0) or None,
            "vin_last6": _span(sp[6], 0) or None,
            "mileage": _clean_int(_span(sp[7], 0)),
            "status": _span(sp[9], 0) or None,
            "alternate_lot": _span(sp[10], 0) or None,
            "acq_date": _parse_date(_span(sp[11], 0)),
            "dol": _clean_int(_span(sp[12], 0)),
            "price": _clean_money(_span(sp[13], 0)),
            "wholesale_price": _clean_money(_span(sp[14], 0)),
            "inventory_flags": _span(sp[15], 0) or None,
        })
    return out


def parse_report(report_id: str, content: bytes) -> List[Dict[str, Any]]:
    """Dispatcher de parsers."""
    if report_id in (IDMS_CHARGE_OFF_REPORT_ID, "2120017"):
        return parse_aa_chargeoffs(content)
    if report_id == IDMS_SALES_REPORT_ID:
        return parse_aa_sales(content)
    raise ValueError(f"Reporte IDMS no soportado: {report_id}")
