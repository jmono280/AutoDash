import api from './api'
import type {
  IdmsChargeOff,
  IdmsChargeOffKpis,
  IdmsChargeOffMonthly,
  IdmsChargeOffMonthlyDetail,
  IdmsChargeOffOverview,
  IdmsSessionStatus,
  IdmsSyncResult,
} from '@/types/idms'

export const idmsApi = {
  session: () =>
    api.get<IdmsSessionStatus>('/idms/session').then((r) => r.data),

  login: (otpCode?: string) =>
    api
      .post<IdmsSessionStatus>('/idms/login', { otp_code: otpCode })
      .then((r) => r.data),

  syncChargeOffs: (year: number) =>
    api
      .post<IdmsSyncResult>('/idms/charge-offs/sync', null, { params: { year } })
      .then((r) => r.data),

  getChargeOffYears: () =>
    api.get<number[]>('/idms/charge-offs/years').then((r) => r.data),

  getChargeOffKpis: (year: number) =>
    api
      .get<IdmsChargeOffKpis>('/idms/charge-offs/kpis', { params: { year } })
      .then((r) => r.data),

  getChargeOffMonthly: (year: number) =>
    api
      .get<IdmsChargeOffMonthly[]>('/idms/charge-offs/monthly', { params: { year } })
      .then((r) => r.data),

  getChargeOffs: (year: number) =>
    api
      .get<IdmsChargeOff[]>('/idms/charge-offs', { params: { year } })
      .then((r) => r.data),

  getChargeOffOverview: (year: number) =>
    api
      .get<IdmsChargeOffOverview>('/idms/charge-offs/overview', { params: { year } })
      .then((r) => r.data),

  getChargeOffMonthlyDetail: (year: number) =>
    api
      .get<IdmsChargeOffMonthlyDetail[]>('/idms/charge-offs/monthly-detail', {
        params: { year },
      })
      .then((r) => r.data),

  syncMonthEnd: () =>
    api.post<IdmsSyncResult>('/idms/month-end/sync').then((r) => r.data),
}
