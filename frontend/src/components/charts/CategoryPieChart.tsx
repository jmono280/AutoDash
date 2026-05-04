import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import type { CategoryGroup } from '@/types/wip'

const COLORS = ['#534AB7', '#1D9E75', '#378ADD', '#BA7517', '#A32D2D']

interface Props {
  data: CategoryGroup[]
}

const USD = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

export default function CategoryPieChart({ data }: Props) {
  const sorted = [...data].sort((a, b) => b.count - a.count)
  // Collapse beyond top 4 into "Other"
  const top4 = sorted.slice(0, 4)
  const rest = sorted.slice(4)
  const chartData =
    rest.length > 0
      ? [
          ...top4,
          {
            category: 'Other',
            count: rest.reduce((s, r) => s + r.count, 0),
            total_cog: String(rest.reduce((s, r) => s + parseFloat(r.total_cog), 0)),
            total_estimated: '0',
          },
        ]
      : top4

  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={chartData}
          dataKey="count"
          nameKey="category"
          cx="50%"
          cy="50%"
          outerRadius={90}
          label={({ category, percent }: { category: string; percent: number }) =>
            `${category} ${(percent * 100).toFixed(0)}%`
          }
          labelLine={false}
        >
          {chartData.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(v: number, name: string) => [v, name === 'count' ? 'ROs' : USD.format(v)]} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
      </PieChart>
    </ResponsiveContainer>
  )
}
