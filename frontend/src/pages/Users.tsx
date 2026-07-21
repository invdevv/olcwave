import { useState, useMemo, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi } from '../api/users'
import type { User } from '../types'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Input from '../components/ui/Input'
import Modal from '../components/ui/Modal'
import ConfirmDialog from '../components/ui/ConfirmDialog'
import { Card, ErrorState, EmptyState, Skeleton } from '../components/ui/Misc'
import {
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  ArrowPathIcon,
  UsersIcon,
  ClipboardDocumentIcon,
  CheckIcon,
} from '@heroicons/react/24/outline'

export default function Users() {
  const [search, setSearch] = useState('')
  const [editUser, setEditUser] = useState<User | null>(null)
  const [deleteUser, setDeleteUser] = useState<User | null>(null)
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
                      <td className="px-5 py-3"><Skeleton className="h-5 w-16 rounded-full" /></td>
                      <td className="px-5 py-3"><Skeleton className="h-4 w-12 ml-auto" /></td>
                    </tr>
                  ))}
                {!isLoading && filtered.length === 0 && (
                  <tr>
                    <td colSpan={5}>
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
                    />
                  ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <EditUserModal user={editUser} onClose={() => setEditUser(null)} />
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

function UserRow({ user, onEdit, onDelete }: { user: User; onEdit: () => void; onDelete: () => void }) {
  const [copied, setCopied] = useState(false)
  const isExpired = new Date(user.expires_at) < new Date()
  const created = new Date(user.created_at)
  const expires = new Date(user.expires_at)

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
        <Badge variant={isExpired ? 'danger' : 'success'} dot>{isExpired ? 'Expired' : 'Active'}</Badge>
      </td>
      <td className="px-5 py-3 text-right">
        <div className="flex items-center justify-end gap-1 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
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
