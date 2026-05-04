import { useQuery } from '@tanstack/react-query'
import { techniciansApi } from '@/models/techniciansApi'
import type { DateRange } from '@/lib/dateRange'

export function useTechnicianDetail(name: string, range: DateRange) {
  const query = useQuery({
    queryKey: ['technicians', name, range],
    queryFn: () => techniciansApi.getByName(name, range),
    enabled: name.trim().length > 0,
  })

  return {
    technician: query.data ?? [],
    isLoading: query.isLoading,
    error: query.error,
  }
}
