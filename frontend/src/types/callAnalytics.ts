export interface CallAnalyticsRecord {
  id: string
  time_from: string
  time_to: string
  extension_number: string
  extension_name: string
  total_calls: number
  inbound: number
  outbound: number
  direct: number
  from_queue: number
  transferred: number
  portal_equiv: number
  duration_seconds: number
  external: number
  internal: number
  answered: number
  not_answered: number
  completed: number
  abandoned: number
  voicemail: number
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface CallAnalyticsKpis {
  total_calls: number
  total_inbound: number
  total_outbound: number
  total_answered: number
  total_not_answered: number
  total_completed: number
  total_abandoned: number
  total_voicemail: number
  total_duration_seconds: number
  extension_count: number
}

export interface CallByExtension {
  extension_number: string
  extension_name: string
  total_calls: number
  inbound: number
  outbound: number
  answered: number
  not_answered: number
  completed: number
  abandoned: number
  voicemail: number
  duration_seconds: number
}

export interface FetchResult {
  rows_saved: number
  time_from: string
  time_to: string
}

export interface IsoRange {
  from: string
  to: string
}
