import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { idmsApi } from '@/models/idmsApi'

export function useIdms() {
  const queryClient = useQueryClient()
  const [selectedYear, setSelectedYear] = useState<number | null>(null)

  const sessionQuery = useQuery({
    queryKey: ['idms', 'session'],
    queryFn: () => idmsApi.session(),
  })

  const loginMutation = useMutation({
    mutationFn: (otpCode?: string) => idmsApi.login(otpCode),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['idms', 'session'] })
    },
  })

  const yearsQuery = useQuery({
    queryKey: ['idms', 'charge-offs', 'years'],
    queryFn: () => idmsApi.getChargeOffYears(),
  })

  const currentYear = new Date().getFullYear()
  const activeYear = selectedYear ?? (yearsQuery.data?.[0] || currentYear)

  const syncMutation = useMutation({
    mutationFn: (year: number) => idmsApi.syncChargeOffs(year),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['idms', 'charge-offs'] })
    },
  })

  // El snapshot de cartera es lo que habilita Gross C/O Ratio y Months On Book.
  const syncMonthEndMutation = useMutation({
    mutationFn: () => idmsApi.syncMonthEnd(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['idms', 'charge-offs'] })
    },
  })

  const overviewQuery = useQuery({
    queryKey: ['idms', 'charge-offs', 'overview', activeYear],
    queryFn: () => idmsApi.getChargeOffOverview(activeYear),
  })

  const monthlyQuery = useQuery({
    queryKey: ['idms', 'charge-offs', 'monthly-detail', activeYear],
    queryFn: () => idmsApi.getChargeOffMonthlyDetail(activeYear),
  })

  // Año anterior: solo para superponer la serie en la gráfica.
  const priorMonthlyQuery = useQuery({
    queryKey: ['idms', 'charge-offs', 'monthly-detail', activeYear - 1],
    queryFn: () => idmsApi.getChargeOffMonthlyDetail(activeYear - 1),
  })

  const detailQuery = useQuery({
    queryKey: ['idms', 'charge-offs', 'detail', activeYear],
    queryFn: () => idmsApi.getChargeOffs(activeYear),
  })

  const isLoading =
    sessionQuery.isLoading ||
    yearsQuery.isLoading ||
    overviewQuery.isLoading ||
    monthlyQuery.isLoading ||
    detailQuery.isLoading ||
    syncMutation.isPending ||
    syncMonthEndMutation.isPending

  return {
    session: sessionQuery.data,
    isAuthenticated: sessionQuery.data?.authenticated ?? false,
    mfaRequired: sessionQuery.data?.mfa_required ?? false,
    login: loginMutation.mutate,
    isLoginLoading: loginMutation.isPending,
    loginError: loginMutation.error?.message || null,

    years: yearsQuery.data ?? [],
    activeYear,
    setSelectedYear,

    sync: syncMutation.mutate,
    syncMonthEnd: syncMonthEndMutation.mutate,
    syncResult: syncMonthEndMutation.data ?? syncMutation.data,
    syncError:
      syncMutation.error?.message || syncMonthEndMutation.error?.message || null,

    overview: overviewQuery.data,
    monthly: monthlyQuery.data ?? [],
    priorMonthly: priorMonthlyQuery.data ?? [],
    detail: detailQuery.data ?? [],

    isLoading,
  }
}
