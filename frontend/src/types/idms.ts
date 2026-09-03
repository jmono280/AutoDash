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

export interface IdmsDelta {
  value: string
  pct: string
}

export interface IdmsChargeOffOverview {
  year: number
  months_with_data: number[]
  ytd_count: number
  ytd_total_charge_off: string
  ytd_avg_prin_bal: string
  delta_count: IdmsDelta
  delta_total_charge_off: IdmsDelta
  delta_avg_prin_bal: IdmsDelta
  mtd_count: number
  mtd_total_charge_off: string
  mtd_avg_prin_bal: string
  recovery_ratio: string
  gross_co_ratio: string
  annualized_co_ratio: string
  has_portfolio_data: boolean
}

export interface IdmsChargeOffMonthlyDetail {
  year: number
  month: number
  month_name: string
  principal_balance: string | null
  original_balance: string
  count: number
  current_balance: string
  recovery_acv: string
  recovery_ratio: string
  gross_co_ratio: string | null
  months_on_book: string | null
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
