import { useAuthStore } from '../store/auth'
import Button from '../components/ui/Button'
import { Card, CardHeader } from '../components/ui/Misc'
import {
  ArrowLeftOnRectangleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'

export default function Settings() {
  const logout = useAuthStore((s) => s.logout)
  const apiUrl = import.meta.env.VITE_API_URL

  return (
    <div className="max-w-2xl space-y-5">
      <Card>
        <CardHeader title="Application" />
        <div className="px-5 py-2">
          <Row label="API Base URL" value={apiUrl} mono />
          <Row label="Admin User" value="admin" />
          <Row label="Token Storage" value="localStorage" last />
        </div>
      </Card>

      <Card>
        <CardHeader title="Session" />
        <div className="px-5 py-2">
          <Row label="Token Expiry" value="24 hours" last />
        </div>
      </Card>

      <Card className="border-danger/20">
        <div className="px-5 py-3.5 border-b border-danger/20 flex items-center gap-2">
          <ExclamationTriangleIcon className="w-4 h-4 text-danger" />
          <h3 className="text-xs font-semibold text-danger uppercase tracking-wider">Danger Zone</h3>
        </div>
        <div className="p-5 flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-text-primary">Sign out</p>
            <p className="text-xs text-text-muted mt-0.5">End your current session and return to login.</p>
          </div>
          <Button variant="danger" onClick={logout}>
            <ArrowLeftOnRectangleIcon className="w-4 h-4" />
            Logout
          </Button>
        </div>
      </Card>
    </div>
  )
}

function Row({ label, value, mono, last }: { label: string; value: string; mono?: boolean; last?: boolean }) {
  return (
    <div className={`flex items-center justify-between gap-4 py-3 ${last ? '' : 'border-b border-border'}`}>
      <span className="text-sm text-text-secondary">{label}</span>
      <span className={`text-sm text-text-primary text-right truncate ${mono ? 'font-mono' : ''}`}>{value}</span>
    </div>
  )
}
