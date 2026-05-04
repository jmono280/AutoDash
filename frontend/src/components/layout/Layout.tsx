import { useAuthStore } from '@/store/authStore'
import Navbar from './Navbar'
import Sidebar from './Sidebar'

export default function Layout({ children }: { children: React.ReactNode }) {
  const logout = useAuthStore((s) => s.logout)

  function handleLogout() {
    logout()
    window.location.href = '/login'
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0">
        <Navbar onLogout={handleLogout} />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  )
}
