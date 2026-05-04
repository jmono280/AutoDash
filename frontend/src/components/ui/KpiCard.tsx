import { HelpTooltip } from './HelpTooltip'

interface HelpContent {
  title: string
  description: string
  examples?: string[]
}

interface KpiCardProps {
  label: string
  value: string | number
  delta?: number
  deltaType?: 'positive' | 'negative' | 'neutral'
  format?: 'currency' | 'percent' | 'number'
  help?: HelpContent
  className?: string
}

const USD = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
const NUM = new Intl.NumberFormat('en-US')

function fmt(value: string | number, format?: KpiCardProps['format']): string {
  const n = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(n)) return String(value)
  switch (format) {
    case 'currency': return USD.format(n)
    case 'percent':  return `${n.toFixed(2)}%`
    default:         return NUM.format(n)
  }
}

export default function KpiCard({ label, value, delta, deltaType, format, help, className = '' }: KpiCardProps) {
  return (
    <div className={`bg-white rounded-xl border border-gray-200 p-5 flex flex-col gap-1 ${className}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</span>
        {help && <HelpTooltip {...help} />}
      </div>
      <span className="text-2xl font-bold text-gray-900">{fmt(value, format)}</span>
      {delta !== undefined && (
        <span
          className={`text-xs font-medium ${
            deltaType === 'positive'
              ? 'text-emerald-600'
              : deltaType === 'negative'
                ? 'text-red-600'
                : 'text-gray-400'
          }`}
        >
          {delta >= 0 ? '▲' : '▼'} {Math.abs(delta).toFixed(2)}%
        </span>
      )}
    </div>
  )
}
