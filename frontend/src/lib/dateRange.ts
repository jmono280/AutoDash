import { endOfMonth, format, parseISO, startOfMonth } from 'date-fns'
import { es } from 'date-fns/locale'

export interface DateRange {
  from: string // 'YYYY-MM-DD'
  to: string
}

export function defaultRange(): DateRange {
  const now = new Date()
  return {
    from: format(startOfMonth(now), 'yyyy-MM-dd'),
    to: format(endOfMonth(now), 'yyyy-MM-dd'),
  }
}

export function formatDate(d: Date): string {
  return format(d, 'yyyy-MM-dd')
}

export function formatImportedAt(iso: string | null | undefined): string | null {
  if (!iso) return null
  return format(parseISO(iso), "d MMM yyyy · HH:mm", { locale: es })
}
