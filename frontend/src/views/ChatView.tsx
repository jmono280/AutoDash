import { useEffect, useRef } from 'react'
import { useChat } from '@/viewmodels/useChat'
import Spinner from '@/components/ui/Spinner'

export default function ChatView() {
  const { messages, streamBuffer, isLoading, error, send, clear } = useChat()

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

  const handleSubmit = (e: { preventDefault(): void }) => {
    e.preventDefault()
    submitInput()
  }

  const handleKeyDown = (e: { key: string; shiftKey: boolean; preventDefault(): void }) => {
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
          <span className="flex items-center gap-1.5 text-xs text-emerald-600">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Con datos del taller
          </span>
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
            <p className="text-sm">Pregunta sobre ventas, horas, técnicos, WIP, pagos o llamadas.</p>
            <p className="text-xs mt-1">El AI tiene acceso a todos los datos del mes actual.</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap ${
                msg.role === 'user'
                  ? 'bg-[#ffea00] text-gray-900 rounded-br-sm'
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
          className="flex-1 resize-none rounded-xl border border-gray-300 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#ffea00] disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="rounded-xl bg-[#ffea00] px-4 py-2.5 text-sm font-medium text-gray-900 hover:bg-yellow-400 disabled:opacity-50 transition-colors"
        >
          Enviar
        </button>
      </form>
    </div>
  )
}
