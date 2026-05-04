import axios from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/store/authStore'

// Extend config type to carry the retry flag
declare module 'axios' {
  interface InternalAxiosRequestConfig {
    _retry?: boolean
  }
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

// ── Request: attach Bearer token ──────────────────────────────────────────────
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response: handle 401 → refresh → retry ───────────────────────────────────
let isRefreshing = false
let pendingQueue: Array<{
  resolve: (token: string) => void
  reject: (err: unknown) => void
}> = []

function flushQueue(err: unknown, token: string | null) {
  pendingQueue.forEach(({ resolve, reject }) =>
    err ? reject(err) : resolve(token!),
  )
  pendingQueue = []
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original: InternalAxiosRequestConfig = error.config

    // Only handle 401s that haven't already been retried
    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error as unknown)
    }

    const { refreshToken, setTokens, logout } = useAuthStore.getState()

    if (!refreshToken) {
      logout()
      window.location.href = '/login'
      return Promise.reject(error as unknown)
    }

    // If a refresh is already in flight, queue this request
    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        pendingQueue.push({ resolve, reject })
      }).then((newToken) => {
        original.headers.Authorization = `Bearer ${newToken}`
        return api(original)
      })
    }

    original._retry = true
    isRefreshing = true

    try {
      // Use a plain axios call to avoid re-triggering this interceptor
      const { data } = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL}/auth/refresh`,
        { refresh_token: refreshToken },
      )
      setTokens(data.access_token, data.refresh_token)
      flushQueue(null, data.access_token)
      original.headers.Authorization = `Bearer ${data.access_token}`
      return api(original)
    } catch (refreshErr) {
      flushQueue(refreshErr, null)
      logout()
      window.location.href = '/login'
      return Promise.reject(refreshErr)
    } finally {
      isRefreshing = false
    }
  },
)

export default api
