import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { subscriptionsApi } from '../api/subscriptions'
import type { SubscriptionBundle } from '../types'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import { Card, CardHeader, LoadingState, ErrorState, EmptyState } from '../components/ui/Misc'
import {
  MagnifyingGlassIcon,
  LinkIcon,
  ServerIcon,
  CheckCircleIcon,
  ClipboardDocumentIcon,
  CheckIcon,
} from '@heroicons/react/24/outline'

export default function Subscriptions() {
  const [uuid, setUuid] = useState('')
  const [activeUuid, setActiveUuid] = useState('')

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['subscription', activeUuid],
    queryFn: () => subscriptionsApi.getBundle(activeUuid).then((r) => r.data as SubscriptionBundle),
    enabled: !!activeUuid,
    retry: false,
  })

  const handleSearch = () => {
    if (uuid.trim()) setActiveUuid(uuid.trim())
  }

  const publicUrl = activeUuid ? `${window.location.origin}/sub/${activeUuid}` : ''

  return (
    <div className="space-y-5">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            value={uuid}
            onChange={(e) => setUuid(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Enter short UUID to view subscription..."
            className="w-full h-9 bg-bg-tertiary border border-border rounded-md pl-9 pr-3 text-sm text-text-primary
              placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/30 transition-all"
          />
        </div>
        <Button onClick={handleSearch}>
          <MagnifyingGlassIcon className="w-4 h-4" />
          Fetch
        </Button>
      </div>

      {activeUuid && <PublicUrlCard url={publicUrl} />}

      {isLoading && <Card><LoadingState text="Fetching subscription bundle..." /></Card>}
      {isError && (
        <Card>
          <ErrorState
            message={(error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to fetch subscription'}
            onRetry={() => refetch()}
          />
        </Card>
      )}
      {data && <SubscriptionBundleView bundle={data} />}
      {!activeUuid && !isLoading && (
        <Card>
          <EmptyState
            message="No subscription loaded"
            hint="Enter a user's short UUID above to inspect their subscription bundle and locations."
            icon={<LinkIcon className="w-6 h-6" />}
          />
        </Card>
      )}
    </div>
  )
}

function PublicUrlCard({ url }: { url: string }) {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(url)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <Card className="p-4 flex items-center gap-3 animate-fade-in">
      <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-accent/10 text-accent shrink-0">
        <LinkIcon className="w-4.5 h-4.5" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-text-muted mb-0.5">Public Subscription URL</p>
        <code className="text-xs text-accent font-mono break-all">{url}</code>
      </div>
      <Button variant="secondary" size="sm" onClick={copy}>
        {copied ? <CheckIcon className="w-3.5 h-3.5 text-success" /> : <ClipboardDocumentIcon className="w-3.5 h-3.5" />}
        {copied ? 'Copied' : 'Copy'}
      </Button>
    </Card>
  )
}

function SubscriptionBundleView({ bundle }: { bundle: SubscriptionBundle }) {
  return (
    <div className="space-y-5 animate-fade-in">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatBox label="Version" value={String(bundle.version)} />
        <StatBox label="Active Location" value={bundle.active_location_id} mono />
        <StatBox label="Locations" value={String(bundle.locations.length)} />
      </div>

      <Card className="overflow-hidden">
        <CardHeader title="Locations" />
        <div className="divide-y divide-border">
          {bundle.locations.map((loc) => {
            const isActive = loc.storage_id === bundle.active_location_id
            return (
              <div key={loc.storage_id} className="px-5 py-4 hover:bg-bg-hover transition-colors">
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <ServerIcon className="w-4 h-4 text-text-muted shrink-0" />
                    <span className="text-sm font-medium text-text-primary truncate">{loc.name}</span>
                    {loc.transport?.type != null && (
                      <Badge variant="info">{String(loc.transport.type)}</Badge>
                    )}
                  </div>
                  {isActive && (
                    <span className="flex items-center gap-1 text-xs text-success shrink-0">
                      <CheckCircleIcon className="w-4 h-4" /> Active
                    </span>
                  )}
                </div>
                <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-xs">
                  <DetailRow label="Storage ID" value={loc.storage_id} />
                  <DetailRow label="Auth" value={loc.auth_provider} />
                  <div className="sm:col-span-2">
                    <DetailRow label="Room ID" value={loc.endpoint.room_id} />
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </Card>
    </div>
  )
}

function StatBox({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <Card className="p-4">
      <p className="text-xs text-text-muted">{label}</p>
      <p className={`mt-1 text-text-primary truncate ${mono ? 'text-sm font-mono' : 'text-2xl font-bold tabular-nums'}`}>
        {value}
      </p>
    </Card>
  )
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-2 min-w-0">
      <span className="text-text-muted shrink-0">{label}:</span>
      <span className="text-text-secondary font-mono truncate">{value}</span>
    </div>
  )
}
