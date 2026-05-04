import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { techniciansApi } from '@/models/techniciansApi'
import type { DateRange } from '@/lib/dateRange'
import type { TechnicianMetric } from '@/types/technician'

export function useTechnicians(range: DateRange) {
  const [metric, setMetric] = useState<TechnicianMetric>('hours_sold')

  const listQuery = useQuery({
    queryKey: ['technicians', 'list', range],
    queryFn: () => techniciansApi.list(range),
  })

  const rankingQuery = useQuery({
    queryKey: ['technicians', 'ranking', range, metric],
    queryFn: () => techniciansApi.getRanking({ ...range, metric }),
  })

  return {
    technicians: listQuery.data,
    ranking: rankingQuery.data,
    metric,
    setMetric,
    isLoading: listQuery.isLoading || rankingQuery.isLoading,
    error: listQuery.error ?? rankingQuery.error,
  }
}
