import api from './api'
import type {
  CallAnalyticsKpis,
  CallAnalyticsRecord,
  CallByExtension,
  FetchResult,
  IsoRange,
} from '@/types/callAnalytics'

export const callAnalyticsApi = {
  list: (range: IsoRange) =>
    api
      .get<CallAnalyticsRecord[]>('/analytics/calls/', { params: { from: range.from, to: range.to } })
      .then((r) => r.data),

  kpis: (range: IsoRange) =>
    api
      .get<CallAnalyticsKpis>('/analytics/calls/kpis', { params: { from: range.from, to: range.to } })
      .then((r) => r.data),

  byExtension: (range: IsoRange) =>
    api
      .get<CallByExtension[]>('/analytics/calls/by-extension', { params: { from: range.from, to: range.to } })
      .then((r) => r.data),

  fetch: (body: { time_from: string; time_to: string }) =>
    api.post<FetchResult>('/analytics/calls/fetch', body).then((r) => r.data),
}
