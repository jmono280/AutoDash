import api from './api'
import type {
  IdmsChargeOff,
  IdmsChargeOffKpis,
  IdmsChargeOffMonthly,
  IdmsChargeOffMonthlyDetail,
  IdmsChargeOffOverview,
  IdmsSales,
  IdmsSalesBySalesperson,
  IdmsSalesByVehicle,
  IdmsSalesKpis,
  IdmsSalesMonthly,
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

  syncSales: (year: number) =>
    api
      .post<IdmsSyncResult>('/idms/sales/sync', null, { params: { year } })
      .then((r) => r.data),

  importSalesHistorical: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api
      .post<IdmsSyncResult>('/idms/sales/import-historical', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data)
  },

  getSalesYears: () =>
    api.get<number[]>('/idms/sales/years').then((r) => r.data),

  getSalesKpis: (year: number) =>
    api
      .get<IdmsSalesKpis>('/idms/sales/kpis', { params: { year } })
      .then((r) => r.data),

  getSalesMonthly: (year: number) =>
    api
      .get<IdmsSalesMonthly[]>('/idms/sales/monthly', { params: { year } })
      .then((r) => r.data),

  getSales: (year: number) =>
    api.get<IdmsSales[]>('/idms/sales', { params: { year } }).then((r) => r.data),

  getSalesBySalesperson: (year: number) =>
    api
      .get<IdmsSalesBySalesperson[]>('/idms/sales/by-salesperson', {
        params: { year },
      })
      .then((r) => r.data),

  getSalesByVehicle: (year: number) =>
    api
      .get<IdmsSalesByVehicle[]>('/idms/sales/by-vehicle', { params: { year } })
      .then((r) => r.data),
}
