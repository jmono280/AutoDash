import type { User, UserRole } from '@/types/auth'

export function hasRole(user: User | null, allowedRoles?: UserRole[]): boolean {
  if (!allowedRoles || allowedRoles.length === 0) {
    return true
  }
  if (!user) {
    return false
  }
  return allowedRoles.includes(user.role)
}
