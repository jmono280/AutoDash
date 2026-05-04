import { create } from 'zustand'
import type { TokenResponse, User } from '@/types/auth'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  // computed
  isAuthenticated: boolean
  // actions
  login: (tokens: TokenResponse, user: User) => void
  logout: () => void
  setTokens: (accessToken: string, refreshToken: string) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,

  login: (tokens, user) =>
    set({
      user,
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      isAuthenticated: true,
    }),

  logout: () =>
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    }),

  setTokens: (accessToken, refreshToken) =>
    set({ accessToken, refreshToken }),
}))
