import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { TechnicianRankingItem } from '@/types/technician'

interface Props {
  ranking: TechnicianRankingItem[]
}

function shortName(full: string): string {
  const parts = full.split(' ')
  return parts.length > 1 ? `${parts[0][0]}. ${parts.slice(1).join(' ')}` : full
}

export default function TechnicianRankingChart({ ranking }: Props) {
  const chartData = [...ranking]
    .slice(0, 10)
    .map((t) => ({
      name: shortName(t.technician_name),
      hours_sold: parseFloat(t.hours_sold),
      hours_paid: parseFloat(t.hours_paid),
    }))
    .reverse() // bottom-to-top ordering for horizontal chart

  return (
    <ResponsiveContainer width="100%" height={Math.max(200, chartData.length * 40)}>
      <BarChart layout="vertical" data={chartData} margin={{ top: 4, right: 24, left: 4, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis type="category" dataKey="name" width={90} tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <Tooltip formatter={(v: number) => [`${v.toFixed(2)} h`]} />
        <Bar dataKey="hours_sold" name="Hours Sold" fill="#378ADD" radius={[0, 3, 3, 0]} barSize={10} />
        <Bar dataKey="hours_paid" name="Hours Paid" fill="#534AB7" radius={[0, 3, 3, 0]} barSize={10} />
      </BarChart>
    </ResponsiveContainer>
  )
}
