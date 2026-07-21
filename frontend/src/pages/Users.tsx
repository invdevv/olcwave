import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi } from '../api/users'
import type { User } from '../types'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Modal from '../components/ui/Modal'
import ConfirmDialog from '../components/ui/ConfirmDialog'
import { EmptyState, LoadingState, ErrorState } from '../components/ui/Misc'
import { MagnifyingGlassIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline'

export default function Users() {
  const [searchUuid, setSearchUuid] = useState('')
  const [activeUuid, setActiveUuid] = useState('')
  const queryClient = useQueryClient()

  const { data: user, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['user', activeUuid],
    queryFn: () => usersApi.getByShortUuid(activeUuid).then((r) => r.data),
    enabled: !!activeUuid,
  })

  const handleSearch = () => {
    if (searchUuid.trim()) {
      setActiveUuid(searchUuid.trim())
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="flex-1 flex gap-2">
          <input
            value={searchUuid}
            onChange={(e) => setSearchUuid(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search by short UUID..."
            className="flex-1 bg-bg-primary border border-border rounded-md px-3 py-2 text-sm text-text-primary
              placeholder:text-text-muted focus:outline-none focus:border-accent"
          />
          <Button onClick={handleSearch} variant="secondary">
            <MagnifyingGlassIcon className="w-4 h-4" />
            Search
          </Button>
        </div>
      </div>

      <p className="text-xs text-text-muted">
        Backend only supports lookup by individual short UUID. No list-all endpoint available.
      </p>

      {isLoading && <LoadingState text="Looking up user..." />}
      {isError && <ErrorState message={(error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'User not found'} onRetry={() => refetch()} />}
      {user && <UserCard user={user} />}
      {!activeUuid && !isLoading && <EmptyState message="Enter a short UUID to look up a user" />}
    </div>
  )
}

function UserCard({ user }: { user: User }) {
  const [editOpen, setEditOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [editExpiry, setEditExpiry] = useState('')
  const queryClient = useQueryClient()

  const updateMutation = useMutation({
    mutationFn: (expiresAt: string) => usersApi.update(user.short_uuid, expiresAt),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', user.short_uuid] })
      setEditOpen(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => usersApi.delete(user.short_uuid),
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: ['user', user.short_uuid] })
      setDeleteOpen(false)
    },
  })

  const isExpired = new Date(user.expires_at) < new Date()

  return (
    <>
      <div className="bg-bg-secondary border border-border rounded-lg p-4 animate-fade-in">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-text-primary font-mono">{user.short_uuid}</h3>
              <Badge variant={isExpired ? 'danger' : 'success'}>{isExpired ? 'Expired' : 'Active'}</Badge>
            </div>
            <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-xs">
              <div>
                <span className="text-text-muted">Created: </span>
                <span className="text-text-primary">{new Date(user.created_at).toLocaleString()}</span>
              </div>
              <div>
                <span className="text-text-muted">Expires: </span>
                <span className="text-text-primary">{new Date(user.expires_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
          <div className="flex gap-1">
            <button
              onClick={() => { setEditExpiry(user.expires_at.slice(0, 16)); setEditOpen(true) }}
              className="p-1.5 rounded-md text-text-muted hover:text-text-primary hover:bg-bg-hover transition-colors cursor-pointer"
            >
              <PencilIcon className="w-4 h-4" />
            </button>
            <button
              onClick={() => setDeleteOpen(true)}
              className="p-1.5 rounded-md text-text-muted hover:text-danger hover:bg-danger/10 transition-colors cursor-pointer"
            >
              <TrashIcon className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-border">
          <div className="flex items-center gap-2">
            <span className="text-xs text-text-muted">Subscription URL:</span>
            <code className="text-xs text-accent font-mono bg-bg-primary px-2 py-0.5 rounded">
              /sub/{user.short_uuid}
            </code>
            <button
              onClick={() => navigator.clipboard.writeText(`${window.location.origin}/sub/${user.short_uuid}`)}
              className="text-xs text-text-muted hover:text-text-primary cursor-pointer"
            >
              Copy
            </button>
          </div>
        </div>
      </div>

      <Modal open={editOpen} onClose={() => setEditOpen(false)} title="Update Expiry">
        <div className="space-y-4">
          <Input
            label="Expires at"
            type="datetime-local"
            value={editExpiry}
            onChange={(e) => setEditExpiry(e.target.value)}
          />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setEditOpen(false)}>Cancel</Button>
            <Button
              loading={updateMutation.isPending}
              onClick={() => updateMutation.mutate(new Date(editExpiry).toISOString())}
            >
              Save
            </Button>
          </div>
        </div>
      </Modal>

      <ConfirmDialog
        open={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        onConfirm={() => deleteMutation.mutate()}
        title="Delete User"
        message={`Are you sure you want to delete user ${user.short_uuid}? This action cannot be undone.`}
        loading={deleteMutation.isPending}
      />
    </>
  )
}
