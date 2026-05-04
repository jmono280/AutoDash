import { useState } from 'react'
import { formatImportedAt } from '@/lib/dateRange'
import { useWip } from '@/viewmodels/useWip'
import KpiCard from '@/components/ui/KpiCard'
import Spinner from '@/components/ui/Spinner'
import EmptyState from '@/components/ui/EmptyState'
import DataTable from '@/components/ui/DataTable'
import type { Column } from '@/components/ui/DataTable'
import WipAgingChart from '@/components/charts/WipAgingChart'
import CategoryPieChart from '@/components/charts/CategoryPieChart'
import AdvisorBarChart from '@/components/charts/AdvisorBarChart'
import { ChartHeader } from '@/components/ui/HelpTooltip'
import type { Wip } from '@/types/wip'

const USD = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

const COLUMNS: Column<Wip>[] = [
  { key: 'ro_number', header: 'RO #' },
  { key: 'customer', header: 'Customer' },
  { key: 'vehicle', header: 'Vehicle' },
  { key: 'advisor', header: 'Advisor', render: (r) => r.advisor ?? '—' },
  { key: 'category', header: 'Category' },
  {
    key: 'days_open',
    header: 'Days Open',
    render: (r) => (
      <span
        className={
          r.days_open > 30
            ? 'font-semibold text-red-600'
            : r.days_open > 14
              ? 'text-amber-600'
              : 'text-gray-700'
        }
      >
        {r.days_open}
      </span>
    ),
    className: 'text-right',
  },
  {
    key: 'estimated',
    header: 'Estimated',
    render: (r) => (r.estimated != null ? USD.format(parseFloat(r.estimated)) : '—'),
    className: 'text-right',
  },
  {
    key: 'cog',
    header: 'COG',
    render: (r) => USD.format(parseFloat(r.cog)),
    className: 'text-right',
  },
]

export default function WorkInProgressDashboard() {
  const { kpis, aging, byCategory, byAdvisor, list, filters, setFilters, page, setPage, isLoading, isLoadingAll } =
    useWip()

  const [search, setSearch] = useState('')

  const filteredItems = list
    ? list.items.filter(
        (r) =>
          !search ||
          r.customer.toLowerCase().includes(search.toLowerCase()) ||
          r.ro_number.toLowerCase().includes(search.toLowerCase()) ||
          r.vehicle.toLowerCase().includes(search.toLowerCase()),
      )
    : []

  if (isLoadingAll && !kpis) {
    return (
      <div className="flex items-center justify-center py-32">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Work in Progress</h1>
          <p className="text-sm text-gray-500 mt-0.5">Live snapshot of all open repair orders</p>
        </div>
        {kpis?.imported_at && (
          <span className="text-xs text-gray-400 whitespace-nowrap mt-1">
            Actualizado: {formatImportedAt(kpis.imported_at)}
          </span>
        )}
      </div>

      {kpis ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <KpiCard 
            label="Open ROs" 
            value={kpis.total_ros} 
            format="number"
            help={{
              title: "Open Repair Orders",
              description: "Número total de órdenes de reparación actualmente abiertas en el taller.",
              examples: ["256 ROs = 256 trabajos sin completar"]
            }}
          />
          <KpiCard 
            label="Total Estimated" 
            value={kpis.total_estimated} 
            format="currency"
            help={{
              title: "Total Estimated",
              description: "Valor estimado total de todas las órdenes abiertas.",
              examples: ["$25,000 en trabajos estimados"]
            }}
          />
          <KpiCard 
            label="Avg Days Open" 
            value={kpis.avg_days_open} 
            format="number"
            help={{
              title: "Average Days Open",
              description: "Promedio de días que llevan abiertas las órdenes. Indicador de eficiencia del taller.",
              examples: ["11.15 días promedio = eficiencia normal", "Mayor a 20 = posible retrasos"]
            }}
          />
          <KpiCard
            label="Oldest RO"
            value={kpis.oldest_ro_days}
            format="number"
            deltaType={kpis.oldest_ro_days > 30 ? 'negative' : 'positive'}
            help={{
              title: "Oldest Repair Order",
              description: "Días que lleva abierta la orden más antigua. Alerta roja si supera 30 días.",
              examples: ["91 días = trabajo crítico, requiere acción inmediata"]
            }}
          />
        </div>
      ) : (
        <EmptyState title="No WIP data" description="Import a Work in Progress report to see KPIs." />
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <ChartHeader
            title="Aging Buckets"
            help={{
              title: "Distribución de Antigüedad",
              description: "Clasifica órdenes abiertas por tiempo transcurrido desde su apertura. Identifica trabajos atrasados.",
              examples: [
                "0-7d: Normal",
                "31-60d: Crítico",
                "60+d: Emergencia"
              ]
            }}
          />
          {aging && aging.length > 0 ? (
            <WipAgingChart aging={aging} />
          ) : (
            <EmptyState title="No aging data" />
          )}
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <ChartHeader
            title="By Category"
            help={{
              title: "Órdenes por Categoría",
              description: "Distribución de órdenes abiertas por tipo de reparación (Motor, Frenos, Transmisión, etc.)",
              examples: [
                "Engine: 45 órdenes",
                "Brakes: 32 órdenes"
              ]
            }}
          />
          {byCategory && byCategory.length > 0 ? (
            <CategoryPieChart data={byCategory} />
          ) : (
            <EmptyState title="No category data" />
          )}
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <ChartHeader
          title="By Advisor"
          help={{
            title: "Órdenes por Asesor",
            description: "Muestra la carga de trabajo de cada asesor. Útil para balancear la distribución de órdenes.",
            examples: [
              "Advisor A: 45 órdenes abiertas",
              "Advisor B: 32 órdenes abiertas"
            ]
          }}
        />
        {byAdvisor && byAdvisor.length > 0 ? (
          <AdvisorBarChart data={byAdvisor} />
        ) : (
          <EmptyState title="No advisor data" />
        )}
      </div>

      {/* Filters + table */}
      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <ChartHeader
            title="Open ROs"
            help={{
              title: "Tabla de Órdenes Abiertas",
              description: "Lista completa de todas las órdenes de reparación abiertas. Filtra por categoría, busca por RO/cliente/vehículo. Códigos de color por antigüedad.",
              examples: [
                "Rojo: Más de 30 días abierto (crítico)",
                "Ámbar: 14-30 días (atención moderada)",
                "Gris: Menos de 14 días (normal)"
              ]
            }}
          />
          <div className="flex flex-wrap gap-2">
            <input
              type="text"
              placeholder="Search RO, customer, vehicle…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 w-56"
            />
            <select
              value={filters.category ?? ''}
              onChange={(e) => setFilters({ ...filters, category: e.target.value || undefined })}
              className="rounded-md border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">All categories</option>
              {byCategory?.map((c) => (
                <option key={c.category} value={c.category}>
                  {c.category}
                </option>
              ))}
            </select>
            <select
              value={filters.advisor ?? ''}
              onChange={(e) => setFilters({ ...filters, advisor: e.target.value || undefined })}
              className="rounded-md border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">All advisors</option>
              {byAdvisor?.map((a) => (
                <option key={a.advisor ?? 'none'} value={a.advisor ?? ''}>
                  {a.advisor ?? 'Unassigned'}
                </option>
              ))}
            </select>
            {(filters.category || filters.advisor) && (
              <button
                onClick={() => setFilters({})}
                className="rounded-md border border-gray-200 px-3 py-1.5 text-sm text-gray-500 hover:bg-gray-50"
              >
                Clear filters
              </button>
            )}
          </div>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : filteredItems.length > 0 ? (
          <>
            <DataTable columns={COLUMNS} data={filteredItems} />
            {list && list.pages > 1 && (
              <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                <span>
                  Page {list.page} of {list.pages} · {list.total} total ROs
                </span>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(page - 1)}
                    disabled={page <= 1}
                    className="rounded border border-gray-200 px-3 py-1 hover:bg-gray-50 disabled:opacity-40"
                  >
                    ‹ Prev
                  </button>
                  <button
                    onClick={() => setPage(page + 1)}
                    disabled={page >= list.pages}
                    className="rounded border border-gray-200 px-3 py-1 hover:bg-gray-50 disabled:opacity-40"
                  >
                    Next ›
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <EmptyState
            title="No ROs found"
            description={search ? 'Try a different search term.' : 'Import a Work in Progress report.'}
          />
        )}
      </div>
    </div>
  )
}
