import { RadialBar, RadialBarChart, ResponsiveContainer, Tooltip } from 'recharts'
import type { HoursKpis } from '@/types/hours'

interface Props {
  kpis: HoursKpis
}

interface GaugeItem {
  label: string
  value: number
  fill: string
}

function Gauge({ item }: { item: GaugeItem }) {
  return (
    <div className="flex flex-col items-center">
      <ResponsiveContainer width="100%" height={120}>
        <RadialBarChart
          cx="50%"
          cy="80%"
          innerRadius="60%"
          outerRadius="90%"
          startAngle={180}
          endAngle={0}
          data={[item]}
          barSize={14}
        >
          {/* Background track */}
          <RadialBar dataKey="value" background={{ fill: '#e5e7eb' }} />
          <Tooltip formatter={(v: number) => [`${v.toFixed(1)}%`, item.label]} />
        </RadialBarChart>
      </ResponsiveContainer>
      <span className="text-lg font-bold text-gray-800 -mt-4">{item.value.toFixed(1)}%</span>
      <span className="text-xs text-gray-500 mt-0.5 text-center leading-tight">{item.label}</span>
    </div>
  )
}

export default function EfficiencyGauges({ kpis }: Props) {
  const items: GaugeItem[] = [
    { label: 'Advisor Efficiency',     value: parseFloat(kpis.advisor_efficiency),         fill: '#378ADD' },
    { label: 'Tech Proficiency',       value: parseFloat(kpis.technician_proficiency),      fill: '#534AB7' },
    { label: 'Tech Productivity',      value: parseFloat(kpis.technician_productivity),     fill: '#1D9E75' },
    { label: 'Tech Efficiency',        value: kpis.technician_efficiency != null ? parseFloat(kpis.technician_efficiency) : 0, fill: '#BA7517' },
  ]

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
      {items.map((item) => (
        <Gauge key={item.label} item={item} />
      ))}
    </div>
  )
}
