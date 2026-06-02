import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { callAnalyticsApi } from '@/models/callAnalyticsApi'
import type { IsoRange } from '@/types/callAnalytics'

function todayIsoRange(): IsoRange {
  const now = new Date()
  const yyyy = now.getUTCFullYear()
  const mm = String(now.getUTCMonth() + 1).padStart(2, '0')
  const dd = String(now.getUTCDate()).padStart(2, '0')
  return {
    from: `${yyyy}-${mm}-${dd}T00:00:00Z`,
    to:   `${yyyy}-${mm}-${dd}T23:59:59Z`,
  }
}

export function useCallAnalytics() {
  const [viewRange, setViewRange] = useState<IsoRange>(todayIsoRange)
  const [extensionFilter, setExtensionFilter] = useState<string>('')

  const kpisQuery = useQuery({
    queryKey: ['callAnalytics', 'kpis', viewRange],
    queryFn:  () => callAnalyticsApi.kpis(viewRange),
  })

  const byExtQuery = useQuery({
    queryKey: ['callAnalytics', 'byExt', viewRange],
    queryFn:  () => callAnalyticsApi.byExtension(viewRange),
  })

  const listQuery = useQuery({
    queryKey: ['callAnalytics', 'list', viewRange],
    queryFn:  () => callAnalyticsApi.list(viewRange),
  })

  const filteredList = extensionFilter
    ? (listQuery.data ?? []).filter((r) => r.extension_number === extensionFilter)
    : (listQuery.data ?? [])

  return {
    kpis:            kpisQuery.data,
    byExtension:     byExtQuery.data ?? [],
    list:            filteredList,
    viewRange,
    setViewRange,
    extensionFilter,
    setExtensionFilter,
    isLoading: kpisQuery.isLoading || byExtQuery.isLoading || listQuery.isLoading,
  }
}
