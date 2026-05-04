export interface HoursSummary {
  id: string
  shop_name: string
  labor_dollars: string
  hours_sold: string
  hours_paid: string
  hours_worked: string
  actual_hours: string
  advisor_efficiency: string
  technician_proficiency: string
  technician_productivity: string
  technician_efficiency: string | null
  period_start: string
  period_end: string
  imported_at: string
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface HoursKpis {
  labor_dollars: string
  hours_sold: string
  hours_paid: string
  hours_worked: string
  actual_hours: string
  advisor_efficiency: string
  technician_proficiency: string
  technician_productivity: string
  technician_efficiency: string | null
  imported_at: string | null
}
