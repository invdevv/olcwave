import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { Container } from '../../types'
import { containersApi } from '../../api/containers'
import { formatBytes, formatRate } from '../../utils/format'
import StatusBadge from './StatusBadge'
import {
  PlayIcon,
  StopIcon,
  ArrowPathIcon,
  DocumentTextIcon,
  CodeBracketIcon,
  CubeIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from '@heroicons/react/24/outline'

type Action = 'run' | 'stop' | 'restart'

interface ContainerCardProps {
  container: Container
  onLogs: (c: Container) => void
  onConfig: (c: Container) => void
  onError: (message: string) => void
  onSuccess: (message: string) => void
}

export default function ContainerCard({ container, onLogs, onConfig, onError, onSuccess }: ContainerCardProps) {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: ({ action }: { action: Action }) => {
      if (action === 'run') return containersApi.run(container.name)
      if (action === 'stop') return containersApi.stop(container.name)
      return containersApi.restart(container.name)
    },
    onSuccess: (_data, { action }) => {
      queryClient.invalidateQueries({ queryKey: ['containers-all'] })
      onSuccess(`Container ${container.name} — ${action} succeeded`)
    },
    onError: (err: { response?: { data?: { detail?: string } } }, { action }) => {
      onError(err?.response?.data?.detail || `Failed to ${action} ${container.name}`)
    },
  })

  const pending = mutation.isPending ? mutation.variables?.action : undefined
  const isRunning = container.status === 'running'
  const created = new Date(container.created)

  const { data: stats } = useQuery({
    queryKey: ['container-stats', container.name],
    queryFn: () => containersApi.stats(container.name).then((r) => r.data),
    enabled: isRunning,
    refetchInterval: isRunning ? 5000 : false,
  })

  return (
    <div className="group bg-bg-secondary border border-border rounded-xl p-4 shadow-soft
      transition-all duration-200 hover:border-border-light hover:-translate-y-0.5 flex flex-col gap-3.5">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2.5 min-w-0">
          <div className="shrink-0 flex items-center justify-center w-9 h-9 rounded-lg bg-accent/10 text-accent">
            <CubeIcon className="w-4.5 h-4.5" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-text-primary truncate" title={container.name}>{container.name}</p>
            <code className="text-[11px] font-mono text-text-muted">{container.id}</code>
          </div>
        </div>
        <StatusBadge status={container.status} />
      </div>

      {/* Meta */}
      <div className="grid grid-cols-2 gap-x-3 gap-y-2 text-xs">
        <Meta label="User ID" value={container.user_id} mono />
        <Meta label="Config Tag" value={container.config_tag} accent />
        <Meta label="Created" value={`${created.toLocaleDateString()} ${created.toLocaleTimeString()}`} />
        <Meta label="Image" value={container.image} mono />
      </div>

      {/* Traffic */}
      {isRunning && (
        <div className="rounded-lg bg-bg-tertiary/50 border border-border px-3 py-2.5 space-y-2">
          <div className="grid grid-cols-3 gap-2 text-xs">
            <TrafficStat label="Upload" value={formatBytes(stats?.upload_bytes ?? 0)} />
            <TrafficStat label="Download" value={formatBytes(stats?.download_bytes ?? 0)} />
            <TrafficStat label="Total" value={formatBytes(stats?.total_bytes ?? 0)} accent />
          </div>
          <div className="flex items-center gap-4 pt-1.5 border-t border-border/60 text-xs">
            <span className="inline-flex items-center gap-1 text-info">
              <ArrowDownIcon className="w-3 h-3" />
              <span className="tabular-nums">{formatRate(stats?.download_rate_bps ?? 0)}</span>
            </span>
            <span className="inline-flex items-center gap-1 text-success">
              <ArrowUpIcon className="w-3 h-3" />
              <span className="tabular-nums">{formatRate(stats?.upload_rate_bps ?? 0)}</span>
            </span>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap items-center gap-1.5 pt-1 border-t border-border">
        <ActionButton
          icon={PlayIcon}
          label="Run"
          onClick={() => mutation.mutate({ action: 'run' })}
          loading={pending === 'run'}
          disabled={mutation.isPending || isRunning}
          variant="success"
        />
        <ActionButton
          icon={StopIcon}
          label="Stop"
          onClick={() => mutation.mutate({ action: 'stop' })}
          loading={pending === 'stop'}
          disabled={mutation.isPending || !isRunning}
          variant="danger"
        />
        <ActionButton
          icon={ArrowPathIcon}
          label="Restart"
          onClick={() => mutation.mutate({ action: 'restart' })}
          loading={pending === 'restart'}
          disabled={mutation.isPending}
        />
        <div className="ml-auto flex items-center gap-1.5">
          <ActionButton icon={DocumentTextIcon} label="Logs" onClick={() => onLogs(container)} disabled={mutation.isPending} />
          <ActionButton icon={CodeBracketIcon} label="Config" onClick={() => onConfig(container)} disabled={mutation.isPending} />
        </div>
      </div>
    </div>
  )
}

function TrafficStat({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="min-w-0">
      <p className="text-[10px] uppercase tracking-wider text-text-muted">{label}</p>
      <p className={`truncate tabular-nums font-medium ${accent ? 'text-accent' : 'text-text-secondary'}`} title={value}>
        {value}
      </p>
    </div>
  )
}

function Meta({ label, value, mono, accent }: { label: string; value: string; mono?: boolean; accent?: boolean }) {
  return (
    <div className="min-w-0">
      <p className="text-[10px] uppercase tracking-wider text-text-muted">{label}</p>
      <p className={`truncate ${mono ? 'font-mono' : ''} ${accent ? 'text-accent' : 'text-text-secondary'}`} title={value}>
        {value}
      </p>
    </div>
  )
}

interface ActionButtonProps {
  icon: React.ComponentType<{ className?: string }>
  label: string
  onClick: () => void
  loading?: boolean
  disabled?: boolean
  variant?: 'default' | 'success' | 'danger'
}

const actionVariants = {
  default: 'text-text-secondary hover:text-text-primary hover:bg-bg-hover',
  success: 'text-success hover:bg-success/10',
  danger: 'text-danger hover:bg-danger/10',
}

function ActionButton({ icon: Icon, label, onClick, loading, disabled, variant = 'default' }: ActionButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`inline-flex items-center gap-1.5 h-7 px-2.5 text-xs font-medium rounded-md
        transition-all duration-150 cursor-pointer active:scale-[0.98]
        disabled:opacity-40 disabled:pointer-events-none ${actionVariants[variant]}`}
      title={label}
    >
      {loading ? (
        <svg className="animate-spin h-3.5 w-3.5 shrink-0" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      ) : (
        <Icon className="w-3.5 h-3.5 shrink-0" />
      )}
      {label}
    </button>
  )
}
