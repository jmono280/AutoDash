import api from './api'
import type { ImportResult } from '@/types/imports'

function buildForm(file: File): FormData {
  const form = new FormData()
  form.append('file', file)
  return form
}

export const importsApi = {
  uploadDailySales: (file: File) =>
    api
      .post<ImportResult>('/imports/daily-sales', buildForm(file))
      .then((r) => r.data),

  uploadHoursSummary: (file: File) =>
    api
      .post<ImportResult>('/imports/hours-summary', buildForm(file))
      .then((r) => r.data),

  uploadHoursDetail: (file: File) =>
    api
      .post<ImportResult>('/imports/hours-detail', buildForm(file))
      .then((r) => r.data),

  uploadWip: (file: File) =>
    api
      .post<ImportResult>('/imports/work-in-progress', buildForm(file))
      .then((r) => r.data),
}
