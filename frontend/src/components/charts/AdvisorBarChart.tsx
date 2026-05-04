import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { AdvisorGroup } from '@/types/wip'

interface Props {
  data: AdvisorGroup[]
}

export default function AdvisorBarChart({ data }: Props) {
  const chartData = [...data]
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
    .map((d) => ({
      advisor: d.advisor ?? 'Unassigned',
      count: d.count,
      avg_days: parseFloat(d.avg_days_open),
    }))

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart layout="vertical" data={chartData} margin={{ top: 4, right: 24, left: 8, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis type="category" dataKey="advisor" width={80} tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <Tooltip
          formatter={(v: number, name: string) => [
            name === 'count' ? `${v} ROs` : `${v.toFixed(1)} days`,
            name === 'count' ? 'Open ROs' : 'Avg Days Open',
          ]}
        />
        <Bar dataKey="count" name="count" fill="#534AB7" radius={[0, 3, 3, 0]} barSize={12} />
      </BarChart>
    </ResponsiveContainer>
  )
}
