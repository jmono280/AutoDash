import { useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useIdms } from '@/viewmodels/useIdms'
import KpiCard from '@/components/ui/KpiCard'
import Spinner from '@/components/ui/Spinner'
import EmptyState from '@/components/ui/EmptyState'
import DataTable from '@/components/ui/DataTable'
import type { Column } from '@/components/ui/DataTable'
import type { IdmsChargeOff, IdmsChargeOffMonthly } from '@/types/idms'

const currency = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
})

const numberFmt = new Intl.NumberFormat('en-US')

function fmt$(val: string | number | undefined): string {
  if (val === undefined || val === null || val === '') return '$0'
  const n = typeof val === 'string' ? parseFloat(val) : val
  return currency.format(n)
}

function fmtN(val: number | string | undefined): string {
  if (val === undefined || val === null || val === '') return '0'
  const n = typeof val === 'string' ? parseFloat(val) : val
  return numberFmt.format(n)
}

const MONTHLY_COLUMNS: Column<IdmsChargeOffMonthly>[] = [
  { key: 'month_name', header: 'Month' },
  { key: 'count', header: 'Units', className: 'text-right' },
  {
    key: 'original_balance',
    header: 'Original Balance',
    className: 'text-right',
    render: (r) => fmt$(r.original_balance),
  },
  {
    key: 'current_balance',
    header: 'Total C/O Balance',
    className: 'text-right',
    render: (r) => fmt$(r.current_balance),
  },
  {
    key: 'total_recovery',
    header: 'Recovery',
    className: 'text-right',
    render: (r) => fmt$(r.total_recovery),
  },
]

const DETAIL_COLUMNS: Column<IdmsChargeOff>[] = [
  { key: 'acct_id', header: 'Account' },
  { key: 'borrower', header: 'Borrower' },
  {
    key: 'charge_off_date',
    header: 'C/O Date',
    render: (r) => (r.charge_off_date ? r.charge_off_date.slice(0, 10) : '—'),
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
    syncResult,
    syncError,
    kpis,
    monthly,
    detail,
    isLoading,
  } = useIdms()

  const [otp, setOtp] = useState('')

  function handleLogin() {
    login(otp || undefined)
  }

  function handleSync() {
    if (activeYear) sync(activeYear)
  }

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
          onClick={handleLogin}
          disabled={isLoginLoading}
          className="w-full rounded-md bg-[#ffea00] px-4 py-2 text-sm font-semibold text-gray-900 hover:bg-yellow-300 disabled:opacity-50"
        >
          {isLoginLoading ? 'Conectando...' : 'Conectar con IDMS'}
        </button>
        {(loginError || syncError) && (
          <p className="text-sm text-red-600">{loginError || syncError}</p>
        )}
        {session?.message && (
          <p className="text-xs text-gray-400">{session.message}</p>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900">IDMS Reports</h1>
          <p className="text-sm text-gray-500">Charge Offs, Sales y Collections desde IDMS</p>
        </div>
        <div className="flex items-center gap-3">
          {years.length > 0 && (
            <select
              value={activeYear ?? ''}
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
            onClick={handleSync}
            disabled={!activeYear || isLoading}
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

      {isLoading && !kpis ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : kpis ? (
        <>
          {/* KPIs */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            <KpiCard
              label="Charge Offs"
              value={kpis.count}
              format="number"
            />
            <KpiCard
              label="Original Balance"
              value={parseFloat(kpis.total_original_balance)}
              format="currency"
            />
            <KpiCard
              label="Total C/O Balance"
              value={parseFloat(kpis.total_current_balance)}
              format="currency"
            />
            <KpiCard
              label="Recovery"
              value={parseFloat(kpis.total_recovery)}
              format="currency"
            />
            <KpiCard
              label="Adjusted"
              value={parseFloat(kpis.total_adjusted)}
              format="currency"
            />
          </div>

          {/* Chart */}
          {monthly.length > 0 && (
            <div className="rounded-xl bg-white p-5 shadow-sm">
              <h3 className="mb-4 text-sm font-semibold text-gray-700">
                Charge Offs mensuales — {activeYear}
              </h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthly}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month_name" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip
                      formatter={(value: number, name: string) =>
                        name === 'Units'
                          ? fmtN(value as number)
                          : fmt$(value as number)
                      }
                    />
                    <Legend />
                    <Bar
                      yAxisId="left"
                      dataKey="count"
                      name="Units"
                      fill="#534AB7"
                    />
                    <Bar
                      yAxisId="right"
                      dataKey="original_balance"
                      name="Original Balance"
                      fill="#1D9E75"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Monthly table */}
          <div className="rounded-xl bg-white p-5 shadow-sm">
            <h3 className="mb-4 text-sm font-semibold text-gray-700">
              Resumen mensual
            </h3>
            <DataTable
              columns={MONTHLY_COLUMNS}
              data={monthly}
              pageSize={12}
              emptyText="No hay datos para el año seleccionado."
            />
          </div>

          {/* Detail table */}
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
