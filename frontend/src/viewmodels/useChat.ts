import { useCallback, useState } from 'react'
import { chatApi } from '@/models/chatApi'
import type { ChatMessage } from '@/types/chat'

const TOOL_LABELS: Array<[string, string]> = [
  ['coverage', 'períodos disponibles'],
  ['idms', 'datos de IDMS'],
  ['sales', 'ventas'],
  ['hours', 'horas del taller'],
  ['technician', 'técnicos'],
  ['wip', 'órdenes en curso'],
  ['payment', 'pagos'],
  ['call', 'llamadas'],
]

function toolLabel(tool: string): string {
  const match = TOOL_LABELS.find(([key]) => tool.includes(key))
  return `Consultando ${match ? match[1] : 'datos'}…`
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [streamBuffer, setStreamBuffer] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTool, setActiveTool] = useState<string | null>(null)

  const send = useCallback(
    async (content: string) => {
      const userMsg: ChatMessage = { role: 'user', content }
      const nextMessages = [...messages, userMsg]
      setMessages(nextMessages)
      setIsLoading(true)
      setError(null)
      setStreamBuffer('')

      let accumulated = ''
      try {
        for await (const chunk of chatApi.stream({ messages: nextMessages })) {
          if (chunk.error) {
            setError(chunk.detail ?? chunk.error)
            break
          }
          if (chunk.done) break
          if (chunk.tool) {
            setActiveTool(toolLabel(chunk.tool))
            continue
          }
          setActiveTool(null)
          accumulated += chunk.delta
          setStreamBuffer(accumulated)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido')
      } finally {
        if (accumulated) {
          setMessages((prev) => [...prev, { role: 'assistant', content: accumulated }])
        }
        setIsLoading(false)
        setActiveTool(null)
        setStreamBuffer('')
      }
    },
    [messages],
  )

  const clear = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return { messages, streamBuffer, activeTool, isLoading, error, send, clear }
}
