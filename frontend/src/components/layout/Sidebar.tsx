import { NavLink } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { hasRole } from '@/lib/permissions'
import type { UserRole } from '@/types/auth'

interface NavItem {
  to: string
  label: string
  exact?: boolean
  roles?: UserRole[]
}

interface NavSection {
  title: string
  items: NavItem[]
}

const NAV_SECTIONS: NavSection[] = [
  {
    title: 'Taller',
    items: [
      { to: '/',            label: 'Overview',         exact: true },
      { to: '/sales',       label: 'Sales' },
      { to: '/hours',       label: 'Hours' },
      { to: '/technicians', label: 'Technicians' },
      { to: '/wip',         label: 'Work in Progress' },
    ]
  },

  {
    title: 'Finanzas',
    items: [
      { to: '/payment', label: 'Payment Report', roles: ['admin'] },
      { to: '/idms-reports', label: 'IDMS Reports' },
    ]
  },
  {
    title: 'Comunicaciones',
    items: [
      { to: '/calls', label: 'Call Analytics' },
    ]
  },
  {
    title: 'Administración',
    items: [
      { to: '/imports', label: 'Imports', roles: ['admin'] },
    ]
  },
  {
    title: 'Asistente IA',
    items: [
      { to: '/chat', label: 'Chat', roles: ['admin'] },
    ]
  }
]

export default function Sidebar() {
  const user = useAuthStore((s) => s.user)

  const visibleSections = NAV_SECTIONS
    .map((section) => ({
      ...section,
      items: section.items.filter((item) => hasRole(user, item.roles)),
    }))
    .filter((section) => section.items.length > 0)

  return (
    <aside className="w-56 flex-shrink-0 flex flex-col bg-white border-r border-gray-200">
      <div className="px-5 py-4 border-b border-gray-800 bg-gray-900">
        <span className="text-base font-bold tracking-tight text-[#ffea00]">Automania</span>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-4">
        {visibleSections.map((section) => (
          <div key={section.title} className="space-y-1">
            <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              {section.title}
            </h3>
            <div className="space-y-0.5">
              {section.items.map(({ to, label, exact }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={exact}
                  className={({ isActive }) =>
                    `flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-yellow-50 text-gray-900 font-semibold border-l-2 border-[#ffea00]'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 border-l-2 border-transparent'
                    }`
                  }
                >
                  {label}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  )
}