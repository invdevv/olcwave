import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { subscriptionsApi } from '../api/subscriptions'
import type { SubscriptionBundle } from '../types'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import { LoadingState, ErrorState, EmptyState } from '../components/ui/Misc'
import { MagnifyingGlassIcon, LinkIcon, ServerIcon, CheckCircleIcon } from '@heroicons/react/24/outline'

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
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="flex-1 flex gap-2">
          <input
            value={uuid}
            onChange={(e) => setUuid(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Enter short UUID to view subscription..."
            className="flex-1 bg-bg-primary border border-border rounded-md px-3 py-2 text-sm text-text-primary
              placeholder:text-text-muted focus:outline-none focus:border-accent"
          />
          <Button onClick={handleSearch} variant="secondary">
            <MagnifyingGlassIcon className="w-4 h-4" />
            Fetch
          </Button>
        </div>
      </div>

      {activeUuid && (
        <div className="bg-bg-secondary border border-border rounded-lg p-3 flex items-center gap-3 animate-fade-in">
          <LinkIcon className="w-4 h-4 text-accent shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-xs text-text-muted mb-1">Public Subscription URL</p>
            <code className="text-xs text-accent font-mono break-all">{publicUrl}</code>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => navigator.clipboard.writeText(publicUrl)}
          >
            Copy
          </Button>
        </div>
      )}

      {isLoading && <LoadingState text="Fetching subscription bundle..." />}
      {isError && (
        <ErrorState
          message={(error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to fetch subscription'}
          onRetry={() => refetch()}
        />
      )}
      {data && <SubscriptionBundleView bundle={data} />}
      {!activeUuid && !isLoading && <EmptyState message="Enter a short UUID to view subscription details" />}
    </div>
  )
}

function SubscriptionBundleView({ bundle }: { bundle: SubscriptionBundle }) {
  return (
    <div className="space-y-3 animate-fade-in">
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-bg-secondary border border-border rounded-lg p-3">
          <p className="text-xs text-text-muted">Version</p>
          <p className="text-lg font-bold text-text-primary">{bundle.version}</p>
        </div>
        <div className="bg-bg-secondary border border-border rounded-lg p-3">
          <p className="text-xs text-text-muted">Active Location</p>
          <p className="text-xs font-mono text-text-primary mt-1 truncate">{bundle.active_location_id}</p>
        </div>
        <div className="bg-bg-secondary border border-border rounded-lg p-3">
          <p className="text-xs text-text-muted">Locations</p>
          <p className="text-lg font-bold text-text-primary">{bundle.locations.length}</p>
        </div>
      </div>

      <div className="bg-bg-secondary border border-border rounded-lg overflow-hidden">
        <div className="px-4 py-2.5 border-b border-border">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider">Locations</h3>
        </div>
        <div className="divide-y divide-border">
          {bundle.locations.map((loc, i) => (
            <div key={loc.storage_id} className="px-4 py-3 hover:bg-bg-hover transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ServerIcon className="w-4 h-4 text-text-muted" />
                  <span className="text-sm font-medium text-text-primary">{loc.name}</span>
                  <Badge variant="info">{loc.transport.type as string}</Badge>
                </div>
                <CheckCircleIcon className="w-4 h-4 text-success" />
              </div>
              <div className="mt-2 grid grid-cols-2 gap-x-6 gap-y-1 text-xs">
                <div>
                  <span className="text-text-muted">Storage ID: </span>
                  <span className="text-text-secondary font-mono">{loc.storage_id}</span>
                </div>
                <div>
                  <span className="text-text-muted">Auth: </span>
                  <span className="text-text-secondary font-mono">{loc.auth_provider}</span>
                </div>
                <div className="col-span-2">
                  <span className="text-text-muted">Room ID: </span>
                  <span className="text-text-secondary font-mono">{loc.endpoint.room_id}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
