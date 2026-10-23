import api from './api'
import { useAuthStore } from '@/store/authStore'
import type { ChatChunk, ChatRequest, ChatResponse } from '@/types/chat'

function postStream(req: ChatRequest) {
  const token = useAuthStore.getState().accessToken
  return fetch(`${import.meta.env.VITE_API_BASE_URL}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ ...req, stream: true }),
  })
}

export const chatApi = {
  complete: (req: ChatRequest) =>
    api.post<ChatResponse>('/chat/completions', req).then((r) => r.data),

  stream: async function* (req: ChatRequest): AsyncGenerator<ChatChunk> {
    let res = await postStream(req)
    if (res.status === 401) {
      // fetch bypasses the axios interceptors: a cheap authenticated call lets the
      // interceptor refresh the token (or log out), then retry once.
      await api.get('/auth/me')
      res = await postStream(req)
    }
    if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`)

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      // An SSE line can be split across network chunks: keep the trailing partial line.
      const lines = buffer.split('\n')
      buffer = lines.pop() ?? ''
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const payload = line.slice(6).trim()
        if (payload === '[DONE]') return
        yield JSON.parse(payload) as ChatChunk
      }
    }
  },
}
