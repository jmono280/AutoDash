import { create } from 'zustand'
import type { User } from '@/types/auth'

// The access token lives only in memory. The refresh token is an httpOnly cookie
// managed by the backend, so JavaScript never sees it.
interface AuthState {
  user: User | null
  accessToken: string | null
  // computed
  isAuthenticated: boolean
  // true once the startup attempt to restore the session (cookie refresh) has finished
  sessionChecked: boolean
  // actions
  login: (accessToken: string, user: User) => void
  logout: () => void
  setAccessToken: (accessToken: string) => void
  markSessionChecked: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,
  sessionChecked: false,

  login: (accessToken, user) =>
    set({
      user,
      accessToken,
      isAuthenticated: true,
    }),

  logout: () =>
    set({
      user: null,
      accessToken: null,
      isAuthenticated: false,
    }),

  setAccessToken: (accessToken) => set({ accessToken }),

  markSessionChecked: () => set({ sessionChecked: true }),
}))
