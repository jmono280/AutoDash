import api from './api'
import type {
  CollectionStat,
  PaymentByCollector,
  PaymentByMethod,
  PaymentDateRange,
  PaymentKpis,
  PaymentPage,
} from '@/types/paymentReport'

export const paymentReportApi = {
  transactions: (range: PaymentDateRange, collector?: string, page = 1, limit = 20) =>
    api
      .get<PaymentPage>('/payment/transactions', {
        params: { from: range.from, to: range.to, collector: collector || undefined, page, limit },
      })
      .then((r) => r.data),

  kpis: (range: PaymentDateRange) =>
    api
      .get<PaymentKpis>('/payment/transactions/kpis', {
        params: { from: range.from, to: range.to },
      })
      .then((r) => r.data),

  byCollector: (range: PaymentDateRange) =>
    api
      .get<PaymentByCollector[]>('/payment/transactions/by-collector', {
        params: { from: range.from, to: range.to },
      })
      .then((r) => r.data),

  byMethod: (range: PaymentDateRange) =>
    api
      .get<PaymentByMethod[]>('/payment/transactions/by-method', {
        params: { from: range.from, to: range.to },
      })
      .then((r) => r.data),

  collectionStats: (range: PaymentDateRange) =>
    api
      .get<CollectionStat[]>('/payment/collection-stats', {
        params: { from: range.from, to: range.to },
      })
      .then((r) => r.data),
}
