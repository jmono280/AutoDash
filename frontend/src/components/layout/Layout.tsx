import { useAuth } from '@/viewmodels/useAuth'
import Navbar from './Navbar'
import Sidebar from './Sidebar'

export default function Layout({ children }: { children: React.ReactNode }) {
  const { logout } = useAuth()

  async function handleLogout() {
    try {
      await logout()
    } finally {
      window.location.href = '/login'
    }
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-100">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0">
        <Navbar onLogout={handleLogout} />
        <main className="flex-1 overflow-y-auto p-6 flex flex-col min-h-0">{children}</main>
      </div>
    </div>
  )
}
