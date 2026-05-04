export interface ImportResult {
  rows_inserted: number
  rows_updated: number
  period_start: string | null
  period_end: string | null
  file_type: string
  message: string
}
