export type UserRole = 'admin' | 'viewer'

export interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
  remember_me: boolean
}

// The refresh token is never in the body: the backend sets it as an httpOnly cookie.
export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface PasswordChangeData {
  current_password: string
  new_password: string
}

export interface MessageResponse {
  message: string
}
