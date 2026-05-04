import { useState } from 'react'
import { defaultRange, formatImportedAt } from '@/lib/dateRange'
import { useHours } from '@/viewmodels/useHours'
import DateRangePicker from '@/components/ui/DateRangePicker'
import KpiCard from '@/components/ui/KpiCard'
import Spinner from '@/components/ui/Spinner'
import EmptyState from '@/components/ui/EmptyState'
import DataTable from '@/components/ui/DataTable'
import type { Column } from '@/components/ui/DataTable'
import EfficiencyGauges from '@/components/charts/EfficiencyGauges'
import { ChartHeader } from '@/components/ui/HelpTooltip'
import type { HoursSummary } from '@/types/hours'

const USD = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

const COLUMNS: Column<HoursSummary>[] = [
  { key: 'period_start', header: 'Period Start' },
  { key: 'period_end', header: 'Period End' },
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
    key: 'advisor_efficiency',
    header: 'Advisor Eff.',
    render: (r) => `${parseFloat(r.advisor_efficiency).toFixed(1)}%`,
    className: 'text-right',
  },
  {
    key: 'technician_proficiency',
    header: 'Tech Prof.',
    render: (r) => `${parseFloat(r.technician_proficiency).toFixed(1)}%`,
    className: 'text-right',
  },
]

export default function HoursDashboard() {
  const [range, setRange] = useState(defaultRange)
  const { kpis, list, isLoading } = useHours(range)

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
          <h1 className="text-xl font-bold text-gray-900">Hours</h1>
          <p className="text-sm text-gray-500 mt-0.5">Shop efficiency and technician proficiency</p>
        </div>
        <div className="flex items-center gap-4">
          {kpis?.imported_at && (
            <span className="text-xs text-gray-400 whitespace-nowrap">
              Actualizado: {formatImportedAt(kpis.imported_at)}
            </span>
          )}
          <DateRangePicker value={range} onChange={setRange} />
        </div>
      </div>

      {kpis ? (
        <>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <KpiCard 
              label="Labor Revenue" 
              value={kpis.labor_dollars} 
              format="currency"
              help={{
                title: "Labor Revenue",
                description: "Ingresos totales por mano de obra vendida.",
                examples: ["$36,977 = ingresos por labor durante el período"]
              }}
            />
            <KpiCard 
              label="Hours Sold" 
              value={kpis.hours_sold} 
              format="number"
              help={{
                title: "Hours Sold",
                description: "Total de horas vendidas al cliente. Métrica de productividad de ventas.",
                examples: ["385.20h = horas que se facturaron al cliente"]
              }}
            />
            <KpiCard 
              label="Hours Paid" 
              value={kpis.hours_paid} 
              format="number"
              help={{
                title: "Hours Paid",
                description: "Total de horas pagadas a los técnicos.",
                examples: ["475h = horas pagadas a técnicos"]
              }}
            />
            <KpiCard 
              label="Hours Worked" 
              value={kpis.hours_worked} 
              format="number"
              help={{
                title: "Hours Worked",
                description: "Total de horas realmente trabajadas.",
                examples: ["1,094.53h = horas totales trabajadas"]
              }}
            />
          </div>

          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <ChartHeader
              title="Efficiency & Proficiency"
              help={{
                title: "Eficiencia y Proficiency",
                description: "Tres métricas clave de eficiencia operativa: Advisor Efficiency (venta), Technician Proficiency (trabajo) y Technician Productivity (ejecución).",
                examples: [
                  "Advisor Efficiency 81% = se vendieron 81 horas de cada 100 pagadas",
                  "Technician Proficiency 43% = se trabajaron 43 horas reales de cada 100 pagadas",
                  "Altos valores = mejor rentabilidad"
                ]
              }}
            />
            <EfficiencyGauges kpis={kpis} />
          </div>
        </>
      ) : (
        <EmptyState title="No hours data" description="Import an hours summary report to see KPIs." />
      )}

      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <ChartHeader
          title="Period Records"
          help={{
            title: "Registros por Período",
            description: "Histórico de eficiencia y proficiency por cada período de reporte importado.",
            examples: [
              "Ver cómo evolucionan las métricas a lo largo del tiempo"
            ]
          }}
        />
        {list && list.length > 0 ? (
          <DataTable columns={COLUMNS} data={list} pageSize={10} />
        ) : (
          <EmptyState title="No records" description="No hours data for the selected period." />
        )}
      </div>
    </div>
  )
}
