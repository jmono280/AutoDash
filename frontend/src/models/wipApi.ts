import api from './api'
import type {
  AdvisorGroup,
  AgingBucket,
  CategoryGroup,
  Page,
  Wip,
  WipKpis,
} from '@/types/wip'

export interface WipListParams {
  advisor?: string
  category?: string
  min_days?: number
  max_days?: number
  page?: number
  limit?: number
}

export const wipApi = {
  list: (params?: WipListParams) =>
    api.get<Page<Wip>>('/wip/', { params }).then((r) => r.data),

  getKpis: () => api.get<WipKpis>('/wip/kpis').then((r) => r.data),

  getAging: () => api.get<AgingBucket[]>('/wip/aging').then((r) => r.data),

  getByCategory: () =>
    api.get<CategoryGroup[]>('/wip/by-category').then((r) => r.data),

  getByAdvisor: () =>
    api.get<AdvisorGroup[]>('/wip/by-advisor').then((r) => r.data),
}
