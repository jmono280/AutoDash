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

  const kpisQuery = useQuery({
    queryKey: ['idms', 'charge-offs', 'kpis', activeYear],
    queryFn: () => idmsApi.getChargeOffKpis(activeYear!),
    enabled: activeYear !== null,
  })

  const monthlyQuery = useQuery({
    queryKey: ['idms', 'charge-offs', 'monthly', activeYear],
    queryFn: () => idmsApi.getChargeOffMonthly(activeYear!),
    enabled: activeYear !== null,
  })

  const detailQuery = useQuery({
    queryKey: ['idms', 'charge-offs', 'detail', activeYear],
    queryFn: () => idmsApi.getChargeOffs(activeYear!),
    enabled: activeYear !== null,
  })

  const isLoading =
    sessionQuery.isLoading ||
    yearsQuery.isLoading ||
    kpisQuery.isLoading ||
    monthlyQuery.isLoading ||
    detailQuery.isLoading ||
    syncMutation.isPending

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
    syncResult: syncMutation.data,
    syncError: syncMutation.error?.message || null,

    kpis: kpisQuery.data,
    monthly: monthlyQuery.data ?? [],
    detail: detailQuery.data ?? [],

    isLoading,
  }
}
