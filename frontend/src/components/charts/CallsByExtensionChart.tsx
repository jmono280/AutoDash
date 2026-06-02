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
import type { CallByExtension } from '@/types/callAnalytics'

interface Props {
  data: CallByExtension[]
}

export default function CallsByExtensionChart({ data }: Props) {
  const chartData = data.map((d) => ({
    name: d.extension_name,
    Total: d.total_calls,
    Entrantes: d.inbound,
    Salientes: d.outbound,
  }))

  return (
    <ResponsiveContainer width="100%" height={Math.max(200, chartData.length * 52)}>
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
          width={110}
          tick={{ fontSize: 11 }}
          tickLine={false}
        />
        <Tooltip />
        <Legend iconSize={10} wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey="Total"     name="Total"     fill="#534AB7" radius={[0, 3, 3, 0]} />
        <Bar dataKey="Entrantes" name="Entrantes" fill="#1D9E75" radius={[0, 3, 3, 0]} />
        <Bar dataKey="Salientes" name="Salientes" fill="#378ADD" radius={[0, 3, 3, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
