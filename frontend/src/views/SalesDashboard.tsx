import { useState } from 'react'
import { defaultRange, formatImportedAt } from '@/lib/dateRange'
import { useSales } from '@/viewmodels/useSales'
import DateRangePicker from '@/components/ui/DateRangePicker'
import KpiCard from '@/components/ui/KpiCard'
import Spinner from '@/components/ui/Spinner'
import EmptyState from '@/components/ui/EmptyState'
import DataTable from '@/components/ui/DataTable'
import type { Column } from '@/components/ui/DataTable'
import DailySalesTrendChart from '@/components/charts/DailySalesTrendChart'
import DayOfWeekChart from '@/components/charts/DayOfWeekChart'
import { ChartHeader } from '@/components/ui/HelpTooltip'
import type { DailySales } from '@/types/sales'

const USD = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

const COLUMNS: Column<DailySales>[] = [
  { key: 'date', header: 'Date' },
  { key: 'day_of_week', header: 'Day' },
  {
    key: 'total_cars',
    header: 'Cars',
    render: (r) => r.total_cars,
    className: 'text-right',
  },
  {
    key: 'gross_sales',
    header: 'Gross Sales',
    render: (r) => USD.format(parseFloat(r.gross_sales)),
    className: 'text-right',
  },
  {
    key: 'gross_profit',
    header: 'Gross Profit',
    render: (r) => USD.format(parseFloat(r.gross_profit)),
    className: 'text-right',
  },
  {
    key: 'gross_profit_pct',
    header: 'Profit %',
    render: (r) => `${parseFloat(r.gross_profit_pct).toFixed(1)}%`,
    className: 'text-right',
  },
  {
    key: 'ticket_average',
    header: 'Avg Ticket',
    render: (r) => USD.format(parseFloat(r.ticket_average)),
    className: 'text-right',
  },
]

export default function SalesDashboard() {
  const [range, setRange] = useState(defaultRange)
  const { kpis, trend, dayOfWeek, list, isLoading } = useSales(range)

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
          <h1 className="text-xl font-bold text-gray-900">Sales</h1>
          <p className="text-sm text-gray-500 mt-0.5">Daily sales performance and trends</p>
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
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          <KpiCard 
            label="Total Cars" 
            value={kpis.total_cars} 
            format="number"
            help={{
              title: "Total Cars",
              description: "Número total de vehículos atendidos en el período seleccionado.",
              examples: ["150 cars = 150 vehículos diferentes pasaron por el taller"]
            }}
          />
          <KpiCard 
            label="Gross Sales" 
            value={kpis.total_gross} 
            format="currency"
            help={{
              title: "Gross Sales",
              description: "Ingresos totales antes de deducir costos. Incluye mano de obra y partes.",
              examples: ["$45,000 = total facturado por servicios"]
            }}
          />
          <KpiCard 
            label="Net Sales" 
            value={kpis.total_net} 
            format="currency"
            help={{
              title: "Net Sales",
              description: "Ventas netas después de devoluciones y ajustes.",
              examples: ["$44,500 = ventas efectivas realizadas"]
            }}
          />
          <KpiCard 
            label="Avg Ticket" 
            value={kpis.avg_ticket} 
            format="currency"
            help={{
              title: "Average Ticket",
              description: "Ticket promedio por vehículo. Indica el gasto medio por cliente.",
              examples: ["$300 ticket promedio = cada auto gasta $300 en promedio"]
            }}
          />
          <KpiCard 
            label="Gross Profit" 
            value={kpis.total_profit} 
            format="currency"
            help={{
              title: "Gross Profit",
              description: "Ganancia bruta después de restar costo de partes.",
              examples: ["$12,000 de ganancia bruta sobre $45,000 de ventas"]
            }}
          />
          <KpiCard 
            label="Profit %" 
            value={kpis.profit_pct} 
            format="percent"
            help={{
              title: "Profit Percentage",
              description: "Porcentaje de ganancia bruta sobre ventas totales.",
              examples: ["26.7% = por cada $100, $26.70 son ganancia"]
            }}
          />
        </div>
      ) : (
        <EmptyState title="No sales data" description="Import a daily sales report to see KPIs." />
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <ChartHeader
            title="Daily Trend"
            help={{
              title: "Tendencia de Ventas Diarias",
              description: "Evolución diaria de ventas brutas. Identifica patrones, picos de demanda y tendencias.",
              examples: [
                "Picos los viernes = más trabajo de fin de semana",
                "Caídas los lunes = menor actividad",
                "Tendencia ascendente = crecimiento del negocio"
              ]
            }}
          />
          {trend && trend.length > 0 ? (
            <DailySalesTrendChart data={trend} />
          ) : (
            <EmptyState title="No trend data" />
          )}
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <ChartHeader
            title="Avg Gross by Day of Week"
            help={{
              title: "Promedio de Ventas por Día de la Semana",
              description: "Muestra cuál es el día de la semana con mayor promedio de ventas. Útil para planificación de personal y recursos.",
              examples: [
                "Viernes: $3,500 promedio = es el día más activo",
                "Lunes: $1,800 promedio = menos demanda"
              ]
            }}
          />
          {dayOfWeek && dayOfWeek.length > 0 ? (
            <DayOfWeekChart data={dayOfWeek} />
          ) : (
            <EmptyState title="No day-of-week data" />
          )}
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <h2 className="mb-4 text-sm font-semibold text-gray-700">Daily Breakdown</h2>
        {list && list.length > 0 ? (
          <DataTable columns={COLUMNS} data={list} pageSize={15} />
        ) : (
          <EmptyState title="No records" description="No sales data for the selected period." />
        )}
      </div>
    </div>
  )
}
