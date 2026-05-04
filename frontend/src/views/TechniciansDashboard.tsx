import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { defaultRange, formatImportedAt } from '@/lib/dateRange'
import { useTechnicians } from '@/viewmodels/useTechnicians'
import DateRangePicker from '@/components/ui/DateRangePicker'
import Spinner from '@/components/ui/Spinner'
import EmptyState from '@/components/ui/EmptyState'
import DataTable from '@/components/ui/DataTable'
import type { Column } from '@/components/ui/DataTable'
import TechnicianRankingChart from '@/components/charts/TechnicianRankingChart'
import { ChartHeader } from '@/components/ui/HelpTooltip'
import type { Technician, TechnicianMetric } from '@/types/technician'

const USD = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

const METRICS: { value: TechnicianMetric; label: string }[] = [
  { value: 'hours_sold', label: 'Hours Sold' },
  { value: 'labor_dollars', label: 'Labor $' },
  { value: 'proficiency', label: 'Proficiency %' },
]

const COLUMNS: Column<Technician>[] = [
  { key: 'technician_name', header: 'Technician' },
  {
    key: 'labor_dollars',
    header: 'Labor $',
    render: (r) => USD.format(parseFloat(r.labor_dollars)),
    className: 'text-right',
  },
  {
    key: 'hours_sold',
    header: 'Hrs Sold',
    render: (r) => parseFloat(r.hours_sold).toFixed(2),
    className: 'text-right',
  },
  {
    key: 'hours_paid',
    header: 'Hrs Paid',
    render: (r) => parseFloat(r.hours_paid).toFixed(2),
    className: 'text-right',
  },
  {
    key: 'technician_proficiency',
    header: 'Proficiency',
    render: (r) =>
      r.technician_proficiency != null
        ? `${parseFloat(r.technician_proficiency).toFixed(1)}%`
        : '—',
    className: 'text-right',
  },
  {
    key: 'technician_productivity',
    header: 'Productivity',
    render: (r) =>
      r.technician_productivity != null
        ? `${parseFloat(r.technician_productivity).toFixed(1)}%`
        : '—',
    className: 'text-right',
  },
]

export default function TechniciansDashboard() {
  const [range, setRange] = useState(defaultRange)
  const navigate = useNavigate()
  const { technicians, ranking, metric, setMetric, isLoading } = useTechnicians(range)

  const techImportedAt = technicians?.reduce<string | null>((max, t) =>
    !max || t.imported_at > max ? t.imported_at : max, null) ?? null

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Technicians</h1>
          <p className="text-sm text-gray-500 mt-0.5">Individual performance and rankings</p>
        </div>
        <div className="flex items-center gap-4">
          {techImportedAt && (
            <span className="text-xs text-gray-400 whitespace-nowrap">
              Actualizado: {formatImportedAt(techImportedAt)}
            </span>
          )}
          <DateRangePicker value={range} onChange={setRange} />
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <div className="mb-4 flex items-center justify-between">
          <ChartHeader
            title="Ranking"
            help={{
              title: "Ranking de Técnicos",
              description: "Clasifica técnicos según la métrica seleccionada: Horas Vendidas, Labor $ o Proficiency %.",
              examples: [
                "Hours Sold: Técnicos que más ingresos generan",
                "Labor $: Dólares totales vendidos por técnico",
                "Proficiency %: Eficiencia en convertir horas vendidas a trabajo realizado"
              ]
            }}
          />
          <div className="flex gap-1">
            {METRICS.map((m) => (
              <button
                key={m.value}
                onClick={() => setMetric(m.value)}
                className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${
                  metric === m.value
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {m.label}
              </button>
            ))}
          </div>
        </div>
        {ranking && ranking.length > 0 ? (
          <TechnicianRankingChart ranking={ranking} />
        ) : (
          <EmptyState title="No ranking data" description="Import hours detail to see technician rankings." />
        )}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <ChartHeader
          title="All Technicians"
          help={{
            title: "Tabla de Todos los Técnicos",
            description: "Lista completa de técnicos con todas sus métricas de performance. Clickea una fila para ver detalles detallados.",
            examples: [
              "Hours Sold: Horas facturadas al cliente",
              "Proficiency: Calidad del trabajo realizado"
            ]
          }}
        />
        {technicians && technicians.length > 0 ? (
          <DataTable
            columns={COLUMNS}
            data={technicians}
            pageSize={15}
            onRowClick={(row) => navigate(`/technicians/${encodeURIComponent(row.technician_name)}`)}
          />
        ) : (
          <EmptyState title="No technician records" description="Import hours detail for the selected period." />
        )}
      </div>
    </div>
  )
}
