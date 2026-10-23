import type { DateRange } from '@/lib/dateRange'

interface DateRangePickerProps {
  value: DateRange
  onChange: (range: DateRange) => void
  className?: string
}

export default function DateRangePicker({ value, onChange, className = '' }: DateRangePickerProps) {
  return (
    <div className={`flex w-full items-center gap-2 sm:w-auto ${className}`}>
      <label className="text-sm text-gray-500">From</label>
      <input
        type="date"
        value={value.from}
        onChange={(e) => onChange({ ...value, from: e.target.value })}
        className="min-w-0 flex-1 border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-[#ffea00] sm:flex-none"
      />
      <span className="text-gray-400">–</span>
      <label className="text-sm text-gray-500">To</label>
      <input
        type="date"
        value={value.to}
        min={value.from}
        onChange={(e) => onChange({ ...value, to: e.target.value })}
        className="min-w-0 flex-1 border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-[#ffea00] sm:flex-none"
      />
    </div>
  )
}
