import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { importsApi } from '@/models/importsApi'
import type { ImportResult } from '@/types/imports'

export function useImports() {
  const queryClient = useQueryClient()
  const [lastResult, setLastResult] = useState<ImportResult | null>(null)
  const [lastError, setLastError] = useState<string | null>(null)

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

  return {
    uploadDailySales: (file: File) => dailySalesMutation.mutateAsync(file),
    uploadHoursSummary: (file: File) => hoursSummaryMutation.mutateAsync(file),
    uploadHoursDetail: (file: File) => hoursDetailMutation.mutateAsync(file),
    uploadWip: (file: File) => wipMutation.mutateAsync(file),
    lastResult,
    lastError,
    isUploading:
      dailySalesMutation.isPending ||
      hoursSummaryMutation.isPending ||
      hoursDetailMutation.isPending ||
      wipMutation.isPending,
  }
}
