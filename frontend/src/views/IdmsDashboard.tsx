import { useState } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useIdms } from '@/viewmodels/useIdms'
import Spinner from '@/components/ui/Spinner'
import EmptyState from '@/components/ui/EmptyState'
import DataTable from '@/components/ui/DataTable'
import type { Column } from '@/components/ui/DataTable'
import type {
  IdmsChargeOff,
  IdmsChargeOffMonthlyDetail,
  IdmsDelta,
} from '@/types/idms'

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const currency = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
})
const numberFmt = new Intl.NumberFormat('en-US')

function n(val: string | number | null | undefined): number {
  if (val === null || val === undefined || val === '') return 0
  return typeof val === 'string' ? parseFloat(val) : val
}

function fmt$(val: string | number | null | undefined): string {
  return currency.format(n(val))
}

function fmtN(val: string | number | null | undefined): string {
  return numberFmt.format(n(val))
}

function fmtPct(val: string | number | null | undefined): string {
  return `${n(val).toFixed(2)}%`
}

function fmtDate(val: string | null): string {
  return val ? val.slice(0, 10) : '—'
}

// ── Tarjetas ─────────────────────────────────────────────────────────────────

interface OverviewCardProps {
  label: string
  value: string
  delta: IdmsDelta
  deltaFormat: 'currency' | 'number'
  mtdLabel: string
  mtdValue: string
}

/** Tarjeta del Overview: valor YTD, variación contra el año anterior y su MTD. */
function OverviewCard({
  label,
  value,
  delta,
  deltaFormat,
  mtdLabel,
  mtdValue,
}: OverviewCardProps) {
  const dv = n(delta.value)
  // En charge offs, bajar es bueno: menos cartera dada de baja.
  const positivo = dv <= 0
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-gray-200 bg-white p-5">
      <div className="flex items-start justify-between gap-2">
        <span className="text-xs font-medium uppercase tracking-wide text-gray-500">
          {label}
        </span>
        <span
          className={`text-xs font-semibold ${
            positivo ? 'text-[#1D9E75]' : 'text-[#A32D2D]'
          }`}
        >
          {deltaFormat === 'currency' ? fmt$(dv) : fmtN(dv)} ({fmtPct(delta.pct)})
        </span>
      </div>
      <span className="text-2xl font-bold text-gray-900">{value}</span>
      <div className="rounded-md bg-[#534AB7] px-3 py-1.5 text-center text-xs font-semibold text-white">
        {mtdLabel}: {mtdValue}
      </div>
    </div>
  )
}

function RatioCard({
  label,
  value,
  disabled,
  hint,
}: {
  label: string
  value: string
  disabled?: boolean
  hint?: string
}) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 text-center">
      <div className="text-xs font-medium uppercase tracking-wide text-gray-500">
        {label}
      </div>
      <div
        className={`mt-1 text-2xl font-bold ${
          disabled ? 'text-gray-300' : 'text-gray-900'
        }`}
      >
        {disabled ? '—' : value}
      </div>
      {disabled && hint && (
        <div className="mt-1 text-[11px] leading-tight text-gray-400">{hint}</div>
      )}
    </div>
  )
}

// ── Columnas ─────────────────────────────────────────────────────────────────

const MONTHLY_COLUMNS: Column<IdmsChargeOffMonthlyDetail>[] = [
  { key: 'month_name', header: 'Month End' },
  {
    key: 'principal_balance',
    header: 'Month End Principal Bal',
    className: 'text-right',
    render: (r) => (r.principal_balance ? fmt$(r.principal_balance) : '—'),
  },
  {
    key: 'original_balance',
    header: 'Original C/O Balance',
    className: 'text-right',
    render: (r) => fmt$(r.original_balance),
  },
  { key: 'count', header: 'Units Charged Off', className: 'text-right' },
  {
    key: 'current_balance',
    header: 'Total Charge Off Balance',
    className: 'text-right',
    render: (r) => fmt$(r.current_balance),
  },
  {
    key: 'recovery_acv',
    header: 'Recovery ACV',
    className: 'text-right',
    render: (r) => fmt$(r.recovery_acv),
  },
  {
    key: 'recovery_ratio',
    header: 'Recovery Ratio',
    className: 'text-right',
    render: (r) => fmtPct(r.recovery_ratio),
  },
  {
    key: 'gross_co_ratio',
    header: 'Gross C/O Ratio',
    className: 'text-right',
    render: (r) => (r.gross_co_ratio !== null ? fmtPct(r.gross_co_ratio) : '—'),
  },
  {
    key: 'months_on_book',
    header: 'Months On Book',
    className: 'text-right',
    render: (r) =>
      r.months_on_book !== null ? n(r.months_on_book).toFixed(2) : '—',
  },
]

const DETAIL_COLUMNS: Column<IdmsChargeOff>[] = [
  { key: 'acct_id', header: 'Account' },
  { key: 'borrower', header: 'Borrower' },
  {
    key: 'charge_off_date',
    header: 'C/O Date',
    render: (r) => fmtDate(r.charge_off_date),
  },
  { key: 'make', header: 'Make' },
  { key: 'model', header: 'Model' },
  {
    key: 'original_balance',
    header: 'Original',
    className: 'text-right',
    render: (r) => fmt$(r.original_balance),
  },
  {
    key: 'current_balance',
    header: 'Current',
    className: 'text-right',
    render: (r) => fmt$(r.current_balance),
  },
  { key: 'status', header: 'Status' },
]

// ── Vista ────────────────────────────────────────────────────────────────────

export default function IdmsDashboard() {
  const {
    session,
    isAuthenticated,
    mfaRequired,
    login,
    isLoginLoading,
    loginError,
    years,
    activeYear,
    setSelectedYear,
    sync,
    syncMonthEnd,
    syncResult,
    syncError,
    overview,
    monthly,
    priorMonthly,
    detail,
    isLoading,
  } = useIdms()

  const [otp, setOtp] = useState('')

  if (!isAuthenticated) {
    return (
      <div className="mx-auto max-w-md space-y-4 rounded-xl bg-white p-6 shadow-sm">
        <h1 className="text-lg font-bold text-gray-900">IDMS Reports</h1>
        <p className="text-sm text-gray-500">
          {mfaRequired
            ? 'IDMS requiere el código de tu app autenticadora.'
            : 'No hay sesión activa con IDMS. Conecta para sincronizar datos.'}
        </p>
        <input
          type="text"
          value={otp}
          onChange={(e) => setOtp(e.target.value)}
          placeholder="Código MFA (si aplica)"
          maxLength={6}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#ffea00]"
        />
        <button
          onClick={() => login(otp || undefined)}
          disabled={isLoginLoading}
          className="w-full rounded-md bg-[#ffea00] px-4 py-2 text-sm font-semibold text-gray-900 hover:bg-yellow-300 disabled:opacity-50"
        >
          {isLoginLoading ? 'Conectando...' : 'Conectar con IDMS'}
        </button>
        {loginError && <p className="text-sm text-red-600">{loginError}</p>}
        {session?.message && <p className="text-xs text-gray-400">{session.message}</p>}
      </div>
    )
  }

  // Serie de la gráfica: unidades del año activo contra el anterior.
  const prior = new Map(priorMonthly.map((m) => [m.month, m.count]))
  const chartData = MONTHS.map((name, i) => {
    const month = i + 1
    const actual = monthly.find((m) => m.month === month)
    return {
      month_name: name,
      current: actual ? actual.count : null,
      prior: prior.get(month) ?? null,
    }
  }).filter((d) => d.current !== null || d.prior !== null)

  const totals = monthly.reduce(
    (a, m) => ({
      count: a.count + m.count,
      original: a.original + n(m.original_balance),
      current: a.current + n(m.current_balance),
      recovery: a.recovery + n(m.recovery_acv),
    }),
    { count: 0, original: 0, current: 0, recovery: 0 },
  )

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Charge Off Overview</h1>
          <p className="text-sm text-gray-500">Datos de IDMS — Automania</p>
        </div>
        <div className="flex items-center gap-3">
          {years.length > 0 && (
            <select
              value={activeYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#ffea00]"
            >
              {years.map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>
          )}
          <button
            onClick={() => syncMonthEnd()}
            disabled={isLoading}
            title="Guarda la foto de la cartera de hoy; habilita Gross C/O Ratio y Months On Book"
            className="rounded-md border border-gray-300 px-4 py-1.5 text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            Snapshot cartera
          </button>
          <button
            onClick={() => sync(activeYear)}
            disabled={isLoading}
            className="rounded-md bg-[#ffea00] px-4 py-1.5 text-sm font-semibold text-gray-900 hover:bg-yellow-300 disabled:opacity-50"
          >
            {isLoading ? 'Sincronizando...' : 'Sincronizar año'}
          </button>
        </div>
      </div>

      {syncResult && (
        <div className="rounded-md bg-green-50 p-3 text-sm text-green-700">
          {syncResult.message}
        </div>
      )}
      {syncError && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{syncError}</div>
      )}

      {isLoading && !overview ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : overview && overview.ytd_count > 0 ? (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <OverviewCard
              label="YTD Total C/O"
              value={fmt$(overview.ytd_total_charge_off)}
              delta={overview.delta_total_charge_off}
              deltaFormat="currency"
              mtdLabel="MTD Total C/O"
              mtdValue={fmt$(overview.mtd_total_charge_off)}
            />
            <OverviewCard
              label="YTD Avg Prin Bal C/O"
              value={fmt$(overview.ytd_avg_prin_bal)}
              delta={overview.delta_avg_prin_bal}
              deltaFormat="currency"
              mtdLabel="MTD Avg Prin Bal C/O"
              mtdValue={fmt$(overview.mtd_avg_prin_bal)}
            />
            <OverviewCard
              label="YTD # of C/O's"
              value={fmtN(overview.ytd_count)}
              delta={overview.delta_count}
              deltaFormat="number"
              mtdLabel="MTD # of C/O"
              mtdValue={fmtN(overview.mtd_count)}
            />
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <RatioCard
              label="Recovery Ratio"
              value={fmtPct(overview.recovery_ratio)}
            />
            <RatioCard
              label="Gross C/O Ratio"
              value={fmtPct(overview.gross_co_ratio)}
              disabled={!overview.has_portfolio_data}
              hint="Requiere snapshot de cartera del período"
            />
            <RatioCard
              label="Annualized C/O Ratio"
              value={fmtPct(overview.annualized_co_ratio)}
              disabled={!overview.has_portfolio_data}
              hint="Requiere snapshot de cartera del período"
            />
          </div>

          <div className="rounded-xl bg-white p-5 shadow-sm">
            <h3 className="mb-4 text-sm font-semibold text-gray-700">
              Resumen mensual — {activeYear}
            </h3>
            <DataTable
              columns={MONTHLY_COLUMNS}
              data={monthly}
              pageSize={12}
              emptyText="No hay datos para el año seleccionado."
            />
            <div className="mt-3 flex flex-wrap gap-x-8 gap-y-1 border-t border-gray-200 pt-3 text-sm">
              <span className="font-semibold text-gray-700">Totales</span>
              <span className="text-gray-600">
                Units: <b>{fmtN(totals.count)}</b>
              </span>
              <span className="text-gray-600">
                Original: <b>{fmt$(totals.original)}</b>
              </span>
              <span className="text-gray-600">
                Total C/O: <b>{fmt$(totals.current)}</b>
              </span>
              <span className="text-gray-600">
                Recovery: <b>{fmt$(totals.recovery)}</b>
              </span>
              <span className="text-gray-600">
                Recovery Ratio:{' '}
                <b>
                  {totals.original
                    ? fmtPct((totals.recovery / totals.original) * 100)
                    : '—'}
                </b>
              </span>
            </div>
          </div>

          {chartData.length > 0 && (
            <div className="rounded-xl bg-white p-5 shadow-sm">
              <h3 className="mb-4 text-sm font-semibold text-gray-700">
                Charge offs por mes — {activeYear} vs {activeYear - 1}
              </h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month_name" />
                    <YAxis />
                    <Tooltip formatter={(v: number) => fmtN(v)} />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="current"
                      name={`Current Year C/O (${activeYear})`}
                      stroke="#1D9E75"
                      strokeWidth={2}
                      connectNulls
                    />
                    <Line
                      type="monotone"
                      dataKey="prior"
                      name={`Prior Year C/O (${activeYear - 1})`}
                      stroke="#378ADD"
                      strokeWidth={2}
                      connectNulls
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          <div className="rounded-xl bg-white p-5 shadow-sm">
            <h3 className="mb-4 text-sm font-semibold text-gray-700">
              Detalle de cuentas
            </h3>
            <DataTable
              columns={DETAIL_COLUMNS}
              data={detail}
              pageSize={20}
              emptyText="No hay cuentas para el año seleccionado."
            />
          </div>
        </>
      ) : (
        <EmptyState
          title="Sin datos"
          description="Seleccioná un año y sincronizá con IDMS para cargar Charge Offs."
        />
      )}
    </div>
  )
}
