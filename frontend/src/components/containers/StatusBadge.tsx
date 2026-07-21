import Badge from '../ui/Badge'

type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info'

const statusMap: Record<string, { variant: BadgeVariant; label: string }> = {
  running: { variant: 'success', label: 'Running' },
  restarting: { variant: 'warning', label: 'Restarting' },
  created: { variant: 'info', label: 'Created' },
  paused: { variant: 'warning', label: 'Paused' },
  exited: { variant: 'danger', label: 'Stopped' },
  dead: { variant: 'danger', label: 'Dead' },
  removing: { variant: 'warning', label: 'Removing' },
}

export default function StatusBadge({ status }: { status: string }) {
  const s = statusMap[status] || { variant: 'default' as BadgeVariant, label: status }
  return <Badge variant={s.variant} dot>{s.label}</Badge>
}
