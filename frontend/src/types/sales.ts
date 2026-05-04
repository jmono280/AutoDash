export interface DailySales {
  id: string
  date: string
  day_of_week: string
  total_cars: number
  gross_sales: string
  net_sales: string
  sales: string
  ticket_average: string
  cost_of_goods: string
  cogs_percent: string
  gross_profit: string
  gross_profit_pct: string
  period_start: string
  period_end: string
  imported_at: string
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface SalesKpis {
  total_cars: number
  total_gross: string
  total_net: string
  avg_ticket: string
  total_cogs: string
  total_profit: string
  profit_pct: string
  cogs_pct: string
  imported_at: string | null
}

export interface TrendPoint {
  date: string
  gross_sales: string
  net_sales: string
  profit: string
}

export interface DayOfWeekStats {
  day_of_week: string
  avg_cars: string
  avg_gross: string
  count_days: number
}
