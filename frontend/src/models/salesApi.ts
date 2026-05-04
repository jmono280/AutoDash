import api from './api'
import type { DailySales, DayOfWeekStats, SalesKpis, TrendPoint } from '@/types/sales'

export interface DateRangeParams {
  from: string
  to: string
}

export const salesApi = {
  list: (params: DateRangeParams) =>
    api.get<DailySales[]>('/sales/', { params }).then((r) => r.data),

  getKpis: (params: DateRangeParams) =>
    api.get<SalesKpis>('/sales/kpis', { params }).then((r) => r.data),

  getTrend: (params: DateRangeParams) =>
    api.get<TrendPoint[]>('/sales/trend', { params }).then((r) => r.data),

  getByDayOfWeek: (params: DateRangeParams) =>
    api.get<DayOfWeekStats[]>('/sales/by-day-of-week', { params }).then((r) => r.data),
}
