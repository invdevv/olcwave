import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { containersApi } from '../api/containers'
import type { Container } from '../types'
import Button from '../components/ui/Button'
import AutoRefreshSelect from '../components/ui/AutoRefreshSelect'
import { Card, ErrorState, EmptyState, Skeleton } from '../components/ui/Misc'
import ContainerRow from '../components/containers/ContainerRow'
import CodeModal from '../components/containers/CodeModal'
import { ToastContainer } from '../components/containers/Toast'
import { useToasts } from '../components/containers/useToasts'
import { useAutoRefresh } from '../utils/useAutoRefresh'
import {
  MagnifyingGlassIcon,
  ArrowPathIcon,
  CubeIcon,
  UsersIcon,
  TagIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline'

type GroupMode = 'user_id' | 'config_tag'
type SortKey = 'user_id' | 'config_tag' | 'created' | 'status'
type SortDir = 'asc' | 'desc'

const COL_SPAN = 11

const groupOptions: { key: GroupMode; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: 'user_id', label: 'By User', icon: UsersIcon },
  { key: 'config_tag', label: 'By Config Tag', icon: TagIcon },
]

export default function Containers() {
  const [search, setSearch] = useState('')
  const [groupMode, setGroupMode] = useState<GroupMode>('user_id')
  const [sort, setSort] = useState<{ key: SortKey; dir: SortDir }>({ key: 'created', dir: 'desc' })
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [logsTarget, setLogsTarget] = useState<Container | null>(null)
  const [configTarget, setConfigTarget] = useState<Container | null>(null)
  const [refreshMs, setRefreshMs] = useAutoRefresh('containers')
  const { toasts, dismiss, success, error } = useToasts()

  const { data: containers, isLoading, isError, error: queryError, refetch, isFetching } = useQuery({
    queryKey: ['containers-all'],
    queryFn: () => containersApi.getAll().then((r) => r.data),
    refetchInterval: refreshMs || false,
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
    const compare = (a: Container, b: Container) => {
      const dir = sort.dir === 'asc' ? 1 : -1
      if (sort.key === 'created') {
        return (new Date(a.created).getTime() - new Date(b.created).getTime()) * dir
      }
      return a[sort.key].localeCompare(b[sort.key]) * dir
    }
    for (const arr of map.values()) arr.sort(compare)
    return Array.from(map.entries()).sort(([a], [b]) => a.localeCompare(b))
  }, [filtered, groupMode, sort])

  const runningCount = filtered.filter((c) => c.status === 'running').length

  const toggleSort = (key: SortKey) =>
    setSort((prev) => (prev.key === key ? { key, dir: prev.dir === 'asc' ? 'desc' : 'asc' } : { key, dir: 'asc' }))

  const toggleExpand = (id: string) =>
    setExpanded((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })

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
        <AutoRefreshSelect value={refreshMs} onChange={setRefreshMs} />
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
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-40 rounded-xl" />)}
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
              <Card className="overflow-hidden">
                <div className="overflow-x-auto max-h-[70vh]">
                  <table className="w-full text-sm border-collapse">
                    <thead className="sticky top-0 z-10">
                      <tr className="bg-bg-tertiary text-left border-b border-border">
                        <SortableTh label="User ID" sortKey="user_id" sort={sort} onSort={toggleSort} />
                        <SortableTh label="Config Tag" sortKey="config_tag" sort={sort} onSort={toggleSort} />
                        <SortableTh label="Created" sortKey="created" sort={sort} onSort={toggleSort} />
                        <Th>Uptime</Th>
                        <Th>Total</Th>
                        <Th>Download</Th>
                        <Th>Upload</Th>
                        <Th>↓ Speed</Th>
                        <Th>↑ Speed</Th>
                        <SortableTh label="Status" sortKey="status" sort={sort} onSort={toggleSort} />
                        <Th className="text-right">Actions</Th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {items.map((c) => (
                        <ContainerRow
                          key={c.id}
                          container={c}
                          expanded={expanded.has(c.id)}
                          onToggle={() => toggleExpand(c.id)}
                          onLogs={setLogsTarget}
                          onConfig={setConfigTarget}
                          onSuccess={success}
                          onError={error}
                          colSpan={COL_SPAN}
                        />
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
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

function Th({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <th className={`px-4 py-2.5 text-[11px] font-semibold text-text-muted uppercase tracking-wider whitespace-nowrap ${className}`}>
      {children}
    </th>
  )
}

function SortableTh({
  label,
  sortKey,
  sort,
  onSort,
}: {
  label: string
  sortKey: SortKey
  sort: { key: SortKey; dir: SortDir }
  onSort: (key: SortKey) => void
}) {
  const active = sort.key === sortKey
  return (
    <th className="px-4 py-2.5 text-[11px] font-semibold text-text-muted uppercase tracking-wider whitespace-nowrap">
      <button
        onClick={() => onSort(sortKey)}
        className={`inline-flex items-center gap-1 transition-colors cursor-pointer hover:text-text-primary ${active ? 'text-text-primary' : ''}`}
      >
        {label}
        {active && (sort.dir === 'asc' ? <ChevronUpIcon className="w-3 h-3" /> : <ChevronDownIcon className="w-3 h-3" />)}
      </button>
    </th>
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
