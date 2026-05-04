import { useAuthStore } from '@/store/authStore'

interface NavbarProps {
  onLogout: () => void
}

export default function Navbar({ onLogout }: NavbarProps) {
  const user = useAuthStore((s) => s.user)

  return (
    <header className="h-14 flex-shrink-0 flex items-center justify-end gap-4 px-6 border-b border-gray-100 bg-white">
      <span className="text-sm text-gray-500">{user?.full_name ?? user?.email}</span>
      <button
        onClick={onLogout}
        className="text-sm font-medium text-gray-500 hover:text-red-600 transition-colors"
      >
        Sign out
      </button>
    </header>
  )
}
