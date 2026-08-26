export interface IdmsSessionStatus {
  authenticated: boolean
  mfa_required: boolean
  message: string
}

export interface IdmsSyncResult {
  report_id: string
  year: number
  rows_inserted: number
  message: string
}

export interface IdmsChargeOff {
  id: string
  report_year: number
  acct_id: string
  borrower: string | null
  date_sold: string | null
  charge_off_date: string | null
  vin: string | null
  year: string | null
  make: string | null
  model: string | null
  original_balance: string
  original_total_balance: string
  total_recovery: string
  current_balance: string
  total_adjusted: string
  repo_method: string | null
  status: string | null
  acct_flags: string | null
  imported_at: string
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface IdmsChargeOffMonthly {
  year: number
  month: number
  month_name: string
  count: number
  original_balance: string
  current_balance: string
  total_recovery: string
  total_adjusted: string
}

export interface IdmsChargeOffKpis {
  year: number
  count: number
  total_original_balance: string
  total_current_balance: string
  total_recovery: string
  total_adjusted: string
  imported_at: string | null
}
