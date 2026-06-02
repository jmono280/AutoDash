import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { paymentReportApi } from '@/models/paymentReportApi'
import type { PaymentDateRange } from '@/types/paymentReport'

function currentMonthRange(): PaymentDateRange {
  const now = new Date()
  const yyyy = now.getFullYear()
  const mm   = String(now.getMonth() + 1).padStart(2, '0')
  const last  = new Date(yyyy, now.getMonth() + 1, 0).getDate()
  return { from: `${yyyy}-${mm}-01`, to: `${yyyy}-${mm}-${last}` }
}

export function usePaymentReport() {
  const [range, setRange]             = useState<PaymentDateRange>(currentMonthRange)
  const [collectorFilter, setCollectorFilter] = useState<string>('')
  const [page, setPage]               = useState(1)

  function setRangeAndReset(r: PaymentDateRange) {
    setRange(r)
    setPage(1)
  }

  function setCollectorAndReset(c: string) {
    setCollectorFilter(c)
    setPage(1)
  }

  const kpisQuery = useQuery({
    queryKey: ['payment', 'kpis', range],
    queryFn:  () => paymentReportApi.kpis(range),
  })

  const byCollectorQuery = useQuery({
    queryKey: ['payment', 'byCollector', range],
    queryFn:  () => paymentReportApi.byCollector(range),
  })

  const byMethodQuery = useQuery({
    queryKey: ['payment', 'byMethod', range],
    queryFn:  () => paymentReportApi.byMethod(range),
  })

  const collectionStatsQuery = useQuery({
    queryKey: ['payment', 'collectionStats', range],
    queryFn:  () => paymentReportApi.collectionStats(range),
  })

  const transactionsQuery = useQuery({
    queryKey: ['payment', 'transactions', range, collectorFilter, page],
    queryFn:  () => paymentReportApi.transactions(range, collectorFilter || undefined, page),
  })

  return {
    range,
    setRange: setRangeAndReset,
    collectorFilter,
    setCollectorFilter: setCollectorAndReset,
    page,
    setPage,
    kpis:            kpisQuery.data,
    byCollector:     byCollectorQuery.data ?? [],
    byMethod:        byMethodQuery.data ?? [],
    collectionStats: collectionStatsQuery.data ?? [],
    transactions:    transactionsQuery.data,
    isLoading:
      kpisQuery.isLoading ||
      byCollectorQuery.isLoading ||
      byMethodQuery.isLoading ||
      collectionStatsQuery.isLoading ||
      transactionsQuery.isLoading,
  }
}
