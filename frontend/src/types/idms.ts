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

export interface IdmsSales {
  id: string
  report_year: number
  acct_id: string
  acct_type: string | null
  borrower: string | null
  booked_date: string | null
  contract_date: string | null
  vin: string | null
  sales_price: string
  cur_total_prin_bal_plus_tax: string
  cash_down: string
  deferred_down: string
  trade_in_acv: string
  trade_in_payoff: string
  year_model: string | null
  make: string | null
  model: string | null
  mileage: number | null
  inventory_cost: string
  cost_with_pack_fee: string
  total_expenses: string
  orig_payments: number | null
  orig_term_months: number | null
  regz_apr: string | null
  payment_frequency: string | null
  amount_financed: string
  finance_charge: string
  total_of_payments: string
  reg_payment: string
  monthly_payment: string
  sales_location: string | null
  salesperson: string | null
  city: string | null
  state: string | null
  zipcode: string | null
  referral: string | null
  gross_profit: string
  inventory_type: string | null
  days_on_lot: number | null
  status: string | null
  acct_flags: string | null
  udf_text_value1: string | null
  branch_name: string | null
  branch_desc: string | null
  portfolio_name: string | null
  source_name: string | null
  lender_name: string | null
  imported_at: string
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface IdmsSalesKpis {
  year: number
  count: number
  total_sales_price: string
  total_gross_profit: string
  total_cash_down: string
  total_amount_financed: string
  avg_gross_profit: string
  imported_at: string | null
}

export interface IdmsSalesMonthly {
  year: number
  month: number
  month_name: string
  count: number
  sales_price: string
  gross_profit: string
  amount_financed: string
}

export interface IdmsSalesBySalesperson {
  salesperson: string
  count: number
  sales_price: string
  gross_profit: string
}

export interface IdmsSalesByVehicle {
  make: string
  model: string
  count: number
  sales_price: string
  gross_profit: string
}
