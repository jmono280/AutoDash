import { Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { format, parseISO } from 'date-fns'
import type { TrendPoint } from '@/types/sales'

const USD = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

interface Props {
  data: TrendPoint[]
}

export default function DailySalesTrendChart({ data }: Props) {
  const chartData = data.map((d) => ({
    day: format(parseISO(d.date), 'MMM d'),
    gross_sales: parseFloat(d.gross_sales),
    net_sales: parseFloat(d.net_sales),
  }))

  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={chartData} margin={{ top: 4, right: 8, left: 8, bottom: 4 }}>
        <defs>
          <linearGradient id="gradGross" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#1D9E75" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#1D9E75" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="gradNet" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#378ADD" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#378ADD" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="day" tick={{ fontSize: 11 }} tickLine={false} />
        <YAxis tickFormatter={(v: number) => `$${(v / 1000).toFixed(0)}k`} tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <Tooltip formatter={(v: number) => USD.format(v)} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Area type="monotone" dataKey="gross_sales" name="Gross Sales" stroke="#1D9E75" fill="url(#gradGross)" strokeWidth={2} dot={false} />
        <Area type="monotone" dataKey="net_sales" name="Net Sales" stroke="#378ADD" fill="url(#gradNet)" strokeWidth={2} dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  )
}
