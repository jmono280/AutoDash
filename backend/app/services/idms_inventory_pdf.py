"""Reporte de inventario en PDF (WeasyPrint) — resumen + detalle completo.

Función pura: recibe filas + agregados ya calculados, devuelve bytes del PDF.
Los colores replican los de IdmsDashboard.tsx (mismo hash) para que el chip de
un canal se vea del mismo color en la UI, el Excel y este PDF.
"""
from __future__ import annotations

from html import escape

from weasyprint import HTML

from app.models.idms_inventory import IdmsInventory

_FLAG_PALETTE = [
    "#534AB7", "#1D9E75", "#378ADD", "#BA7517", "#A32D2D",
    "#0E7490", "#C2410C", "#7C3AED", "#0F766E", "#BE185D",
]
_AGING_COLORS = {
    "0-7d": "#1D9E75",
    "8-14d": "#378ADD",
    "15-30d": "#534AB7",
    "31-60d": "#BA7517",
    "60+d": "#A32D2D",
}


def _flag_color(flag: str) -> str:
    h = 0
    for ch in flag:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return _FLAG_PALETTE[h % len(_FLAG_PALETTE)]


def _vehicle_label(row: IdmsInventory) -> str:
    model_trim = (row.model_trim or "").replace("/", " / ") or None
    desc = " ".join(p for p in (row.vehicle_year, row.make, model_trim) if p)
    return f"{row.stock_number or '—'} – {desc}" if desc else (row.stock_number or "—")


def _channel_breakdown(rows: list[IdmsInventory]) -> list[tuple[str, list[str]]]:
    """Agrupa por canal las descripciones de vehículo, ordenado por # unidades."""
    grouped: dict[str, list[str]] = {}
    for row in rows:
        if not row.inventory_flags:
            continue
        label = _vehicle_label(row)
        for flag in row.inventory_flags.split(","):
            flag = flag.strip()
            if flag:
                grouped.setdefault(flag, []).append(label)
    return sorted(grouped.items(), key=lambda kv: len(kv[1]), reverse=True)


def _money(value) -> str:
    return f"${float(value):,.2f}"


def _bar_row(label: str, value: int, max_value: int, color: str) -> str:
    pct = round((value / max_value) * 100, 1) if max_value else 0
    return f"""<div class="bar-row">
      <span class="bar-label">{escape(label)}</span>
      <div class="bar-track"><div class="bar-fill" style="width:{pct}%;background:{color};"></div></div>
      <span class="bar-value">{value}</span>
    </div>"""


def _channel_block(name: str, labels: list[str], color: str) -> str:
    items = "".join(f"<li>{escape(label)}</li>" for label in labels)
    return f"""<div class="channel-block">
      <div class="channel-header">
        <span class="channel-dot" style="background:{color};"></span>
        <span class="channel-name">{escape(name)}</span>
        <span class="channel-count">({len(labels)})</span>
      </div>
      <ul class="channel-list">{items}</ul>
    </div>"""


def _detail_row(r: IdmsInventory) -> str:
    return f"""<tr>
      <td>{escape(r.stock_number or '')}</td>
      <td>{escape(r.vehicle_year or '')}</td>
      <td>{escape(r.make or '')}</td>
      <td>{escape(r.model_trim or '')}</td>
      <td>{escape(r.exterior_color or '')}</td>
      <td>{escape(r.vin_last6 or '')}</td>
      <td>{r.mileage if r.mileage is not None else ''}</td>
      <td>{escape(r.status or '')}</td>
      <td>{escape(r.alternate_lot or '')}</td>
      <td>{r.acq_date.strftime('%m/%d/%Y') if r.acq_date else ''}</td>
      <td>{r.dol if r.dol is not None else ''}</td>
      <td>{_money(r.price)}</td>
      <td>{_money(r.wholesale_price)}</td>
      <td>{escape(r.inventory_flags or '')}</td>
    </tr>"""


_CSS = """
@page { size: A4 landscape; margin: 1.4cm; }
* { box-sizing: border-box; }
body { font-family: 'DejaVu Sans', Arial, sans-serif; color: #1a1a1a; margin: 0; }
h1 { font-size: 20px; margin: 0 0 2px; color: #111827; }
.subtitle { font-size: 11px; color: #6b7280; margin: 0 0 16px; }
.kpis { display: flex; gap: 10px; margin-bottom: 20px; }
.kpi { flex: 1; border: 1px solid #e5e7eb; border-top: 3px solid #534AB7; border-radius: 6px; padding: 10px 12px; }
.kpi .label { font-size: 9px; font-weight: bold; color: #6b7280; text-transform: uppercase; letter-spacing: .03em; }
.kpi .value { font-size: 18px; font-weight: bold; margin-top: 4px; }
.section { border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px 14px; margin-bottom: 14px; }
.section h2 { font-size: 12px; margin: 0 0 10px; color: #111827; }
.bar-row { display: flex; align-items: center; gap: 8px; font-size: 10px; margin-bottom: 4px; }
.bar-label { width: 90px; flex-shrink: 0; color: #374151; font-weight: bold; }
.bar-track { flex: 1; background: #f3f4f6; border-radius: 4px; height: 12px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 4px; }
.bar-value { width: 28px; text-align: right; font-weight: bold; flex-shrink: 0; }
.channels-columns { column-count: 3; column-gap: 20px; }
.channel-block { padding: 8px 0; border-bottom: 1px solid #e5e7eb; break-inside: avoid; }
.channel-block:last-child { border-bottom: none; padding-bottom: 0; }
.channel-header { display: flex; align-items: center; gap: 6px; font-size: 11px; margin-bottom: 4px; }
.channel-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.channel-name { font-weight: bold; color: #111827; }
.channel-count { color: #6b7280; }
.channel-list { list-style: none; margin: 0; padding: 0 0 0 15px; }
.channel-list li { position: relative; font-size: 8px; color: #4b5563; line-height: 1.7; }
.channel-list li::before { content: "•"; position: absolute; left: -12px; color: #9ca3af; }
.detail-title { font-size: 13px; font-weight: bold; margin: 0 0 8px; color: #111827; }
table { width: 100%; border-collapse: collapse; font-size: 8.5px; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th { background: #111827; color: #fff; text-align: left; padding: 5px 6px; font-size: 8px; text-transform: uppercase; }
td { padding: 4px 6px; border-bottom: 1px solid #f0f0f0; }
tbody tr:nth-child(even) { background: #fafafa; }
"""


def build_inventory_pdf(rows: list[IdmsInventory], kpis: dict, aging: list[dict]) -> bytes:
    channels = _channel_breakdown(rows)
    max_aging = max((b["count"] for b in aging), default=1)

    aging_bars = "".join(
        _bar_row(b["bucket"], b["count"], max_aging, _AGING_COLORS.get(b["bucket"], "#534AB7"))
        for b in aging
    ) or "<p>Sin datos.</p>"
    channel_blocks = "".join(
        _channel_block(name, labels, _flag_color(name)) for name, labels in channels
    ) or "<p>Sin datos.</p>"

    detail_rows = "".join(_detail_row(r) for r in rows)
    snapshot = kpis.get("snapshot_date")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{_CSS}</style>
</head>
<body>
  <h1>Reporte de Inventario — Automania</h1>
  <p class="subtitle">Snapshot: {snapshot if snapshot else '—'}</p>

  <div class="kpis">
    <div class="kpi"><div class="label">Unidades</div><div class="value">{kpis['count']}</div></div>
    <div class="kpi"><div class="label">Asking Price Total</div><div class="value">{_money(kpis['total_price'])}</div></div>
    <div class="kpi"><div class="label">Wholesale Total</div><div class="value">{_money(kpis['total_wholesale'])}</div></div>
    <div class="kpi"><div class="label">DOL Promedio</div><div class="value">{kpis['avg_dol']:.1f}</div></div>
    <div class="kpi"><div class="label">DOL Máximo</div><div class="value">{kpis['max_dol']}</div></div>
  </div>

  <div class="section">
    <h2>Antigüedad en lote (DOL)</h2>
    {aging_bars}
  </div>

  <div class="section">
    <h2>Publicado en (canales)</h2>
    <div class="channels-columns">{channel_blocks}</div>
  </div>

  <p class="detail-title">Detalle de inventario ({len(rows)} unidades)</p>
  <table>
    <thead>
      <tr>
        <th>Stock #</th><th>Year</th><th>Make</th><th>Model/Trim</th><th>Color</th>
        <th>VIN Last 6</th><th>Mileage</th><th>Status</th><th>Alternate Lot</th>
        <th>Acquired</th><th>DOL</th><th>Asking Price</th><th>Wholesale $</th><th>Flags</th>
      </tr>
    </thead>
    <tbody>
      {detail_rows}
    </tbody>
  </table>
</body>
</html>"""

    return HTML(string=html).write_pdf()
