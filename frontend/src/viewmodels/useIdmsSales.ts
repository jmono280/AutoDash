import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { idmsApi } from '@/models/idmsApi'

export function useIdmsSales() {
  const queryClient = useQueryClient()
  const [selectedYear, setSelectedYear] = useState<number | null>(null)

  const yearsQuery = useQuery({
    queryKey: ['idms', 'sales', 'years'],
    queryFn: () => idmsApi.getSalesYears(),
  })

  const currentYear = new Date().getFullYear()
  const activeYear = selectedYear ?? (yearsQuery.data?.[0] || currentYear)

  const syncMutation = useMutation({
    mutationFn: (year: number) => idmsApi.syncSales(year),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['idms', 'sales'] })
    },
  })

  const importMutation = useMutation({
    mutationFn: (file: File) => idmsApi.importSalesHistorical(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['idms', 'sales'] })
    },
  })

  const kpisQuery = useQuery({
    queryKey: ['idms', 'sales', 'kpis', activeYear],
    queryFn: () => idmsApi.getSalesKpis(activeYear),
  })

  const monthlyQuery = useQuery({
    queryKey: ['idms', 'sales', 'monthly', activeYear],
    queryFn: () => idmsApi.getSalesMonthly(activeYear),
  })

  const detailQuery = useQuery({
    queryKey: ['idms', 'sales', 'detail', activeYear],
    queryFn: () => idmsApi.getSales(activeYear),
  })

  const bySalespersonQuery = useQuery({
    queryKey: ['idms', 'sales', 'by-salesperson', activeYear],
    queryFn: () => idmsApi.getSalesBySalesperson(activeYear),
  })

  const byVehicleQuery = useQuery({
    queryKey: ['idms', 'sales', 'by-vehicle', activeYear],
    queryFn: () => idmsApi.getSalesByVehicle(activeYear),
  })

  const isLoading =
    yearsQuery.isLoading ||
    kpisQuery.isLoading ||
    monthlyQuery.isLoading ||
    detailQuery.isLoading ||
    bySalespersonQuery.isLoading ||
    byVehicleQuery.isLoading ||
    syncMutation.isPending ||
    importMutation.isPending

  return {
    years: yearsQuery.data ?? [],
    activeYear,
    setSelectedYear,

    sync: syncMutation.mutate,
    importHistorical: importMutation.mutate,
    syncResult: syncMutation.data ?? importMutation.data,
    syncError: syncMutation.error?.message || importMutation.error?.message || null,
    isSyncing: syncMutation.isPending,
    isImporting: importMutation.isPending,

    kpis: kpisQuery.data,
    monthly: monthlyQuery.data ?? [],
    detail: detailQuery.data ?? [],
    bySalesperson: bySalespersonQuery.data ?? [],
    byVehicle: byVehicleQuery.data ?? [],

    isLoading,
  }
}
