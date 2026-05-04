import type { DateRange } from '@/lib/dateRange'

interface DateRangePickerProps {
  value: DateRange
  onChange: (range: DateRange) => void
  className?: string
}

export default function DateRangePicker({ value, onChange, className = '' }: DateRangePickerProps) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <label className="text-sm text-gray-500">From</label>
      <input
        type="date"
        value={value.from}
        onChange={(e) => onChange({ ...value, from: e.target.value })}
        className="border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
      />
      <span className="text-gray-400">–</span>
      <label className="text-sm text-gray-500">To</label>
      <input
        type="date"
        value={value.to}
        min={value.from}
        onChange={(e) => onChange({ ...value, to: e.target.value })}
        className="border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
      />
    </div>
  )
}
