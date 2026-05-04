import { useState } from 'react'
import { authApi } from '@/models/authApi'
import { useAuthStore } from '@/store/authStore'

export function useAuth() {
  const [isLoading, setIsLoading] = useState(false)

  const user = useAuthStore((s) => s.user)
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const storeLogin = useAuthStore((s) => s.login)
  const storeLogout = useAuthStore((s) => s.logout)
  const setTokens = useAuthStore((s) => s.setTokens)

  async function login(email: string, password: string): Promise<void> {
    setIsLoading(true)
    try {
      const tokens = await authApi.login(email, password)
      // Set tokens before getMe so the request interceptor can attach them
      setTokens(tokens.access_token, tokens.refresh_token)
      const me = await authApi.getMe()
      storeLogin(tokens, me)
    } finally {
      setIsLoading(false)
    }
  }

  async function logout(): Promise<void> {
    try {
      await authApi.logout()
    } finally {
      storeLogout()
    }
  }

  return { user, isAuthenticated, login, logout, isLoading }
}
