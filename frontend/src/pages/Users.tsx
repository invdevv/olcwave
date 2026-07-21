import { useState, useMemo, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi } from '../api/users'
import type { User } from '../types'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Input from '../components/ui/Input'
import Modal from '../components/ui/Modal'
import ConfirmDialog from '../components/ui/ConfirmDialog'
import ProgressBar from '../components/ui/ProgressBar'
import { Card, ErrorState, EmptyState, Skeleton } from '../components/ui/Misc'
import { formatBytes, trafficPercent, bytesToGB, gbToBytes } from '../utils/format'
import {
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  ArrowPathIcon,
  UsersIcon,
  ClipboardDocumentIcon,
  CheckIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'

export default function Users() {
  const [search, setSearch] = useState('')
  const [editUser, setEditUser] = useState<User | null>(null)
  const [deleteUser, setDeleteUser] = useState<User | null>(null)
  const [trafficUser, setTrafficUser] = useState<User | null>(null)
  const queryClient = useQueryClient()

  const { data: users, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['users-all'],
    queryFn: () => usersApi.getAll().then((r) => r.data),
  })

  const deleteMutation = useMutation({
    mutationFn: (uuid: string) => usersApi.delete(uuid),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users-all'] })
      setDeleteUser(null)
    },
  })

  const filtered = useMemo(() => {
    if (!users) return []
    const q = search.toLowerCase()
    return users.filter(
      (u) =>
        u.short_uuid.toLowerCase().includes(q) ||
        u.created_at.toLowerCase().includes(q) ||
        u.expires_at.toLowerCase().includes(q)
    )
  }, [users, search])

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter users..."
            className="w-full h-9 bg-bg-tertiary border border-border rounded-md pl-9 pr-3 text-sm text-text-primary
              placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/30 transition-all"
          />
        </div>
        <span className="text-xs text-text-muted tabular-nums">{filtered.length} users</span>
        <Button variant="secondary" onClick={() => refetch()}>
          <ArrowPathIcon className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {isError ? (
        <Card>
          <ErrorState
            message={(error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to load users'}
            onRetry={() => refetch()}
          />
        </Card>
      ) : (
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left bg-bg-tertiary/40">
                  <Th>Short UUID</Th>
                  <Th>Created</Th>
                  <Th>Expires</Th>
                  <Th>Traffic</Th>
                  <Th>Status</Th>
                  <Th className="text-right">Actions</Th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {isLoading &&
                  Array.from({ length: 6 }).map((_, i) => (
                    <tr key={i}>
                      <td className="px-5 py-3"><Skeleton className="h-4 w-24" /></td>
                      <td className="px-5 py-3"><Skeleton className="h-4 w-32" /></td>
                      <td className="px-5 py-3"><Skeleton className="h-4 w-32" /></td>
                      <td className="px-5 py-3"><Skeleton className="h-4 w-28" /></td>
                      <td className="px-5 py-3"><Skeleton className="h-5 w-16 rounded-full" /></td>
                      <td className="px-5 py-3"><Skeleton className="h-4 w-12 ml-auto" /></td>
                    </tr>
                  ))}
                {!isLoading && filtered.length === 0 && (
                  <tr>
                    <td colSpan={6}>
                      <EmptyState
                        message={users?.length === 0 ? 'No users found' : 'No matching users'}
                        hint={users?.length === 0 ? undefined : 'Try adjusting your search filter.'}
                        icon={<UsersIcon className="w-6 h-6" />}
                      />
                    </td>
                  </tr>
                )}
                {!isLoading &&
                  filtered.map((user) => (
                    <UserRow
                      key={user.short_uuid}
                      user={user}
                      onEdit={() => setEditUser(user)}
                      onDelete={() => setDeleteUser(user)}
                      onTraffic={() => setTrafficUser(user)}
                    />
                  ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <EditUserModal user={editUser} onClose={() => setEditUser(null)} />
      <TrafficModal user={trafficUser} onClose={() => setTrafficUser(null)} />
      <ConfirmDialog
        open={!!deleteUser}
        onClose={() => setDeleteUser(null)}
        onConfirm={() => deleteUser && deleteMutation.mutate(deleteUser.short_uuid)}
        title="Delete User"
        message={`Delete user ${deleteUser?.short_uuid}? This action cannot be undone.`}
        loading={deleteMutation.isPending}
      />
    </div>
  )
}

function Th({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <th className={`px-5 py-3 text-xs font-semibold text-text-muted uppercase tracking-wider ${className}`}>
      {children}
    </th>
  )
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-bg-tertiary border border-border rounded-lg px-3 py-2.5">
      <p className="text-[10px] uppercase tracking-wider text-text-muted">{label}</p>
      <p className="text-sm font-semibold text-text-primary mt-0.5 tabular-nums">{value}</p>
    </div>
  )
}

function UserRow({ user, onEdit, onDelete, onTraffic }: { user: User; onEdit: () => void; onDelete: () => void; onTraffic: () => void }) {
  const [copied, setCopied] = useState(false)
  const isExpired = new Date(user.expires_at) < new Date()
  const created = new Date(user.created_at)
  const expires = new Date(user.expires_at)
  const unlimited = user.traffic_limit_bytes === 0
  const percent = trafficPercent(user.traffic_used_bytes, user.traffic_limit_bytes)
  const exceeded = !unlimited && user.traffic_used_bytes >= user.traffic_limit_bytes

  const copy = () => {
    navigator.clipboard.writeText(user.short_uuid)
    setCopied(true)
    setTimeout(() => setCopied(false), 1200)
  }

  return (
    <tr className="hover:bg-bg-hover transition-colors group">
      <td className="px-5 py-3">
        <div className="flex items-center gap-2">
          <code className="text-xs font-mono text-accent">{user.short_uuid}</code>
          <button
            onClick={copy}
            className="text-text-muted hover:text-text-primary sm:opacity-0 sm:group-hover:opacity-100 transition-all cursor-pointer"
            title="Copy UUID"
          >
            {copied ? <CheckIcon className="w-3.5 h-3.5 text-success" /> : <ClipboardDocumentIcon className="w-3.5 h-3.5" />}
          </button>
        </div>
      </td>
      <td className="px-5 py-3 text-xs text-text-secondary whitespace-nowrap">{created.toLocaleDateString()} {created.toLocaleTimeString()}</td>
      <td className="px-5 py-3 text-xs text-text-secondary whitespace-nowrap">{expires.toLocaleDateString()} {expires.toLocaleTimeString()}</td>
      <td className="px-5 py-3">
        <div className="w-40 space-y-1">
          <div className="flex items-center justify-between gap-2 text-xs">
            <span className="text-text-secondary tabular-nums">
              {formatBytes(user.traffic_used_bytes)} / {unlimited ? '∞' : formatBytes(user.traffic_limit_bytes)}
            </span>
            {!unlimited && <span className="text-text-muted tabular-nums">{percent}%</span>}
          </div>
          <ProgressBar percent={percent} unlimited={unlimited} />
        </div>
      </td>
      <td className="px-5 py-3">
        {exceeded ? (
          <Badge variant="danger" dot>Traffic exceeded</Badge>
        ) : (
          <Badge variant={isExpired ? 'danger' : 'success'} dot>{isExpired ? 'Expired' : 'Active'}</Badge>
        )}
      </td>
      <td className="px-5 py-3 text-right">
        <div className="flex items-center justify-end gap-1 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
          <button
            onClick={onTraffic}
            className="p-1.5 rounded-md text-text-muted hover:text-text-primary hover:bg-bg-tertiary transition-colors cursor-pointer"
            title="Traffic management"
          >
            <ChartBarIcon className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onEdit}
            className="p-1.5 rounded-md text-text-muted hover:text-text-primary hover:bg-bg-tertiary transition-colors cursor-pointer"
            title="Edit expiry"
          >
            <PencilIcon className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onDelete}
            className="p-1.5 rounded-md text-text-muted hover:text-danger hover:bg-danger/10 transition-colors cursor-pointer"
            title="Delete"
          >
            <TrashIcon className="w-3.5 h-3.5" />
          </button>
        </div>
      </td>
    </tr>
  )
}

function EditUserModal({ user, onClose }: { user: User | null; onClose: () => void }) {
  const [expiry, setExpiry] = useState('')
  const queryClient = useQueryClient()

  useEffect(() => {
    if (user) setExpiry(user.expires_at.slice(0, 16))
  }, [user])

  const mutation = useMutation({
    mutationFn: (expiresAt: string) => usersApi.update(user!.short_uuid, expiresAt),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users-all'] })
      onClose()
    },
  })

  if (!user) return null

  return (
    <Modal open={!!user} onClose={onClose} title="Edit User Expiry" description="Update when this user's access expires">
      <div className="space-y-4">
        <div className="bg-bg-tertiary border border-border rounded-lg px-3.5 py-2.5">
          <p className="text-xs text-text-muted mb-0.5">User</p>
          <code className="text-sm font-mono text-accent">{user.short_uuid}</code>
        </div>
        <Input
          label="Expires at"
          type="datetime-local"
          value={expiry}
          onChange={(e) => setExpiry(e.target.value)}
        />
        <div className="flex justify-end gap-2 pt-1">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button loading={mutation.isPending} onClick={() => mutation.mutate(new Date(expiry).toISOString())}>
            Save
          </Button>
        </div>
      </div>
    </Modal>
  )
}

function TrafficModal({ user, onClose }: { user: User | null; onClose: () => void }) {
  const queryClient = useQueryClient()
  const [limitGb, setLimitGb] = useState('')
  const [unlimited, setUnlimited] = useState(false)
  const [confirmReset, setConfirmReset] = useState(false)

  const { data: traffic, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['user-traffic', user?.short_uuid],
    queryFn: () => usersApi.getTraffic(user!.short_uuid).then((r) => r.data),
    enabled: !!user,
  })

  useEffect(() => {
    if (traffic) {
      setUnlimited(traffic.unlimited)
      setLimitGb(traffic.unlimited ? '' : bytesToGB(traffic.limit).toFixed(2))
    }
    setConfirmReset(false)
  }, [traffic])

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['users-all'] })
    queryClient.invalidateQueries({ queryKey: ['user-traffic', user?.short_uuid] })
  }

  const limitMutation = useMutation({
    mutationFn: (bytes: number) => usersApi.setTrafficLimit(user!.short_uuid, bytes),
    onSuccess: () => {
      invalidate()
      onClose()
    },
  })

  const resetMutation = useMutation({
    mutationFn: () => usersApi.resetTraffic(user!.short_uuid),
    onSuccess: () => {
      invalidate()
      setConfirmReset(false)
      refetch()
    },
  })

  if (!user) return null

  const saveLimit = () => {
    const bytes = unlimited ? 0 : gbToBytes(parseFloat(limitGb) || 0)
    limitMutation.mutate(bytes)
  }
  const percent = traffic ? trafficPercent(traffic.used, traffic.limit) : 0

  return (
    <Modal open={!!user} onClose={onClose} title="Traffic Management" description={user.short_uuid}>
      {isLoading ? (
        <div className="space-y-3">
          <Skeleton className="h-16 rounded-lg" />
          <Skeleton className="h-2 w-full" />
          <Skeleton className="h-9 w-full" />
        </div>
      ) : isError ? (
        <ErrorState
          message={(error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to load traffic'}
          onRetry={() => refetch()}
        />
      ) : traffic ? (
        <div className="space-y-5">
          <div className="grid grid-cols-3 gap-3">
            <StatBox label="Used" value={formatBytes(traffic.used)} />
            <StatBox label="Limit" value={traffic.unlimited ? '∞' : formatBytes(traffic.limit)} />
            <StatBox label="Remaining" value={traffic.unlimited ? '∞' : formatBytes(traffic.remaining)} />
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs text-text-muted">
              <span>{traffic.unlimited ? 'Unlimited plan' : `${percent}% used`}</span>
              {traffic.exceeded && <span className="text-danger font-medium">Traffic exceeded</span>}
            </div>
            <ProgressBar percent={percent} unlimited={traffic.unlimited} />
          </div>

          <div className="border-t border-border pt-4 space-y-3">
            <label className="flex items-center gap-2 text-sm text-text-secondary cursor-pointer select-none">
              <input
                type="checkbox"
                checked={unlimited}
                onChange={(e) => setUnlimited(e.target.checked)}
                className="accent-accent w-4 h-4 cursor-pointer"
              />
              Unlimited traffic
            </label>
            {!unlimited && (
              <Input
                label="Traffic limit (GB)"
                type="number"
                min="0"
                step="0.1"
                value={limitGb}
                onChange={(e) => setLimitGb(e.target.value)}
                placeholder="e.g. 100"
              />
            )}
            <div className="flex items-center justify-between gap-2 pt-1">
              {confirmReset ? (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-text-muted">Reset used traffic to 0?</span>
                  <Button size="sm" variant="danger" loading={resetMutation.isPending} onClick={() => resetMutation.mutate()}>
                    Confirm
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setConfirmReset(false)}>Cancel</Button>
                </div>
              ) : (
                <Button size="sm" variant="secondary" onClick={() => setConfirmReset(true)}>
                  Reset traffic
                </Button>
              )}
              <Button loading={limitMutation.isPending} onClick={saveLimit}>
                Change limit
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </Modal>
  )
}
