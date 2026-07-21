import { useLocation } from 'react-router-dom'

const pages: Record<string, { title: string; subtitle: string }> = {
  '/dashboard': { title: 'Dashboard', subtitle: 'Overview of your deployment' },
  '/users': { title: 'Users', subtitle: 'Manage user accounts and access' },
  '/profiles': { title: 'Profiles', subtitle: 'Configuration profiles' },
  '/containers': { title: 'Containers', subtitle: 'Manage OLCRtc containers' },
  '/subscriptions': { title: 'Subscriptions', subtitle: 'Inspect subscription bundles' },
  '/settings': { title: 'Settings', subtitle: 'Application configuration' },
}

export default function Topbar() {
  const location = useLocation()
  const page = pages[location.pathname] || pages['/dashboard']

  return (
    <header className="sticky top-0 z-20 h-14 bg-bg-secondary/80 backdrop-blur-md border-b border-border
      flex items-center justify-between px-6 shrink-0">
      <div className="min-w-0">
        <h1 className="text-base font-semibold text-text-primary leading-tight truncate">{page.title}</h1>
        <p className="text-xs text-text-muted truncate">{page.subtitle}</p>
      </div>
      <div className="flex items-center gap-3 shrink-0">
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-success/10 border border-success/20">
          <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-subtle" />
          <span className="text-xs font-medium text-success">Connected</span>
        </div>
        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-accent/15 text-accent text-xs font-semibold">
          A
        </div>
      </div>
    </header>
  )
}
