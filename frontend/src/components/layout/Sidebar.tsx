import { NavLink, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/auth'
import {
  HomeIcon,
  UsersIcon,
  UserCircleIcon,
  LinkIcon,
  Cog6ToothIcon,
  ArrowLeftOnRectangleIcon,
  BoltIcon,
} from '@heroicons/react/24/outline'

const nav = [
  { to: '/dashboard', label: 'Dashboard', icon: HomeIcon },
  { to: '/users', label: 'Users', icon: UsersIcon },
  { to: '/profiles', label: 'Profiles', icon: UserCircleIcon },
  { to: '/subscriptions', label: 'Subscriptions', icon: LinkIcon },
  { to: '/settings', label: 'Settings', icon: Cog6ToothIcon },
]

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

export default function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const logout = useAuthStore((s) => s.logout)
  const location = useLocation()

  return (
    <aside className={`fixed left-0 top-0 h-full bg-bg-secondary border-r border-border z-30
      flex flex-col transition-all duration-200 ${collapsed ? 'w-14' : 'w-52'}`}>
      {/* Logo */}
      <div className="h-12 flex items-center gap-2 px-3 border-b border-border shrink-0">
        <button onClick={onToggle} className="text-accent hover:text-accent-hover cursor-pointer shrink-0">
          <BoltIcon className="w-5 h-5" />
        </button>
        {!collapsed && (
          <span className="text-sm font-bold text-text-primary truncate">OLC Wave</span>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 py-2 overflow-y-auto">
        {nav.map((item) => {
          const active = location.pathname === item.to
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={`flex items-center gap-2.5 mx-2 px-2.5 py-2 rounded-md text-sm transition-colors
                ${active
                  ? 'bg-accent/10 text-accent'
                  : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'}
                ${collapsed ? 'justify-center' : ''}`}
              title={collapsed ? item.label : undefined}
            >
              <item.icon className="w-4 h-4 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          )
        })}
      </nav>

      {/* Logout */}
      <div className="p-2 border-t border-border shrink-0">
        <button
          onClick={logout}
          className={`flex items-center gap-2.5 w-full px-2.5 py-2 rounded-md text-sm
            text-text-secondary hover:text-danger hover:bg-danger/10 transition-colors cursor-pointer
            ${collapsed ? 'justify-center' : ''}`}
          title={collapsed ? 'Logout' : undefined}
        >
          <ArrowLeftOnRectangleIcon className="w-4 h-4 shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  )
}
