import axios from 'axios'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { idmsApi } from '@/models/idmsApi'

function extractError(err: unknown): string | null {
  if (!err) return null
  if (axios.isAxiosError(err)) {
    const detail = (err.response?.data as { detail?: string } | undefined)?.detail
    return detail ?? err.message
  }
  return err instanceof Error ? err.message : String(err)
}

function downloadFile(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export function useIdmsInventory() {
  const queryClient = useQueryClient()

  const syncMutation = useMutation({
    mutationFn: () => idmsApi.syncInventory(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['idms', 'inventory'] })
    },
  })

  const kpisQuery = useQuery({
    queryKey: ['idms', 'inventory', 'kpis'],
    queryFn: () => idmsApi.getInventoryKpis(),
  })

  const agingQuery = useQuery({
    queryKey: ['idms', 'inventory', 'aging'],
    queryFn: () => idmsApi.getInventoryAging(),
  })

  const detailQuery = useQuery({
    queryKey: ['idms', 'inventory', 'detail'],
    queryFn: () => idmsApi.getInventory(),
  })

  const exportMutation = useMutation({
    mutationFn: () => idmsApi.exportInventory(),
    onSuccess: ({ blob, filename }) => downloadFile(blob, filename),
  })

  const exportPdfMutation = useMutation({
    mutationFn: () => idmsApi.exportInventoryPdf(),
    onSuccess: ({ blob, filename }) => downloadFile(blob, filename),
  })

  const isLoading =
    kpisQuery.isLoading || agingQuery.isLoading || detailQuery.isLoading || syncMutation.isPending

  return {
    sync: syncMutation.mutate,
    syncResult: syncMutation.data,
    syncError: extractError(syncMutation.error),
    isSyncing: syncMutation.isPending,

    exportExcel: exportMutation.mutate,
    isExporting: exportMutation.isPending,
    exportError: exportMutation.error?.message ?? null,

    exportPdf: exportPdfMutation.mutate,
    isExportingPdf: exportPdfMutation.isPending,
    exportPdfError: exportPdfMutation.error?.message ?? null,

    kpis: kpisQuery.data,
    aging: agingQuery.data ?? [],
    detail: detailQuery.data ?? [],

    isLoading,
  }
}
