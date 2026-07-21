import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi } from '../api/users'
import type { User } from '../types'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Input from '../components/ui/Input'
import Modal from '../components/ui/Modal'
import ConfirmDialog from '../components/ui/ConfirmDialog'
import { LoadingState, ErrorState } from '../components/ui/Misc'
import { MagnifyingGlassIcon, PencilIcon, TrashIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

export default function Users() {
  const [search, setSearch] = useState('')
  const [editUser, setEditUser] = useState<User | null>(null)
  const [deleteUser, setDeleteUser] = useState<User | null>(null)
  const queryClient = useQueryClient()

  const { data: users, isLoading, isError, error, refetch } = useQuery({
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
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter users..."
            className="w-full bg-bg-primary border border-border rounded-md pl-9 pr-3 py-2 text-sm text-text-primary
              placeholder:text-text-muted focus:outline-none focus:border-accent"
          />
        </div>
        <Button variant="secondary" onClick={() => refetch()}>
          <ArrowPathIcon className="w-4 h-4" />
          Refresh
        </Button>
        <span className="text-xs text-text-muted">{filtered.length} users</span>
      </div>

      {isLoading && <LoadingState text="Loading users..." />}
      {isError && <ErrorState message={(error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to load users'} onRetry={() => refetch()} />}

      {!isLoading && !isError && (
        <div className="bg-bg-secondary border border-border rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                <th className="px-4 py-2.5 text-xs font-semibold text-text-muted uppercase tracking-wider">Short UUID</th>
                <th className="px-4 py-2.5 text-xs font-semibold text-text-muted uppercase tracking-wider">Created</th>
                <th className="px-4 py-2.5 text-xs font-semibold text-text-muted uppercase tracking-wider">Expires</th>
                <th className="px-4 py-2.5 text-xs font-semibold text-text-muted uppercase tracking-wider">Status</th>
                <th className="px-4 py-2.5 text-xs font-semibold text-text-muted uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-text-muted text-xs">
                    {users?.length === 0 ? 'No users found' : 'No matches'}
                  </td>
                </tr>
              )}
              {filtered.map((user) => (
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

function UserRow({ user, onEdit, onDelete }: { user: User; onEdit: () => void; onDelete: () => void }) {
  const isExpired = new Date(user.expires_at) < new Date()
  const created = new Date(user.created_at)
  const expires = new Date(user.expires_at)

  return (
    <tr className="hover:bg-bg-hover transition-colors group">
      <td className="px-4 py-2.5">
        <div className="flex items-center gap-2">
          <code className="text-xs font-mono text-accent">{user.short_uuid}</code>
          <button
            onClick={() => navigator.clipboard.writeText(user.short_uuid)}
            className="opacity-0 group-hover:opacity-100 text-text-muted hover:text-text-primary text-xs cursor-pointer transition-opacity"
            title="Copy"
          >
            Copy
          </button>
        </div>
      </td>
      <td className="px-4 py-2.5 text-xs text-text-secondary">{created.toLocaleDateString()} {created.toLocaleTimeString()}</td>
      <td className="px-4 py-2.5 text-xs text-text-secondary">{expires.toLocaleDateString()} {expires.toLocaleTimeString()}</td>
      <td className="px-4 py-2.5">
        <Badge variant={isExpired ? 'danger' : 'success'}>{isExpired ? 'Expired' : 'Active'}</Badge>
      </td>
      <td className="px-4 py-2.5 text-right">
        <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
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

  const mutation = useMutation({
    mutationFn: (expiresAt: string) => user && usersApi.update(user.short_uuid, expiresAt),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users-all'] })
      onClose()
    },
  })

  if (!user) return null

  const handleOpen = () => {
    setExpiry(user.expires_at.slice(0, 16))
  }

  return (
    <Modal open={!!user} onClose={onClose} title="Edit User Expiry">
      <div className="space-y-4">
        <div className="bg-bg-primary border border-border rounded-md px-3 py-2">
          <p className="text-xs text-text-muted">User</p>
          <code className="text-sm font-mono text-accent">{user.short_uuid}</code>
        </div>
        <Input
          label="Expires at"
          type="datetime-local"
          value={expiry}
          onChange={(e) => setExpiry(e.target.value)}
        />
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button loading={mutation.isPending} onClick={() => mutation.mutate(new Date(expiry).toISOString())}>
            Save
          </Button>
        </div>
      </div>
    </Modal>
  )
}
