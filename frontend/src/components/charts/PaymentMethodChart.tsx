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
import type { PaymentByMethod } from '@/types/paymentReport'

interface Props {
  data: PaymentByMethod[]
}

export default function PaymentMethodChart({ data }: Props) {
  const chartData = data.map((d) => ({
    name:  d.payment_method,
    Pagos: d.count,
    Monto: parseFloat(d.total_amount),
  }))

  return (
    <ResponsiveContainer width="100%" height={Math.max(180, chartData.length * 52)}>
      <BarChart
        layout="vertical"
        data={chartData}
        margin={{ top: 4, right: 24, left: 8, bottom: 4 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis
          type="category"
          dataKey="name"
          width={90}
          tick={{ fontSize: 11 }}
          tickLine={false}
        />
        <Tooltip formatter={(v: number, name: string) => name === 'Monto' ? `$${v.toFixed(2)}` : v} />
        <Legend iconSize={10} wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey="Pagos" fill="#378ADD" radius={[0, 3, 3, 0]} />
        <Bar dataKey="Monto" fill="#BA7517" radius={[0, 3, 3, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
