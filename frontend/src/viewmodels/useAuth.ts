import { useEffect, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { authApi } from '@/models/authApi'
import { useAuthStore } from '@/store/authStore'
import type { PasswordChangeData } from '@/types/auth'

// Shared across StrictMode double-mounts so the cookie refresh runs only once per page load
let restorePromise: Promise<void> | null = null

async function restoreSession(): Promise<void> {
  const { login, markSessionChecked, setAccessToken } = useAuthStore.getState()
  try {
    const { access_token } = await authApi.refresh()
    // Set the token before getMe so the request interceptor can attach it
    setAccessToken(access_token)
    const me = await authApi.getMe()
    login(access_token, me)
  } catch {
    // No valid refresh cookie: the user has to sign in
  } finally {
    markSessionChecked()
  }
}

/** On app start, try to resume the session from the httpOnly refresh cookie. */
export function useSessionRestore() {
  const sessionChecked = useAuthStore((s) => s.sessionChecked)

  useEffect(() => {
    if (!useAuthStore.getState().sessionChecked) {
      restorePromise ??= restoreSession()
    }
  }, [])

  return { sessionChecked }
}

export function useAuth() {
  const [isLoading, setIsLoading] = useState(false)

  const user = useAuthStore((s) => s.user)
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const sessionChecked = useAuthStore((s) => s.sessionChecked)
  const storeLogin = useAuthStore((s) => s.login)
  const storeLogout = useAuthStore((s) => s.logout)
  const setAccessToken = useAuthStore((s) => s.setAccessToken)

  async function login(email: string, password: string, rememberMe: boolean): Promise<void> {
    setIsLoading(true)
    try {
      const { access_token } = await authApi.login({ email, password, remember_me: rememberMe })
      // Set the token before getMe so the request interceptor can attach it
      setAccessToken(access_token)
      const me = await authApi.getMe()
      storeLogin(access_token, me)
    } finally {
      setIsLoading(false)
    }
  }

  async function logout(): Promise<void> {
    try {
      // Clears the refresh cookie on the server
      await authApi.logout()
    } finally {
      storeLogout()
    }
  }

  return { user, isAuthenticated, sessionChecked, login, logout, isLoading }
}

export function useChangePassword() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: PasswordChangeData) => authApi.changePassword(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auth', 'me'] })
    },
  })
}
