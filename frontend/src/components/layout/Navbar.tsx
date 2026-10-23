import { Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'

interface NavbarProps {
  onLogout: () => void
  onMenuClick: () => void
}

export default function Navbar({ onLogout, onMenuClick }: NavbarProps) {
  const user = useAuthStore((s) => s.user)

  return (
    <header className="h-14 flex-shrink-0 flex items-center gap-3 px-4 lg:px-6 border-b border-gray-800 bg-gray-900">
      <button
        type="button"
        onClick={onMenuClick}
        aria-label="Abrir menú"
        className="lg:hidden -ml-1 p-2 rounded-md text-gray-300 hover:text-[#ffea00] hover:bg-gray-800 transition-colors"
      >
        <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <span className="lg:hidden text-base font-bold tracking-tight text-[#ffea00]">Automania</span>

      <div className="ml-auto flex items-center gap-4 min-w-0">
        <Link
          to="/profile"
          className="truncate max-w-[10rem] sm:max-w-none text-sm text-gray-300 hover:text-[#ffea00] transition-colors"
        >
          {user?.full_name ?? user?.email}
        </Link>
        <button
          onClick={onLogout}
          className="flex-shrink-0 text-sm font-medium text-gray-400 hover:text-[#ffea00] transition-colors"
        >
          Sign out
        </button>
      </div>
    </header>
  )
}
