import { Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'

interface NavbarProps {
  onLogout: () => void
}

export default function Navbar({ onLogout }: NavbarProps) {
  const user = useAuthStore((s) => s.user)

  return (
    <header className="h-14 flex-shrink-0 flex items-center justify-end gap-4 px-6 border-b border-gray-800 bg-gray-900">
      <Link
        to="/profile"
        className="text-sm text-gray-300 hover:text-[#ffea00] transition-colors"
      >
        {user?.full_name ?? user?.email}
      </Link>
      <button
        onClick={onLogout}
        className="text-sm font-medium text-gray-400 hover:text-[#ffea00] transition-colors"
      >
        Sign out
      </button>
    </header>
  )
}
