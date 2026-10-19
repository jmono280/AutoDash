"""Reporte PDF del 'Charge Off Overview' (WeasyPrint) — KPIs + tabla mensual.

Función pura: recibe el overview y el detalle mensual ya calculados por el
repositorio, devuelve bytes del PDF. Replica las mismas tarjetas y columnas
que ChargeOffsTab en el frontend.
"""
from __future__ import annotations

from html import escape

from weasyprint import HTML

_POSITIVE = "#1D9E75"
_NEGATIVE = "#A32D2D"


def _money(value) -> str:
    return f"${float(value):,.2f}"


def _pct(value) -> str:
    return f"{float(value):.2f}%"


def _delta_html(delta: dict, fmt: str) -> str:
    val = float(delta["value"])
    pct = float(delta["pct"])
    positive = val >= 0
    sign = "+" if positive else ""
    color = _POSITIVE if positive else _NEGATIVE
    formatted = _money(val) if fmt == "currency" else f"{val:,.0f}"
    return (
        f'<span style="color:{color};">{sign}{formatted} ({sign}{pct:.1f}%) vs año anterior</span>'
    )


def _kpi_card(
    label: str, value: str, delta: dict, delta_fmt: str, mtd_label: str, mtd_value: str
) -> str:
    return f"""<div class="kpi">
      <div class="label">{escape(label)}</div>
      <div class="value">{escape(value)}</div>
      <div class="kpi-delta">{_delta_html(delta, delta_fmt)}</div>
      <div class="kpi-mtd">{escape(mtd_label)}: <b>{escape(mtd_value)}</b></div>
    </div>"""


def _ratio_card(label: str, value: str, disabled: bool = False, hint: str | None = None) -> str:
    cls = "ratio disabled" if disabled else "ratio"
    hint_html = f'<div class="ratio-hint">{escape(hint)}</div>' if disabled and hint else ""
    return f"""<div class="{cls}">
      <div class="label">{escape(label)}</div>
      <div class="value">{escape(value)}</div>
      {hint_html}
    </div>"""


def _monthly_row(m: dict) -> str:
    principal = _money(m["principal_balance"]) if m["principal_balance"] is not None else "—"
    gross = _pct(m["gross_co_ratio"]) if m["gross_co_ratio"] is not None else "—"
    mob = f"{float(m['months_on_book']):.1f}" if m.get("months_on_book") is not None else "—"
    return f"""<tr>
      <td>{escape(m['month_name'])}</td>
      <td class="num">{principal}</td>
      <td class="num">{_money(m['original_balance'])}</td>
      <td class="num">{m['count']}</td>
      <td class="num">{_money(m['current_balance'])}</td>
      <td class="num">{_money(m['recovery_acv'])}</td>
      <td class="num">{_pct(m['recovery_ratio'])}</td>
      <td class="num">{gross}</td>
      <td class="num">{mob}</td>
    </tr>"""


_CSS = """
@page { size: A4 landscape; margin: 1.4cm; }
* { box-sizing: border-box; }
body { font-family: 'DejaVu Sans', Arial, sans-serif; color: #1a1a1a; margin: 0; }
h1 { font-size: 20px; margin: 0 0 2px; color: #111827; }
.subtitle { font-size: 11px; color: #6b7280; margin: 0 0 16px; }
.kpis { display: flex; gap: 10px; margin-bottom: 14px; }
.kpi { flex: 1; border: 1px solid #e5e7eb; border-top: 3px solid #534AB7; border-radius: 6px; padding: 10px 12px; }
.kpi .label { font-size: 9px; font-weight: bold; color: #6b7280; text-transform: uppercase; letter-spacing: .03em; }
.kpi .value { font-size: 18px; font-weight: bold; margin-top: 4px; }
.kpi-delta { font-size: 9px; margin-top: 4px; }
.kpi-mtd { font-size: 9px; color: #6b7280; margin-top: 6px; border-top: 1px solid #f0f0f0; padding-top: 6px; }
.ratios { display: flex; gap: 10px; margin-bottom: 20px; }
.ratio { flex: 1; border: 1px solid #e5e7eb; border-radius: 6px; padding: 10px 12px; text-align: center; }
.ratio.disabled { opacity: 0.5; }
.ratio .label { font-size: 9px; font-weight: bold; color: #6b7280; text-transform: uppercase; letter-spacing: .03em; }
.ratio .value { font-size: 16px; font-weight: bold; margin-top: 4px; }
.ratio-hint { font-size: 8px; color: #9ca3af; margin-top: 4px; }
.detail-title { font-size: 13px; font-weight: bold; margin: 0 0 8px; color: #111827; }
table { width: 100%; border-collapse: collapse; font-size: 9px; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th { background: #111827; color: #fff; text-align: left; padding: 6px 8px; font-size: 8.5px; text-transform: uppercase; }
th.num, td.num { text-align: right; }
td { padding: 5px 8px; border-bottom: 1px solid #f0f0f0; }
tbody tr:nth-child(even) { background: #fafafa; }
tfoot td { font-weight: bold; border-top: 2px solid #111827; background: #f9fafb; }
"""


def build_charge_off_overview_pdf(overview: dict, monthly: list[dict]) -> bytes:
    year = overview["year"]

    kpis_html = "".join([
        _kpi_card(
            "YTD Total C/O", _money(overview["ytd_total_charge_off"]),
            overview["delta_total_charge_off"], "currency",
            "MTD Total C/O", _money(overview["mtd_total_charge_off"]),
        ),
        _kpi_card(
            "YTD Avg Prin Bal C/O", _money(overview["ytd_avg_prin_bal"]),
            overview["delta_avg_prin_bal"], "currency",
            "MTD Avg Prin Bal C/O", _money(overview["mtd_avg_prin_bal"]),
        ),
        _kpi_card(
            "YTD # of C/O's", f"{overview['ytd_count']:,}",
            overview["delta_count"], "number",
            "MTD # of C/O", f"{overview['mtd_count']:,}",
        ),
    ])

    has_portfolio = overview["has_portfolio_data"]
    hint = "Requiere snapshot de cartera del período"
    ratios_html = "".join([
        _ratio_card("Recovery Ratio", _pct(overview["recovery_ratio"])),
        _ratio_card(
            "Gross C/O Ratio", _pct(overview["gross_co_ratio"]),
            disabled=not has_portfolio, hint=hint,
        ),
        _ratio_card(
            "Annualized C/O Ratio", _pct(overview["annualized_co_ratio"]),
            disabled=not has_portfolio, hint=hint,
        ),
    ])

    rows_html = "".join(_monthly_row(m) for m in monthly) or (
        "<tr><td colspan='9'>Sin datos para este año.</td></tr>"
    )

    total_count = sum(m["count"] for m in monthly)
    total_original = sum(float(m["original_balance"]) for m in monthly)
    total_current = sum(float(m["current_balance"]) for m in monthly)
    total_recovery = sum(float(m["recovery_acv"]) for m in monthly)
    total_recovery_ratio = (total_recovery / total_original * 100) if total_original else 0

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{_CSS}</style>
</head>
<body>
  <h1>Charge Off Overview — Automania</h1>
  <p class="subtitle">Año {year} — Datos de IDMS</p>

  <div class="kpis">{kpis_html}</div>
  <div class="ratios">{ratios_html}</div>

  <p class="detail-title">Resumen mensual — {year}</p>
  <table>
    <thead>
      <tr>
        <th>Month End</th><th class="num">Month End Principal Bal</th>
        <th class="num">Original C/O Balance</th><th class="num">Units Charged Off</th>
        <th class="num">Total Charge Off Balance</th><th class="num">Recovery ACV</th>
        <th class="num">Recovery Ratio</th><th class="num">Gross C/O Ratio</th>
        <th class="num">Months On Book</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
    <tfoot>
      <tr>
        <td>Totales</td><td class="num">—</td>
        <td class="num">{_money(total_original)}</td><td class="num">{total_count}</td>
        <td class="num">{_money(total_current)}</td><td class="num">{_money(total_recovery)}</td>
        <td class="num">{total_recovery_ratio:.2f}%</td><td class="num">—</td><td class="num">—</td>
      </tr>
    </tfoot>
  </table>
</body>
</html>"""

    return HTML(string=html).write_pdf()
