import api from './api'
import type { TokenResponse, User } from '@/types/auth'

export const authApi = {
  login: (email: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { email, password }).then((r) => r.data),

  refresh: (refreshToken: string) =>
    api
      .post<TokenResponse>('/auth/refresh', { refresh_token: refreshToken })
      .then((r) => r.data),

  getMe: () => api.get<User>('/auth/me').then((r) => r.data),

  logout: () =>
    api.post<{ message: string }>('/auth/logout').then((r) => r.data),
}
