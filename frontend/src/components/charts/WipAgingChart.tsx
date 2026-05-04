import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { AgingBucket } from '@/types/wip'

const BUCKET_COLORS: Record<string, string> = {
  '0-7d':   '#1D9E75',
  '8-14d':  '#B8A020',
  '15-30d': '#BA7517',
  '31-60d': '#D46020',
  '60+d':   '#A32D2D',
}

interface Props {
  aging: AgingBucket[]
}

export default function WipAgingChart({ aging }: Props) {
  const chartData = aging.map((b) => ({
    bucket: b.bucket,
    count: b.count,
  }))

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={chartData} margin={{ top: 4, right: 8, left: 8, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="bucket" tick={{ fontSize: 12 }} tickLine={false} />
        <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <Tooltip formatter={(v: number) => [`${v} ROs`, 'Count']} />
        <Bar dataKey="count" name="Open ROs" radius={[4, 4, 0, 0]} maxBarSize={56}>
          {chartData.map((entry) => (
            <Cell key={entry.bucket} fill={BUCKET_COLORS[entry.bucket] ?? '#9CA3AF'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
