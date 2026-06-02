from __future__ import annotations

import io
import re
from datetime import date, datetime, timezone
from decimal import Decimal

import pandas as pd


# ── helpers ───────────────────────────────────────────────────────────────────

def _to_decimal_or_none(val) -> Decimal | None:
    if pd.isna(val):
        return None
    return Decimal(str(val))


def _to_decimal(val) -> Decimal:
    return Decimal(str(val))


def _to_int_or_none(val) -> int | None:
    if pd.isna(val):
        return None
    return int(val)


def _to_str_or_none(val) -> str | None:
    if pd.isna(val):
        return None
    s = str(val).strip()
    return s if s else None


def _parse_dt(val) -> datetime:
    """Parse 'YYYY-MM-DD HH:MM:SS' string or Timestamp → UTC-aware datetime."""
    if isinstance(val, pd.Timestamp):
        return val.to_pydatetime().replace(tzinfo=timezone.utc)
    s = str(val).strip()
    # Handle both with and without fractional seconds
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {val!r}")


def _parse_count_amount(val) -> tuple[int, Decimal]:
    """Parse '22 - $5,221.50' → (22, Decimal('5221.50'))."""
    m = re.match(r"(\d+)\s*-\s*\$([0-9,]+\.?\d*)", str(val).strip())
    if m:
        return int(m.group(1)), Decimal(m.group(2).replace(",", ""))
    # Fallback: just a plain number
    try:
        return int(float(str(val))), Decimal("0")
    except (ValueError, TypeError):
        return 0, Decimal("0")


def _parse_period(raw_df: pd.DataFrame) -> tuple[date, date]:
    """Scan the first column for a row starting with 'Período:' and extract dates."""
    for _, row in raw_df.iterrows():
        cell = str(row.iloc[0]).strip()
        if cell.startswith("Período:") or cell.startswith("Per"):
            # 'Período: 2026-05-10 → 2026-05-15'
            body = cell.split(":", 1)[1].strip()
            parts = re.split(r"\s*→\s*|\s+-\s+", body)
            if len(parts) >= 2:
                return (
                    date.fromisoformat(parts[0].strip()[:10]),
                    date.fromisoformat(parts[1].strip()[:10]),
                )
    raise ValueError("Could not find 'Período:' row in Collection Stats sheet")


# ── public API ────────────────────────────────────────────────────────────────

def parse_payment_excel(
    file_bytes: bytes,
) -> tuple[list[dict], list[dict], date, date]:
    """
    Parse both sheets of a payment report Excel file.
    Returns (transactions, collection_stats, period_start, period_end).
    period_* is extracted from the 'Período:' metadata row in Collection Stats.
    """
    buf = io.BytesIO(file_bytes)

    # ── Sheet 2 first (need period before building transaction rows) ──────────
    stats_raw = pd.read_excel(buf, sheet_name="Collection Stats", header=0)
    period_start, period_end = _parse_period(stats_raw)

    imported_at = datetime.now(timezone.utc)

    # Parse collector rows — skip rows where Collector is NaN or starts with metadata markers
    collection_stats: list[dict] = []
    data_cols = [
        "Collector", "Payments", "Autopay Created", "Promise Sent",
        "Promise Confirmed", "Messages Sent", "Notes", "Waived Fees", "Worked",
    ]
    for _, row in stats_raw.iterrows():
        collector_val = row.get("Collector", None)
        if pd.isna(collector_val):
            continue
        collector_str = str(collector_val).strip()
        if not collector_str or collector_str.startswith("Período") or collector_str.startswith("Per") or collector_str.startswith("Generado"):
            continue

        payments_count, payments_amount = _parse_count_amount(row.get("Payments", "0"))
        waived_count, waived_amount     = _parse_count_amount(row.get("Waived Fees", "0"))

        collection_stats.append({
            "period_start":      period_start,
            "period_end":        period_end,
            "collector":         collector_str,
            "payments_count":    payments_count,
            "payments_amount":   payments_amount,
            "autopay_created":   int(float(str(row.get("Autopay Created", 0) or 0))),
            "promise_sent":      int(float(str(row.get("Promise Sent", 0) or 0))),
            "promise_confirmed": int(float(str(row.get("Promise Confirmed", 0) or 0))),
            "messages_sent":     int(float(str(row.get("Messages Sent", 0) or 0))),
            "notes_count":       int(float(str(row.get("Notes", 0) or 0))),
            "waived_fees_count": waived_count,
            "waived_fees_amount":waived_amount,
            "worked":            int(float(str(row.get("Worked", 0) or 0))),
            "imported_at":       imported_at,
        })

    # ── Sheet 1 — transactions (header on row index 2, i.e. Excel row 3) ─────
    buf.seek(0)
    df = pd.read_excel(buf, sheet_name="Sheet1", header=2)

    expected = {
        "Date", "Account", "Customer", "Payment Method Type",
        "Last 4", "Amount", "Convenience Fee", "Status",
        "Payment Origin", "Collector",
    }
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns in Sheet1: {missing}")

    transactions: list[dict] = []
    for _, row in df.iterrows():
        # Skip completely empty rows
        if pd.isna(row.get("Date")) and pd.isna(row.get("Customer")):
            continue

        transactions.append({
            "period_start":        period_start,
            "period_end":          period_end,
            "payment_date":        _parse_dt(row["Date"]),
            "account_id":          _to_int_or_none(row.get("Account")),
            "customer_name":       str(row["Customer"]).strip(),
            "payment_method":      _to_str_or_none(row.get("Payment Method Type")),
            "card_last_4":         _to_int_or_none(row.get("Last 4")),
            "amount":              _to_decimal(row["Amount"]),
            "convenience_fee":     _to_decimal(row.get("Convenience Fee", 0) or 0),
            "status":              _to_str_or_none(row.get("Status")),
            "reason_code":         _to_str_or_none(row.get("Reason Code")),
            "payment_origin":      _to_str_or_none(row.get("Payment Origin")),
            "collector":           _to_str_or_none(row.get("Collector")),
            "reference_number":    _to_str_or_none(row.get("Reference Number")),
            "notes":               _to_str_or_none(row.get("Notes")),
            "refund_amount":       _to_decimal_or_none(row.get("Refund Amount")),
            "refund_date":         None if pd.isna(row.get("Refund Date", float("nan"))) else _parse_dt(row["Refund Date"]),
            "refund_initiated_by": _to_str_or_none(row.get("Refund Initiated By Email")),
            "imported_at":         imported_at,
        })

    if not transactions:
        raise ValueError("No transaction rows found in Sheet1")

    return transactions, collection_stats, period_start, period_end
