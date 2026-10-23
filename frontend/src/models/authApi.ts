import api from './api'
import type {
  LoginRequest,
  MessageResponse,
  PasswordChangeData,
  TokenResponse,
  User,
} from '@/types/auth'

export const authApi = {
  login: (data: LoginRequest) =>
    api.post<TokenResponse>('/auth/login', data).then((r) => r.data),

  // Uses the httpOnly refresh cookie sent by the browser
  refresh: () => api.post<TokenResponse>('/auth/refresh').then((r) => r.data),

  getMe: () => api.get<User>('/auth/me').then((r) => r.data),

  logout: () =>
    api.post<{ message: string }>('/auth/logout').then((r) => r.data),

  changePassword: (data: PasswordChangeData) =>
    api.post<MessageResponse>('/auth/change-password', data).then((r) => r.data),
}
