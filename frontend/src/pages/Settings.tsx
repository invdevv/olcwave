import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { settingsApi, type RuntimeSettings } from '../api/settings'
import { useAuthStore } from '../store/auth'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import { Card, CardHeader } from '../components/ui/Misc'
import { ToastContainer } from '../components/containers/Toast'
import { useToasts } from '../components/containers/useToasts'
import { bytesToGB, gbToBytes } from '../utils/format'
import {
  ArrowLeftOnRectangleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'

export default function Settings() {
  const logout = useAuthStore((s) => s.logout)
  const apiUrl = import.meta.env.VITE_API_URL
  const { toasts, dismiss, success, error: toastError } = useToasts()
  const queryClient = useQueryClient()

  const { data: settings, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: () => settingsApi.get().then((r) => r.data),
  })

  const [subName, setSubName] = useState('')
  const [defaultTrafficGb, setDefaultTrafficGb] = useState('')
  const [collectInterval, setCollectInterval] = useState('')

  useEffect(() => {
    if (!settings) return

    setSubName(settings.sub_name)
    setDefaultTrafficGb(bytesToGB(settings.default_traffic_limit).toFixed(2))
    setCollectInterval(String(settings.traffic_collect_interval))
  }, [settings])

  const saveMutation = useMutation({
    mutationFn: (data: RuntimeSettings) => settingsApi.update(data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
      success('Settings saved')
    },
    onError: (err) => {
      toastError(
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
          'Failed to save settings',
      )
    },
  })

  const handleSave = () => {
    saveMutation.mutate({
      sub_name: subName,
      default_traffic_limit: gbToBytes(parseFloat(defaultTrafficGb) || 0),
      traffic_collect_interval: parseInt(collectInterval, 10) || 10,
    })
  }

  return (
    <div className="max-w-2xl space-y-5">
      <Card>
        <CardHeader title="Traffic settings" />
        <div className="px-5 py-4 space-y-4">
          <Input
            label="Subscription name"
            value={subName}
            onChange={(e) => setSubName(e.target.value)}
            placeholder="My VPN"
            hint="Service name used in subscriptions"
            disabled={isLoading}
          />
          <Input
            label="Default traffic limit (GB)"
            type="number"
            min="0"
            step="0.1"
            value={defaultTrafficGb}
            onChange={(e) => setDefaultTrafficGb(e.target.value)}
            placeholder="e.g. 100"
            hint="Default traffic limit for new users"
            disabled={isLoading}
          />
          <Input
            label="Traffic collect interval (seconds)"
            type="number"
            min="1"
            step="1"
            value={collectInterval}
            onChange={(e) => setCollectInterval(e.target.value)}
            placeholder="e.g. 10"
            hint="How often backend checks container traffic usage"
            disabled={isLoading}
          />
          <div className="flex justify-end pt-1">
            <Button onClick={handleSave} loading={saveMutation.isPending} disabled={isLoading}>
              Save settings
            </Button>
          </div>
        </div>
      </Card>

      {/* <Card>
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
      </Card> */}

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

      <ToastContainer toasts={toasts} onDismiss={dismiss} />
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
