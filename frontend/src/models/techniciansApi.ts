import api from './api'
import type { Technician, TechnicianMetric, TechnicianRankingItem } from '@/types/technician'

export interface DateRangeParams {
  from: string
  to: string
}

export interface RankingParams extends DateRangeParams {
  metric?: TechnicianMetric | 'labor'
}

export const techniciansApi = {
  list: (params: DateRangeParams) =>
    api.get<Technician[]>('/technicians/', { params }).then((r) => r.data),

  getRanking: (params: RankingParams) =>
    api
      .get<TechnicianRankingItem[]>('/technicians/ranking', { params })
      .then((r) => r.data),

  getByName: (name: string, params: DateRangeParams) =>
    api
      .get<Technician[]>(`/technicians/${encodeURIComponent(name)}`, { params })
      .then((r) => r.data),
}
