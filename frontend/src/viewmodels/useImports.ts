import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { importsApi } from '@/models/importsApi'
import { callAnalyticsApi } from '@/models/callAnalyticsApi'
import type { ImportResult } from '@/types/imports'
import type { FetchResult } from '@/types/callAnalytics'

export function useImports() {
  const queryClient = useQueryClient()
  const [lastResult, setLastResult] = useState<ImportResult | null>(null)
  const [lastError, setLastError] = useState<string | null>(null)
  const [rcFetchResult, setRcFetchResult] = useState<FetchResult | null>(null)

  function onSuccess(domain: string) {
    return (result: ImportResult) => {
      setLastResult(result)
      setLastError(null)
      void queryClient.invalidateQueries({ queryKey: [domain] })
    }
  }

  function onError(err: unknown) {
    const msg = err instanceof Error ? err.message : 'Upload failed'
    setLastError(msg)
  }

  const dailySalesMutation = useMutation({
    mutationFn: importsApi.uploadDailySales,
    onSuccess: onSuccess('sales'),
    onError,
  })

  const hoursSummaryMutation = useMutation({
    mutationFn: importsApi.uploadHoursSummary,
    onSuccess: onSuccess('hours'),
    onError,
  })

  const hoursDetailMutation = useMutation({
    mutationFn: importsApi.uploadHoursDetail,
    onSuccess: onSuccess('technicians'),
    onError,
  })

  const wipMutation = useMutation({
    mutationFn: importsApi.uploadWip,
    onSuccess: onSuccess('wip'),
    onError,
  })

  const rcFetchMutation = useMutation({
    mutationFn: callAnalyticsApi.fetch,
    onSuccess: (result) => {
      setRcFetchResult(result)
      void queryClient.invalidateQueries({ queryKey: ['callAnalytics'] })
    },
  })

  const paymentReportMutation = useMutation({
    mutationFn: importsApi.uploadPaymentReport,
    onSuccess: onSuccess('payment'),
    onError,
  })

  return {
    uploadDailySales: (file: File) => dailySalesMutation.mutateAsync(file),
    uploadHoursSummary: (file: File) => hoursSummaryMutation.mutateAsync(file),
    uploadHoursDetail: (file: File) => hoursDetailMutation.mutateAsync(file),
    uploadWip: (file: File) => wipMutation.mutateAsync(file),
    uploadPaymentReport: (file: File) => paymentReportMutation.mutateAsync(file),
    lastResult,
    lastError,
    rcFetchMutation,
    rcFetchResult,
    isRcFetchPending: rcFetchMutation.isPending,
    isUploading:
      dailySalesMutation.isPending ||
      hoursSummaryMutation.isPending ||
      hoursDetailMutation.isPending ||
      wipMutation.isPending ||
      paymentReportMutation.isPending,
  }
}
