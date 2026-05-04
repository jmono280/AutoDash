export interface Technician {
  id: string
  technician_name: string
  labor_dollars: string
  hours_sold: string
  hours_paid: string
  hours_worked: string
  actual_hours: string
  technician_proficiency: string | null
  technician_productivity: string | null
  period_start: string
  period_end: string
  imported_at: string
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface TechnicianRankingItem {
  technician_name: string
  labor_dollars: string
  hours_sold: string
  hours_paid: string
  hours_worked: string
  actual_hours: string
  technician_proficiency: string | null
  technician_productivity: string | null
}

export type TechnicianMetric = 'labor_dollars' | 'hours_sold' | 'proficiency'
