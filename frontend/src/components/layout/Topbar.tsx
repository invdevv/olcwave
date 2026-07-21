import { useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/auth'

const titles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/users': 'Users',
  '/profiles': 'Profiles',
  '/subscriptions': 'Subscriptions',
  '/settings': 'Settings',
}

export default function Topbar() {
  const location = useLocation()
  const title = titles[location.pathname] || 'Dashboard'

  return (
    <header className="h-12 bg-bg-secondary border-b border-border flex items-center justify-between px-4 shrink-0">
      <h1 className="text-sm font-semibold text-text-primary">{title}</h1>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-subtle" />
          <span className="text-xs text-text-muted">Connected</span>
        </div>
        <div className="w-px h-4 bg-border" />
        <span className="text-xs text-text-secondary">admin</span>
      </div>
    </header>
  )
}
