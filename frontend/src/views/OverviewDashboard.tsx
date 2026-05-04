import { useState } from 'react'
import { defaultRange, formatImportedAt } from '@/lib/dateRange'
import { useOverview } from '@/viewmodels/useOverview'
import { useTechnicians } from '@/viewmodels/useTechnicians'
import DateRangePicker from '@/components/ui/DateRangePicker'
import KpiCard from '@/components/ui/KpiCard'
import Spinner from '@/components/ui/Spinner'
import EmptyState from '@/components/ui/EmptyState'
import DailySalesTrendChart from '@/components/charts/DailySalesTrendChart'
import WipAgingChart from '@/components/charts/WipAgingChart'
import { ChartHeader } from '@/components/ui/HelpTooltip'

const USD = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

export default function OverviewDashboard() {
  const [range, setRange] = useState(defaultRange)

  const { salesKpis, hoursKpis, wipKpis, aging, salesTrend, isLoading } = useOverview(range)
  const { ranking } = useTechnicians(range)

  const rosOver30 = aging
    ? aging.filter((b) => b.bucket === '31-60d' || b.bucket === '60+d').reduce((s, b) => s + b.count, 0)
    : null

  const top3 = ranking?.slice(0, 3) ?? []

  const importDates = [salesKpis?.imported_at, hoursKpis?.imported_at, wipKpis?.imported_at]
    .filter((d): d is string => !!d)
    .sort()
  const latestImport = importDates.length > 0 ? importDates[importDates.length - 1] : null

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
          <h1 className="text-xl font-bold text-gray-900">Overview</h1>
          <p className="text-sm text-gray-500 mt-0.5">Executive summary across all operations</p>
        </div>
        <div className="flex items-center gap-4">
          {latestImport && (
            <span className="text-xs text-gray-400 whitespace-nowrap">
              Actualizado: {formatImportedAt(latestImport)}
            </span>
          )}
          <DateRangePicker value={range} onChange={setRange} />
        </div>
      </div>

      {/* KPI grid */}
      {salesKpis && hoursKpis && wipKpis ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          <KpiCard 
            label="Total Cars" 
            value={salesKpis.total_cars} 
            format="number"
            help={{
              title: "Total Cars",
              description: "Número total de vehículos atendidos en el período seleccionado.",
              examples: ["150 cars = 150 vehículos diferentes en el taller"]
            }}
          />
          <KpiCard 
            label="Gross Sales" 
            value={salesKpis.total_gross} 
            format="currency"
            help={{
              title: "Gross Sales",
              description: "Ingresos totales por ventas antes de deducir costos.",
              examples: ["$71,740 = total facturado"]
            }}
          />
          <KpiCard 
            label="Gross Profit" 
            value={salesKpis.total_profit} 
            format="currency"
            help={{
              title: "Gross Profit",
              description: "Ganancia bruta después de restar el costo de las partes vendidas.",
              examples: ["$45,447 = ganancia sobre $71,740 en ventas"]
            }}
          />
          <KpiCard 
            label="Profit %" 
            value={salesKpis.profit_pct} 
            format="percent"
            help={{
              title: "Profit Percentage",
              description: "Porcentaje de ganancia bruta sobre ventas totales.",
              examples: ["63.35% = por cada $100, $63.35 son ganancia"]
            }}
          />
          <KpiCard 
            label="Open ROs" 
            value={wipKpis.total_ros} 
            format="number"
            help={{
              title: "Open Repair Orders",
              description: "Número total de órdenes de reparación abiertas.",
              examples: ["256 ROs = trabajos sin completar"]
            }}
          />
          <KpiCard
            label="ROs >30d"
            value={rosOver30 ?? 0}
            format="number"
            deltaType={rosOver30 && rosOver30 > 0 ? 'negative' : 'positive'}
            help={{
              title: "ROs Over 30 Days",
              description: "Órdenes abiertas más de 30 días. Métrica crítica de eficiencia.",
              examples: ["3 ROs >30d = trabajos atrasados que afectan satisfacción del cliente"]
            }}
          />
        </div>
      ) : (
        <EmptyState title="No sales data" description="Import a daily sales report to see KPIs." />
      )}

      {/* Charts row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <ChartHeader
            title="Sales Trend"
            help={{
              title: "Tendencia de Ventas",
              description: "Evolución diaria de las ventas brutas. Identifica patrones, picos de demanda y tendencias de crecimiento.",
              examples: [
                "Picos los viernes = más trabajo de fin de semana",
                "Caídas los lunes = menor actividad",
                "Tendencia ascendente = negocio en crecimiento"
              ]
            }}
          />
          {salesTrend && salesTrend.length > 0 ? (
            <DailySalesTrendChart data={salesTrend} />
          ) : (
            <EmptyState title="No trend data" description="Import sales data for the selected period." />
          )}
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <ChartHeader
            title="WIP Aging"
            help={{
              title: "Antigüedad del Trabajo en Progreso",
              description: "Distribuye las órdenes de reparación abiertas por tiempo transcurrido. Identifica trabajos atrasados.",
              examples: [
                "0-7d: Trabajos recientes, flujo normal",
                "8-14d: Requieren atención moderada",
                "31-60d: Críticos, afectan satisfacción",
                "60+d: Emergencia, requiere acción inmediata"
              ]
            }}
          />
          {aging && aging.length > 0 ? (
            <WipAgingChart aging={aging} />
          ) : (
            <EmptyState title="No WIP data" description="Import a Work in Progress report." />
          )}
        </div>
      </div>

      {/* Top technicians */}
      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <ChartHeader
          title="Top 3 Technicians — Hours Sold"
          help={{
            title: "Top Técnicos por Horas Vendidas",
            description: "Ranking de los 3 técnicos con mayor cantidad de horas vendidas. Muestra capacidad de venta e ingresos.",
            examples: [
              "Joe Davis: 64.66h vendidas = más ingresos",
              "Proficiency 85% = eficiencia en convertir ventas a trabajo"
            ]
          }}
        />
        {top3.length > 0 ? (
          <div className="divide-y divide-gray-100">
            {top3.map((t, i) => (
              <div key={t.technician_name} className="flex items-center justify-between py-3">
                <div className="flex items-center gap-3">
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-purple-100 text-xs font-bold text-purple-700">
                    {i + 1}
                  </span>
                  <span className="text-sm font-medium text-gray-800">{t.technician_name}</span>
                </div>
                <div className="flex gap-6 text-sm text-gray-600">
                  <span>{parseFloat(t.hours_sold).toFixed(1)} h sold</span>
                  {t.technician_proficiency && (
                    <span className="text-purple-600 font-medium">
                      {parseFloat(t.technician_proficiency).toFixed(1)}% proficiency
                    </span>
                  )}
                  <span className="text-emerald-600 font-medium">{USD.format(parseFloat(t.labor_dollars))}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState title="No technician data" description="Import hours detail to see technician rankings." />
        )}
      </div>
    </div>
  )
}
