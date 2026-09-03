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


def parse_report(report_id: str, content: bytes) -> List[Dict[str, Any]]:
    """Dispatcher de parsers."""
    if report_id in (IDMS_CHARGE_OFF_REPORT_ID, "2120017"):
        return parse_aa_chargeoffs(content)
    if report_id == IDMS_SALES_REPORT_ID:
        return parse_aa_sales(content)
    raise ValueError(f"Reporte IDMS no soportado: {report_id}")
