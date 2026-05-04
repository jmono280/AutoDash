import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { format, parseISO } from 'date-fns'
import type { TrendPoint } from '@/types/sales'

const USD = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

interface Props {
  data: TrendPoint[]
}

export default function DailySalesBarChart({ data }: Props) {
  const chartData = data.map((d) => ({
    day: format(parseISO(d.date), 'MMM d'),
    profit: parseFloat(d.profit),
    gross: parseFloat(d.gross_sales),
  }))

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={chartData} margin={{ top: 4, right: 8, left: 8, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="day" tick={{ fontSize: 11 }} tickLine={false} />
        <YAxis tickFormatter={(v: number) => `$${(v / 1000).toFixed(0)}k`} tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <Tooltip formatter={(v: number) => [USD.format(v), 'Gross Profit']} />
        <Bar dataKey="profit" fill="#1D9E75" radius={[3, 3, 0, 0]} maxBarSize={28} />
      </BarChart>
    </ResponsiveContainer>
  )
}
