import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { wipApi } from '@/models/wipApi'
import type { WipListParams } from '@/models/wipApi'

export function useWip() {
  const [filters, setFiltersState] = useState<WipListParams>({})
  const [page, setPageState] = useState(1)

  // Reset page to 1 whenever filters change
  function setFilters(next: WipListParams) {
    setPageState(1)
    setFiltersState(next)
  }

  function setPage(next: number) {
    setPageState(next)
  }

  const listQuery = useQuery({
    queryKey: ['wip', 'list', filters, page],
    queryFn: () => wipApi.list({ ...filters, page }),
  })

  const kpisQuery = useQuery({
    queryKey: ['wip', 'kpis'],
    queryFn: wipApi.getKpis,
  })

  const agingQuery = useQuery({
    queryKey: ['wip', 'aging'],
    queryFn: wipApi.getAging,
  })

  const byCategoryQuery = useQuery({
    queryKey: ['wip', 'by-category'],
    queryFn: wipApi.getByCategory,
  })

  const byAdvisorQuery = useQuery({
    queryKey: ['wip', 'by-advisor'],
    queryFn: wipApi.getByAdvisor,
  })

  return {
    list: listQuery.data,
    kpis: kpisQuery.data,
    aging: agingQuery.data,
    byCategory: byCategoryQuery.data,
    byAdvisor: byAdvisorQuery.data,
    filters,
    setFilters,
    page,
    setPage,
    isLoading: listQuery.isLoading,
    isLoadingAll:
      listQuery.isLoading ||
      kpisQuery.isLoading ||
      agingQuery.isLoading ||
      byCategoryQuery.isLoading ||
      byAdvisorQuery.isLoading,
  }
}
