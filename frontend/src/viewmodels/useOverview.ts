import { useQuery } from '@tanstack/react-query'
import { hoursApi } from '@/models/hoursApi'
import { salesApi } from '@/models/salesApi'
import { wipApi } from '@/models/wipApi'
import type { DateRange } from '@/lib/dateRange'

export function useOverview(range: DateRange) {
  const salesKpisQuery = useQuery({
    queryKey: ['sales', 'kpis', range],
    queryFn: () => salesApi.getKpis(range),
  })

  const hoursKpisQuery = useQuery({
    queryKey: ['hours', 'kpis', range],
    queryFn: () => hoursApi.getKpis(range),
  })

  const wipKpisQuery = useQuery({
    queryKey: ['wip', 'kpis'],
    queryFn: wipApi.getKpis,
  })

  const agingQuery = useQuery({
    queryKey: ['wip', 'aging'],
    queryFn: wipApi.getAging,
  })

  const salesTrendQuery = useQuery({
    queryKey: ['sales', 'trend', range],
    queryFn: () => salesApi.getTrend(range),
  })

  return {
    salesKpis: salesKpisQuery.data,
    hoursKpis: hoursKpisQuery.data,
    wipKpis: wipKpisQuery.data,
    aging: agingQuery.data,
    salesTrend: salesTrendQuery.data,
    isLoading:
      salesKpisQuery.isLoading ||
      hoursKpisQuery.isLoading ||
      wipKpisQuery.isLoading ||
      agingQuery.isLoading ||
      salesTrendQuery.isLoading,
  }
}
