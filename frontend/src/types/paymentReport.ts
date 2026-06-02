export interface PaymentTransaction {
  id:                  string
  period_start:        string
  period_end:          string
  payment_date:        string
  account_id:          number | null
  customer_name:       string
  payment_method:      string | null
  card_last_4:         number | null
  amount:              string
  convenience_fee:     string
  status:              string | null
  reason_code:         string | null
  payment_origin:      string | null
  collector:           string | null
  reference_number:    string | null
  notes:               string | null
  refund_amount:       string | null
  refund_date:         string | null
  refund_initiated_by: string | null
  imported_at:         string
  created_at:          string
  updated_at:          string
}

export interface PaymentKpis {
  total_payments:     number
  total_amount:       string
  total_fees:         string
  total_collected:    string
  total_refunds:      string
  avg_payment_amount: string
}

export interface CollectionStat {
  id:                 string
  period_start:       string
  period_end:         string
  collector:          string
  payments_count:     number
  payments_amount:    string
  autopay_created:    number
  promise_sent:       number
  promise_confirmed:  number
  messages_sent:      number
  notes_count:        number
  waived_fees_count:  number
  waived_fees_amount: string
  worked:             number
  imported_at:        string
}

export interface PaymentByCollector {
  collector:    string
  count:        number
  total_amount: string
}

export interface PaymentByMethod {
  payment_method: string
  count:          number
  total_amount:   string
}

export interface PaymentPage {
  items:  PaymentTransaction[]
  total:  number
  page:   number
  limit:  number
  pages:  number
}

export interface PaymentDateRange {
  from: string  // YYYY-MM-DD
  to:   string  // YYYY-MM-DD
}
