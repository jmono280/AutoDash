import { useQuery } from '@tanstack/react-query'
import { hoursApi } from '@/models/hoursApi'
import type { DateRange } from '@/lib/dateRange'

export function useHours(range: DateRange) {
  const kpisQuery = useQuery({
    queryKey: ['hours', 'kpis', range],
    queryFn: () => hoursApi.getKpis(range),
  })

  const listQuery = useQuery({
    queryKey: ['hours', 'list', range],
    queryFn: () => hoursApi.list(range),
  })

  return {
    kpis: kpisQuery.data,
    list: listQuery.data,
    isLoading: kpisQuery.isLoading || listQuery.isLoading,
    error: kpisQuery.error ?? listQuery.error,
  }
}
