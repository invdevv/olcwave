import { useAuthStore } from '../store/auth'
import Button from '../components/ui/Button'
import { Cog6ToothIcon, ArrowLeftOnRectangleIcon } from '@heroicons/react/24/outline'

export default function Settings() {
  const logout = useAuthStore((s) => s.logout)
  const apiUrl = import.meta.env.VITE_API_URL

  return (
    <div className="max-w-xl space-y-4">
      <div className="bg-bg-secondary border border-border rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <Cog6ToothIcon className="w-4 h-4 text-text-muted" />
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider">Application</h3>
        </div>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between py-1.5 border-b border-border">
            <span className="text-text-muted">API Base URL</span>
            <span className="text-text-primary font-mono">{apiUrl}</span>
          </div>
          <div className="flex justify-between py-1.5 border-b border-border">
            <span className="text-text-muted">Admin User</span>
            <span className="text-text-primary">admin</span>
          </div>
          <div className="flex justify-between py-1.5">
            <span className="text-text-muted">Token Storage</span>
            <span className="text-text-primary">localStorage</span>
          </div>
        </div>
      </div>

      <div className="bg-bg-secondary border border-border rounded-lg p-4">
        <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">Session</h3>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between py-1.5">
            <span className="text-text-muted">Token Expiry</span>
            <span className="text-text-primary">24 hours</span>
          </div>
        </div>
      </div>

      <div className="bg-bg-secondary border border-border rounded-lg p-4">
        <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">Danger Zone</h3>
        <Button variant="danger" onClick={logout}>
          <ArrowLeftOnRectangleIcon className="w-4 h-4" />
          Logout
        </Button>
      </div>
    </div>
  )
}
