import { useQuery } from '@tanstack/react-query'
import { salesApi } from '@/models/salesApi'
import type { DateRange } from '@/lib/dateRange'

export function useSales(range: DateRange) {
  const kpisQuery = useQuery({
    queryKey: ['sales', 'kpis', range],
    queryFn: () => salesApi.getKpis(range),
  })

  const trendQuery = useQuery({
    queryKey: ['sales', 'trend', range],
    queryFn: () => salesApi.getTrend(range),
  })

  const dowQuery = useQuery({
    queryKey: ['sales', 'dow', range],
    queryFn: () => salesApi.getByDayOfWeek(range),
  })

  const listQuery = useQuery({
    queryKey: ['sales', 'list', range],
    queryFn: () => salesApi.list(range),
  })

  return {
    kpis: kpisQuery.data,
    trend: trendQuery.data,
    dayOfWeek: dowQuery.data,
    list: listQuery.data,
    isLoading:
      kpisQuery.isLoading ||
      trendQuery.isLoading ||
      dowQuery.isLoading ||
      listQuery.isLoading,
    error: kpisQuery.error ?? trendQuery.error ?? dowQuery.error ?? listQuery.error,
  }
}
