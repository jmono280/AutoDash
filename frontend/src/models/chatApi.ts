import api from './api'
import { useAuthStore } from '@/store/authStore'
import type { ChatChunk, ChatRequest, ChatResponse } from '@/types/chat'

export const chatApi = {
  complete: (req: ChatRequest) =>
    api.post<ChatResponse>('/chat/completions', req).then((r) => r.data),

  stream: async function* (req: ChatRequest): AsyncGenerator<ChatChunk> {
    const token = useAuthStore.getState().accessToken
    const res = await fetch(
      `${import.meta.env.VITE_API_BASE_URL}/chat/completions`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ ...req, stream: true }),
      },
    )
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const reader = res.body!.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const text = decoder.decode(value, { stream: true })
      for (const line of text.split('\n')) {
        if (!line.startsWith('data: ')) continue
        const payload = line.slice(6).trim()
        if (payload === '[DONE]') return
        yield JSON.parse(payload) as ChatChunk
      }
    }
  },
}
