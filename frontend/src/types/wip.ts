export interface Wip {
  id: string
  shop_number: number
  ro_number: string
  op_code: string
  supplier: string | null
  advisor: string | null
  opened: string
  days_open: number
  customer: string
  stock_other_id: string | null
  vehicle: string
  vin: string
  estimated: string | null
  category: string
  cog: string
  col: string
  imported_at: string
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface WipKpis {
  total_ros: number
  total_estimated: string
  total_cog: string
  total_col: string
  avg_days_open: string
  oldest_ro_days: number
  imported_at: string | null
}

export interface AgingBucket {
  bucket: string
  count: number
  total_estimated: string
}

export interface CategoryGroup {
  category: string
  count: number
  total_cog: string
  total_estimated: string
}

export interface AdvisorGroup {
  advisor: string | null
  count: number
  total_estimated: string
  avg_days_open: string
}

export interface Page<T> {
  items: T[]
  total: number
  page: number
  limit: number
  pages: number
}
