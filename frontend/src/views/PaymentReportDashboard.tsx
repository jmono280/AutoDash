import { useState } from 'react'
import { usePaymentReport } from '@/viewmodels/usePaymentReport'
import KpiCard from '@/components/ui/KpiCard'
import Spinner from '@/components/ui/Spinner'
import EmptyState from '@/components/ui/EmptyState'
import DataTable from '@/components/ui/DataTable'
import type { Column } from '@/components/ui/DataTable'
import PaymentByCollectorChart from '@/components/charts/PaymentByCollectorChart'
import PaymentMethodChart from '@/components/charts/PaymentMethodChart'
import type { CollectionStat, PaymentTransaction } from '@/types/paymentReport'

// ── helpers ───────────────────────────────────────────────────────────────────

function fmt$(val: string | undefined): string {
  if (!val) return '$0.00'
  return `$${parseFloat(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function fmtDate(iso: string): string {
  return iso.slice(0, 10)
}

function yesterdayStr(): string {
  const d = new Date()
  d.setDate(d.getDate() - 1)
  return d.toISOString().slice(0, 10)
}

// ── table columns ─────────────────────────────────────────────────────────────

const TX_COLUMNS: Column<PaymentTransaction>[] = [
  {
    key: 'payment_date',
    header: 'Fecha',
    render: (r) => <span className="text-xs text-gray-500">{fmtDate(r.payment_date)}</span>,
  },
  {
    key: 'customer_name',
    header: 'Cliente',
    render: (r) => <span className="font-medium text-gray-800">{r.customer_name}</span>,
  },
  {
    key: 'payment_method',
    header: 'Método',
    render: (r) => (
      <span className="text-xs font-medium px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">
        {r.payment_method ?? '—'} {r.card_last_4 ? `···${r.card_last_4}` : ''}
      </span>
    ),
  },
  {
    key: 'amount',
    header: 'Monto',
    className: 'text-right',
    render: (r) => <span className="font-medium text-gray-800">{fmt$(r.amount)}</span>,
  },
  {
    key: 'convenience_fee',
    header: 'Fee',
    className: 'text-right',
    render: (r) => <span className="text-xs text-gray-500">{fmt$(r.convenience_fee)}</span>,
  },
  {
    key: 'status',
    header: 'Status',
    render: (r) => (
      <span className={`text-xs font-medium ${r.status === 'PAID' ? 'text-emerald-600' : 'text-gray-500'}`}>
        {r.status ?? '—'}
      </span>
    ),
  },
  { key: 'collector', header: 'Cobrador', render: (r) => r.collector ?? '—' },
  {
    key: 'refund_amount',
    header: 'Refund',
    className: 'text-right',
    render: (r) =>
      r.refund_amount ? (
        <span className="text-amber-600 font-medium">{fmt$(r.refund_amount)}</span>
      ) : (
        <span className="text-gray-300">—</span>
      ),
  },
]

const CS_COLUMNS: Column<CollectionStat>[] = [
  {
    key: 'collector',
    header: 'Cobrador',
    render: (r) => <span className="font-medium text-gray-800">{r.collector}</span>,
  },
  {
    key: 'payments_count',
    header: 'Pagos',
    className: 'text-right',
    render: (r) => `${r.payments_count} · ${fmt$(r.payments_amount)}`,
  },
  { key: 'autopay_created',  header: 'Autopay',   className: 'text-right' },
  { key: 'promise_sent',     header: 'Prom. enviadas', className: 'text-right' },
  { key: 'promise_confirmed',header: 'Prom. conf.',    className: 'text-right' },
  { key: 'messages_sent',    header: 'Mensajes',  className: 'text-right' },
  {
    key: 'waived_fees_count',
    header: 'Fees Waived',
    className: 'text-right',
    render: (r) =>
      r.waived_fees_count > 0
        ? <span className="text-amber-600">{r.waived_fees_count} · {fmt$(r.waived_fees_amount)}</span>
        : <span className="text-gray-300">—</span>,
  },
  {
    key: 'period_start',
    header: 'Período',
    render: (r) => (
      <span className="text-xs text-gray-400">{r.period_start} – {r.period_end}</span>
    ),
  },
]

// ── component ─────────────────────────────────────────────────────────────────

export default function PaymentReportDashboard() {
  const {
    range,
    setRange,
    collectorFilter,
    setCollectorFilter,
    page,
    setPage,
    kpis,
    byCollector,
    byMethod,
    collectionStats,
    transactions,
    isLoading,
  } = usePaymentReport()

  const [viewFrom, setViewFrom] = useState(range.from)
  const [viewTo,   setViewTo]   = useState(range.to)

  function handleRangeChange(from: string, to: string) {
    setViewFrom(from)
    setViewTo(to)
    if (from && to) setRange({ from, to })
  }

  function handleYesterday() {
    const y = yesterdayStr()
    handleRangeChange(y, y)
  }

  return (
    <div className="space-y-6">
      {/* Título */}
      <div>
        <h1 className="text-xl font-bold text-gray-900">Payment Report</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Transacciones y estadísticas de cobranza
        </p>
      </div>

      {/* Selector de período */}
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
          onChange={(e) => handleRangeChange(e.target.value, viewTo)}
          className="border border-gray-300 rounded-md px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#ffea00]"
        />
        <span className="text-gray-400">–</span>
        <input
          type="date"
          value={viewTo}
          min={viewFrom}
          onChange={(e) => handleRangeChange(viewFrom, e.target.value)}
          className="border border-gray-300 rounded-md px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#ffea00]"
        />
      </div>

      {/* KPIs */}
      {isLoading && !kpis ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : kpis ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          <KpiCard label="Total pagos"  value={kpis.total_payments}  format="number" />
          <KpiCard label="Monto total"  value={parseFloat(kpis.total_amount)}  format="currency" />
          <KpiCard label="Fees"         value={parseFloat(kpis.total_fees)}    format="currency" />
          <KpiCard label="Cobrado"      value={parseFloat(kpis.total_collected)} format="currency" />
          <KpiCard label="Pago prom."   value={parseFloat(kpis.avg_payment_amount)} format="currency" />
          <KpiCard
            label="Refunds"
            value={parseFloat(kpis.total_refunds)}
            format="currency"
            deltaType={parseFloat(kpis.total_refunds) > 0 ? 'negative' : 'neutral'}
          />
        </div>
      ) : (
        <EmptyState
          title="Sin datos en este período"
          description="Importa un archivo payment report en Administración → Imports."
        />
      )}

      {/* Gráficas */}
      {(byCollector.length > 0 || byMethod.length > 0) && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {byCollector.length > 0 && (
            <div className="rounded-xl bg-gray-200 shadow-sm p-5">
              <h3 className="mb-4 text-sm font-semibold text-gray-700">Pagos por cobrador</h3>
              <PaymentByCollectorChart data={byCollector} />
            </div>
          )}
          {byMethod.length > 0 && (
            <div className="rounded-xl bg-gray-200 shadow-sm p-5">
              <h3 className="mb-4 text-sm font-semibold text-gray-700">Distribución por método de pago</h3>
              <PaymentMethodChart data={byMethod} />
            </div>
          )}
        </div>
      )}

      {/* Tabla: Collection Stats */}
      {collectionStats.length > 0 && (
        <div className="rounded-xl bg-gray-200 shadow-sm p-5">
          <h3 className="mb-4 text-sm font-semibold text-gray-700">Estadísticas de cobranza</h3>
          <DataTable columns={CS_COLUMNS} data={collectionStats} pageSize={collectionStats.length} />
        </div>
      )}

      {/* Tabla: Transacciones */}
      <div className="rounded-xl bg-gray-200 shadow-sm p-5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h3 className="text-sm font-semibold text-gray-700">Transacciones</h3>
          {byCollector.length > 0 && (
            <div className="flex items-center gap-2">
              <label className="text-xs text-gray-500">Cobrador:</label>
              <select
                value={collectorFilter}
                onChange={(e) => setCollectorFilter(e.target.value)}
                className="rounded-md border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#ffea00]"
              >
                <option value="">Todos</option>
                {byCollector.map((c) => (
                  <option key={c.collector} value={c.collector}>{c.collector}</option>
                ))}
              </select>
            </div>
          )}
        </div>

        {isLoading ? (
          <div className="flex justify-center py-8"><Spinner /></div>
        ) : (
          <>
            <DataTable
              columns={TX_COLUMNS}
              data={transactions?.items ?? []}
              pageSize={20}
              emptyText="No hay transacciones en este período."
            />
            {transactions && transactions.pages > 1 && (
              <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                <span>{transactions.total} registros · página {transactions.page} de {transactions.pages}</span>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(page - 1)}
                    disabled={page <= 1}
                    className="px-3 py-1.5 rounded-md bg-gray-100 hover:bg-gray-200 disabled:opacity-40 transition-colors"
                  >
                    ← Ant.
                  </button>
                  <button
                    onClick={() => setPage(page + 1)}
                    disabled={page >= transactions.pages}
                    className="px-3 py-1.5 rounded-md bg-gray-100 hover:bg-gray-200 disabled:opacity-40 transition-colors"
                  >
                    Sig. →
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
