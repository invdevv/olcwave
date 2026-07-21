import { NavLink, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/auth'
import {
  HomeIcon,
  UsersIcon,
  UserCircleIcon,
  CubeIcon,
  LinkIcon,
  Cog6ToothIcon,
  ArrowLeftOnRectangleIcon,
  BoltIcon,
  ChevronLeftIcon,
} from '@heroicons/react/24/outline'

const nav = [
  { to: '/dashboard', label: 'Dashboard', icon: HomeIcon },
  { to: '/users', label: 'Users', icon: UsersIcon },
  { to: '/profiles', label: 'Profiles', icon: UserCircleIcon },
  { to: '/containers', label: 'Containers', icon: CubeIcon },
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
      flex flex-col transition-all duration-200 ${collapsed ? 'w-16' : 'w-60'}`}>
      {/* Logo */}
      <div className="h-14 flex items-center gap-2.5 px-4 border-b border-border shrink-0">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-accent/15 text-accent shrink-0">
          <BoltIcon className="w-4.5 h-4.5" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="text-sm font-semibold text-text-primary leading-tight truncate">OLC Wave</p>
            <p className="text-[10px] text-text-muted uppercase tracking-wider">Admin Panel</p>
          </div>
        )}
        <button
          onClick={onToggle}
          className={`ml-auto p-1 rounded-md text-text-muted hover:text-text-primary hover:bg-bg-hover
            transition-colors cursor-pointer ${collapsed ? 'hidden' : ''}`}
          title="Collapse sidebar"
        >
          <ChevronLeftIcon className="w-4 h-4" />
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3 overflow-y-auto">
        {!collapsed && (
          <p className="px-4 mb-1.5 text-[10px] font-semibold text-text-muted uppercase tracking-wider">Menu</p>
        )}
        <div className="px-2.5 space-y-0.5">
          {nav.map((item) => {
            const active = location.pathname === item.to
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={`group relative flex items-center gap-3 px-2.5 py-2 rounded-lg text-sm font-medium
                  transition-colors ${active
                    ? 'bg-accent/10 text-accent'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'}
                  ${collapsed ? 'justify-center' : ''}`}
                title={collapsed ? item.label : undefined}
              >
                {active && (
                  <span className="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-0.5 rounded-r-full bg-accent" />
                )}
                <item.icon className="w-4.5 h-4.5 shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </NavLink>
            )
          })}
        </div>
      </nav>

      {/* Collapsed expand button */}
      {collapsed && (
        <div className="px-2.5 pb-2 shrink-0">
          <button
            onClick={onToggle}
            className="flex items-center justify-center w-full py-2 rounded-lg text-text-muted
              hover:text-text-primary hover:bg-bg-hover transition-colors cursor-pointer"
            title="Expand sidebar"
          >
            <ChevronLeftIcon className="w-4 h-4 rotate-180" />
          </button>
        </div>
      )}

      {/* Footer / account */}
      <div className="p-2.5 border-t border-border shrink-0">
        {!collapsed && (
          <div className="flex items-center gap-2.5 px-2 py-2 mb-1">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-accent/15 text-accent text-xs font-semibold shrink-0">
              A
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-text-primary leading-tight truncate">admin</p>
              <p className="text-[10px] text-text-muted truncate">Administrator</p>
            </div>
          </div>
        )}
        <button
          onClick={logout}
          className={`flex items-center gap-3 w-full px-2.5 py-2 rounded-lg text-sm font-medium
            text-text-secondary hover:text-danger hover:bg-danger/10 transition-colors cursor-pointer
            ${collapsed ? 'justify-center' : ''}`}
          title={collapsed ? 'Logout' : undefined}
        >
          <ArrowLeftOnRectangleIcon className="w-4.5 h-4.5 shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  )
}
