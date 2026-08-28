import { useState } from 'react'
import { useCallAnalytics } from '@/viewmodels/useCallAnalytics'

import KpiCard from '@/components/ui/KpiCard'
import Spinner from '@/components/ui/Spinner'
import EmptyState from '@/components/ui/EmptyState'
import DataTable from '@/components/ui/DataTable'
import type { Column } from '@/components/ui/DataTable'
import CallsByExtensionChart from '@/components/charts/CallsByExtensionChart'
import CallsDistributionChart from '@/components/charts/CallsDistributionChart'
import type { CallAnalyticsRecord, IsoRange } from '@/types/callAnalytics'

// ── helpers ──────────────────────────────────────────────────────────────────

function fmtDuration(secs: number): string {
  if (secs === 0) return '0s'
  const h = Math.floor(secs / 3600)
  const m = Math.floor((secs % 3600) / 60)
  const s = secs % 60
  if (h > 0) return `${h}h ${m}m`
  if (m > 0) return `${m}m ${s}s`
  return `${s}s`
}

function dateToIsoRange(from: string, to: string): IsoRange {
  return {
    from: `${from}T00:00:00Z`,
    to:   `${to}T23:59:59Z`,
  }
}

function isoToDate(iso: string): string {
  return iso.slice(0, 10)
}

// ── table columns ─────────────────────────────────────────────────────────────

const COLUMNS: Column<CallAnalyticsRecord>[] = [
  {
    key: 'extension_name',
    header: 'Extensión',
    render: (r) => (
      <span className="font-medium text-gray-800">
        {r.extension_name}
        <span className="ml-1 text-xs text-gray-400">#{r.extension_number}</span>
      </span>
    ),
  },
  {
    key: 'time_from',
    header: 'Período',
    render: (r) => (
      <span className="text-xs text-gray-500">
        {isoToDate(r.time_from)} – {isoToDate(r.time_to)}
      </span>
    ),
  },
  { key: 'total_calls',  header: 'Total',    className: 'text-right' },
  { key: 'inbound',      header: 'Entrantes', className: 'text-right' },
  { key: 'outbound',     header: 'Salientes', className: 'text-right' },
  { key: 'answered',     header: 'Contest.',  className: 'text-right' },
  {
    key: 'not_answered',
    header: 'No Contest.',
    className: 'text-right',
    render: (r) => (
      <span className={r.not_answered > 0 ? 'text-amber-600 font-medium' : ''}>
        {r.not_answered}
      </span>
    ),
  },
  {
    key: 'abandoned',
    header: 'Abandon.',
    className: 'text-right',
    render: (r) => (
      <span className={r.abandoned > 0 ? 'text-red-600 font-medium' : ''}>{r.abandoned}</span>
    ),
  },
  { key: 'voicemail', header: 'Buzón', className: 'text-right' },
  {
    key: 'duration_seconds',
    header: 'Duración',
    className: 'text-right',
    render: (r) => fmtDuration(r.duration_seconds),
  },
]

// ── component ─────────────────────────────────────────────────────────────────

export default function CallAnalyticsDashboard() {
  const {
    kpis,
    byExtension,
    list,
    viewRange,
    setViewRange,
    extensionFilter,
    setExtensionFilter,
    isLoading,
  } = useCallAnalytics()

  // View range (YYYY-MM-DD)
  const [viewFrom, setViewFrom] = useState(isoToDate(viewRange.from))
  const [viewTo,   setViewTo]   = useState(isoToDate(viewRange.to))

  function handleViewRangeChange(from: string, to: string) {
    setViewFrom(from)
    setViewTo(to)
    if (from && to) setViewRange(dateToIsoRange(from, to))
  }

  function handleYesterday() {
    const d = new Date()
    d.setDate(d.getDate() - 1)
    const yesterday = d.toISOString().slice(0, 10)
    handleViewRangeChange(yesterday, yesterday)
  }

  return (
    <div className="space-y-6">
      {/* ── Título ─────────────────────────────────────────────────────────── */}
      <div>
        <h1 className="text-xl font-bold text-gray-900">Call Analytics</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Métricas de llamadas por extensión desde RingCentral
        </p>
      </div>

      {/* ── Selector de rango para visualizar ─────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-sm font-medium text-gray-600">Ver período:</span>
        <button
          onClick={handleYesterday}
          className="px-3 py-1.5 rounded-md text-sm font-medium bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
        >
          Ayer
        </button>
        <input
          type="date"
          value={viewFrom}
          onChange={(e) => handleViewRangeChange(e.target.value, viewTo)}
          className="border border-gray-300 rounded-md px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#ffea00]"
        />
        <span className="text-gray-400">–</span>
        <input
          type="date"
          value={viewTo}
          min={viewFrom}
          onChange={(e) => handleViewRangeChange(viewFrom, e.target.value)}
          className="border border-gray-300 rounded-md px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#ffea00]"
        />
      </div>

      {/* ── KPI cards ──────────────────────────────────────────────────────── */}
      {isLoading && !kpis ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : kpis ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          <KpiCard label="Total"       value={kpis.total_calls}        format="number" />
          <KpiCard label="Entrantes"   value={kpis.total_inbound}      format="number" />
          <KpiCard label="Salientes"   value={kpis.total_outbound}     format="number" />
          <KpiCard label="Contestadas" value={kpis.total_answered}     format="number" />
          <KpiCard
            label="No Contest."
            value={kpis.total_not_answered}
            format="number"
            deltaType={kpis.total_not_answered > 0 ? 'negative' : 'neutral'}
          />
          <KpiCard
            label="Abandonadas"
            value={kpis.total_abandoned}
            format="number"
            deltaType={kpis.total_abandoned > 0 ? 'negative' : 'neutral'}
          />
        </div>
      ) : (
        <EmptyState
          title="Sin datos en este período"
          description="Usa el panel de arriba para descargar datos desde RingCentral."
        />
      )}

      {/* ── Gráficas ───────────────────────────────────────────────────────── */}
      {byExtension.length > 0 && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="rounded-xl bg-gray-200 shadow-sm p-5">
            <h3 className="mb-4 text-sm font-semibold text-gray-700">
              Llamadas por extensión — Volumen
            </h3>
            <CallsByExtensionChart data={byExtension} />
          </div>

          <div className="rounded-xl bg-gray-200 shadow-sm p-5">
            <h3 className="mb-4 text-sm font-semibold text-gray-700">
              Resultado de llamadas por extensión
            </h3>
            <CallsDistributionChart data={byExtension} />
          </div>
        </div>
      )}

      {/* ── Tabla de registros ─────────────────────────────────────────────── */}
      <div className="rounded-xl bg-gray-200 shadow-sm p-5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h3 className="text-sm font-semibold text-gray-700">Registros detallados</h3>

          {byExtension.length > 0 && (
            <div className="flex items-center gap-2">
              <label className="text-xs text-gray-500">Extensión:</label>
              <select
                value={extensionFilter}
                onChange={(e) => setExtensionFilter(e.target.value)}
                className="rounded-md border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#ffea00]"
              >
                <option value="">Todas</option>
                {byExtension.map((ext) => (
                  <option key={ext.extension_number} value={ext.extension_number}>
                    {ext.extension_name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : (
          <DataTable
            columns={COLUMNS}
            data={list}
            pageSize={20}
            emptyText="No hay registros en este período."
          />
        )}
      </div>
    </div>
  )
}
