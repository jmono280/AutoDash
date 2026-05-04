import { NavLink } from 'react-router-dom'

const NAV_SECTIONS = [
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
    title: 'Administración',
    items: [
      { to: '/imports',     label: 'Imports' },
    ]
  },
  {
    title: 'Asistente IA',
    items: [
      { to: '/chat', label: 'Chat' },
    ]
  }
]

export default function Sidebar() {
  return (
    <aside className="w-56 flex-shrink-0 flex flex-col bg-white border-r border-gray-200">
      <div className="px-5 py-5 border-b border-gray-100">
        <span className="text-base font-bold text-gray-900 tracking-tight">Automania</span>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-4">
        {NAV_SECTIONS.map((section) => (
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
                        ? 'bg-purple-50 text-purple-700'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
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