import { useEffect, useMemo, useRef } from 'react'
import { defaultRange } from '@/lib/dateRange'
import { useOverview } from '@/viewmodels/useOverview'
import { useTechnicians } from '@/viewmodels/useTechnicians'
import { useChat } from '@/viewmodels/useChat'
import Spinner from '@/components/ui/Spinner'
import type { SalesKpis } from '@/types/sales'
import type { HoursKpis } from '@/types/hours'
import type { WipKpis, AgingBucket } from '@/types/wip'
import type { TechnicianRankingItem } from '@/types/technician'

const RANGE = defaultRange()

function buildContext(
  salesKpis: SalesKpis | undefined,
  hoursKpis: HoursKpis | undefined,
  wipKpis: WipKpis | undefined,
  aging: AgingBucket[] | undefined,
  ranking: TechnicianRankingItem[] | undefined,
): string | undefined {
  if (!salesKpis && !wipKpis) return undefined

  const lines: string[] = []

  if (salesKpis) {
    lines.push(
      `Ventas: ${salesKpis.total_cars} cars | Gross $${parseFloat(salesKpis.total_gross).toFixed(0)} | Profit $${parseFloat(salesKpis.total_profit).toFixed(0)} | Profit% ${parseFloat(salesKpis.profit_pct).toFixed(1)}%`,
    )
  }
  if (hoursKpis) {
    lines.push(
      `Horas: Labor $${parseFloat(hoursKpis.labor_dollars).toFixed(0)} | Vendidas ${parseFloat(hoursKpis.hours_sold).toFixed(1)}h | Advisor Eff ${parseFloat(hoursKpis.advisor_efficiency).toFixed(1)}% | Tech Prof ${parseFloat(hoursKpis.technician_proficiency).toFixed(1)}%`,
    )
  }
  if (wipKpis) {
    lines.push(
      `WIP: ${wipKpis.total_ros} ROs | Avg ${parseFloat(wipKpis.avg_days_open).toFixed(1)}d | Oldest ${wipKpis.oldest_ro_days}d`,
    )
  }
  if (aging && aging.length > 0) {
    lines.push(`Aging: ${aging.map((b) => `${b.bucket}:${b.count}`).join(' | ')}`)
  }
  if (ranking && ranking.length > 0) {
    const top = ranking
      .slice(0, 3)
      .map(
        (t, i) =>
          `${i + 1}.${t.technician_name} ${parseFloat(t.hours_sold).toFixed(1)}h${
            t.technician_proficiency
              ? ` prof${parseFloat(t.technician_proficiency).toFixed(0)}%`
              : ''
          }`,
      )
      .join(' | ')
    lines.push(`Top técnicos: ${top}`)
  }

  return lines.join('\n')
}

export default function ChatView() {
  const { salesKpis, hoursKpis, wipKpis, aging, isLoading: isLoadingData } = useOverview(RANGE)
  const { ranking } = useTechnicians(RANGE)

  const context = useMemo(
    () => buildContext(salesKpis, hoursKpis, wipKpis, aging, ranking),
    [salesKpis, hoursKpis, wipKpis, aging, ranking],
  )

  const { messages, streamBuffer, isLoading, error, send, clear } = useChat(context)

  const inputRef = useRef<HTMLTextAreaElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamBuffer])

  const submitInput = () => {
    const val = inputRef.current?.value.trim()
    if (!val || isLoading) return
    inputRef.current!.value = ''
    send(val)
  }

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    submitInput()
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submitInput()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Chat</h1>
          <p className="text-sm text-gray-500 mt-0.5">Consulta métricas con lenguaje natural</p>
        </div>
        <div className="flex items-center gap-3">
          {isLoadingData ? (
            <span className="flex items-center gap-1.5 text-xs text-gray-400">
              <span className="h-2 w-2 rounded-full bg-gray-300 animate-pulse" />
              Cargando datos…
            </span>
          ) : context ? (
            <span className="flex items-center gap-1.5 text-xs text-emerald-600">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              Con contexto del dashboard
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-xs text-amber-500">
              <span className="h-2 w-2 rounded-full bg-amber-400" />
              Sin datos importados
            </span>
          )}
          {messages.length > 0 && (
            <button
              onClick={clear}
              className="text-xs text-gray-400 hover:text-gray-600 border border-gray-200 rounded-md px-3 py-1.5"
            >
              Nueva conversación
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 pb-4 min-h-0">
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-400 py-16">
            <p className="text-sm">Pregunta sobre ventas, horas, técnicos o trabajo en progreso.</p>
            <p className="text-xs mt-1">
              {context
                ? 'El AI tiene acceso a los datos del mes actual.'
                : 'Importa datos para que el AI responda con contexto real.'}
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap ${
                msg.role === 'user'
                  ? 'bg-purple-600 text-white rounded-br-sm'
                  : 'bg-gray-100 text-gray-800 rounded-bl-sm'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {streamBuffer && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-2xl rounded-bl-sm px-4 py-2.5 text-sm bg-gray-100 text-gray-800 whitespace-pre-wrap">
              {streamBuffer}
              <span className="animate-pulse ml-0.5">|</span>
            </div>
          </div>
        )}

        {isLoading && !streamBuffer && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-sm px-4 py-2.5 bg-gray-100">
              <Spinner size="sm" />
            </div>
          </div>
        )}

        {error && (
          <div className="rounded-lg px-4 py-3 text-sm bg-red-50 text-red-600 border border-red-100">
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex items-end gap-2 pt-4 border-t border-gray-200">
        <textarea
          ref={inputRef}
          rows={1}
          disabled={isLoading}
          placeholder="Escribe tu pregunta… (Enter para enviar, Shift+Enter para nueva línea)"
          onKeyDown={handleKeyDown}
          className="flex-1 resize-none rounded-xl border border-gray-300 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="rounded-xl bg-purple-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50 transition-colors"
        >
          Enviar
        </button>
      </form>
    </div>
  )
}
