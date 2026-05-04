import api from './api'
import type { HoursKpis, HoursSummary } from '@/types/hours'

export interface DateRangeParams {
  from: string
  to: string
}

export const hoursApi = {
  list: (params: DateRangeParams) =>
    api.get<HoursSummary[]>('/hours/', { params }).then((r) => r.data),

  getKpis: (params: DateRangeParams) =>
    api.get<HoursKpis>('/hours/kpis', { params }).then((r) => r.data),
}
