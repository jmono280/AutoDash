import { useCallback, useState } from 'react'
import { chatApi } from '@/models/chatApi'
import type { ChatMessage } from '@/types/chat'

export function useChat(context?: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [streamBuffer, setStreamBuffer] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
        for await (const chunk of chatApi.stream({ messages: nextMessages, context })) {
          if (chunk.error) {
            setError(chunk.detail ?? chunk.error)
            break
          }
          if (chunk.done) break
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
        setStreamBuffer('')
      }
    },
    [messages, context],
  )

  const clear = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return { messages, streamBuffer, isLoading, error, send, clear }
}
