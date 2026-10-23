import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { useAuth } from '@/viewmodels/useAuth'
import Navbar from './Navbar'
import Sidebar from './Sidebar'

export default function Layout({ children }: { children: React.ReactNode }) {
  const { logout } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { pathname } = useLocation()

  // Close the mobile drawer whenever the route changes
  useEffect(() => {
    setSidebarOpen(false)
  }, [pathname])

  useEffect(() => {
    if (!sidebarOpen) return
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSidebarOpen(false)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [sidebarOpen])

  async function handleLogout() {
    try {
      await logout()
    } finally {
      window.location.href = '/login'
    }
  }

  return (
    <div className="flex h-dvh overflow-hidden bg-gray-100">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          aria-hidden="true"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="flex flex-col flex-1 min-w-0">
        <Navbar onLogout={handleLogout} onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 overflow-y-auto p-4 lg:p-6 flex flex-col min-h-0">{children}</main>
      </div>
    </div>
  )
}
