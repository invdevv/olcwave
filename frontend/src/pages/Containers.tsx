import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { containersApi } from '../api/containers'
import type { Container } from '../types'
import Button from '../components/ui/Button'
import { Card, ErrorState, EmptyState, Skeleton } from '../components/ui/Misc'
import ContainerCard from '../components/containers/ContainerCard'
import CodeModal from '../components/containers/CodeModal'
import { ToastContainer } from '../components/containers/Toast'
import { useToasts } from '../components/containers/useToasts'
import {
  MagnifyingGlassIcon,
  ArrowPathIcon,
  CubeIcon,
  UsersIcon,
  TagIcon,
} from '@heroicons/react/24/outline'

type GroupMode = 'user_id' | 'config_tag'

const groupOptions: { key: GroupMode; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: 'user_id', label: 'By User', icon: UsersIcon },
  { key: 'config_tag', label: 'By Config Tag', icon: TagIcon },
]

export default function Containers() {
  const [search, setSearch] = useState('')
  const [groupMode, setGroupMode] = useState<GroupMode>('user_id')
  const [logsTarget, setLogsTarget] = useState<Container | null>(null)
  const [configTarget, setConfigTarget] = useState<Container | null>(null)
  const { toasts, dismiss, success, error } = useToasts()

  const { data: containers, isLoading, isError, error: queryError, refetch, isFetching } = useQuery({
    queryKey: ['containers-all'],
    queryFn: () => containersApi.getAll().then((r) => r.data),
  })

  const filtered = useMemo(() => {
    if (!containers) return []
    const q = search.toLowerCase()
    return containers.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        c.user_id.toLowerCase().includes(q) ||
        c.config_tag.toLowerCase().includes(q) ||
        c.status.toLowerCase().includes(q)
    )
  }, [containers, search])

  const groups = useMemo(() => {
    const map = new Map<string, Container[]>()
    for (const c of filtered) {
      const key = c[groupMode]
      const arr = map.get(key)
      if (arr) arr.push(c)
      else map.set(key, [c])
    }
    return Array.from(map.entries()).sort(([a], [b]) => a.localeCompare(b))
  }, [filtered, groupMode])

  const runningCount = filtered.filter((c) => c.status === 'running').length

  return (
    <div className="space-y-5">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter containers..."
            className="w-full h-9 bg-bg-tertiary border border-border rounded-md pl-9 pr-3 text-sm text-text-primary
              placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/30 transition-all"
          />
        </div>
        <span className="text-xs text-text-muted tabular-nums">
          {filtered.length} containers · {runningCount} running
        </span>
        <GroupToggle mode={groupMode} onChange={setGroupMode} />
        <Button variant="secondary" onClick={() => refetch()}>
          <ArrowPathIcon className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Content */}
      {isError ? (
        <Card>
          <ErrorState
            message={(queryError as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to load containers'}
            onRetry={() => refetch()}
          />
        </Card>
      ) : isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-52 rounded-xl" />)}
        </div>
      ) : filtered.length === 0 ? (
        <Card>
          <EmptyState
            message={containers?.length === 0 ? 'No containers running' : 'No matching containers'}
            hint={containers?.length === 0 ? 'Containers appear here once profiles are launched for a user.' : 'Try adjusting your search filter.'}
            icon={<CubeIcon className="w-6 h-6" />}
          />
        </Card>
      ) : (
        <div className="space-y-6">
          {groups.map(([key, items]) => (
            <section key={key} className="space-y-3">
              <div className="flex items-center gap-2.5">
                <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
                  {groupMode === 'user_id' ? 'User' : 'Config Tag'}
                </h3>
                <code className="text-xs font-mono text-accent bg-accent/10 px-2 py-0.5 rounded">{key}</code>
                <span className="text-xs text-text-muted tabular-nums">{items.length}</span>
                <div className="flex-1 h-px bg-border" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {items.map((c) => (
                  <ContainerCard
                    key={c.id}
                    container={c}
                    onLogs={setLogsTarget}
                    onConfig={setConfigTarget}
                    onSuccess={success}
                    onError={error}
                  />
                ))}
              </div>
            </section>
          ))}
        </div>
      )}

      <LogsModal container={logsTarget} onClose={() => setLogsTarget(null)} />
      <ConfigModal container={configTarget} onClose={() => setConfigTarget(null)} />
      <ToastContainer toasts={toasts} onDismiss={dismiss} />
    </div>
  )
}

function GroupToggle({ mode, onChange }: { mode: GroupMode; onChange: (m: GroupMode) => void }) {
  return (
    <div className="inline-flex items-center gap-0.5 p-0.5 bg-bg-tertiary border border-border rounded-md">
      {groupOptions.map((opt) => {
        const active = mode === opt.key
        return (
          <button
            key={opt.key}
            onClick={() => onChange(opt.key)}
            className={`inline-flex items-center gap-1.5 h-7 px-2.5 text-xs font-medium rounded transition-all cursor-pointer
              ${active
                ? 'bg-accent text-white shadow-soft'
                : 'text-text-secondary hover:text-text-primary'}`}
          >
            <opt.icon className="w-3.5 h-3.5" />
            {opt.label}
          </button>
        )
      })}
    </div>
  )
}

function LogsModal({ container, onClose }: { container: Container | null; onClose: () => void }) {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['container-logs', container?.name],
    queryFn: () => containersApi.logs(container!.name).then((r) => r.data),
    enabled: !!container,
  })

  return (
    <CodeModal
      open={!!container}
      onClose={onClose}
      title={container ? `Logs — ${container.name}` : 'Logs'}
      description="Container output"
      content={data?.logs || ''}
      loading={isLoading}
      error={isError ? (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to load logs' : undefined}
      onRefresh={() => refetch()}
      refreshing={isFetching}
    />
  )
}

function ConfigModal({ container, onClose }: { container: Container | null; onClose: () => void }) {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['container-config', container?.name],
    queryFn: () => containersApi.getConfig(container!.name).then((r) => r.data),
    enabled: !!container,
  })

  return (
    <CodeModal
      open={!!container}
      onClose={onClose}
      title={container ? `Config — ${container.name}` : 'Config'}
      description="config.yaml"
      content={data?.config || ''}
      loading={isLoading}
      error={isError ? (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to load config' : undefined}
      onRefresh={() => refetch()}
      refreshing={isFetching}
    />
  )
}
