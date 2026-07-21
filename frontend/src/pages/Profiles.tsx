import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { profilesApi } from '../api/profiles'
import type { Profile } from '../types'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Modal from '../components/ui/Modal'
import ConfirmDialog from '../components/ui/ConfirmDialog'
import { EmptyState, LoadingState, ErrorState } from '../components/ui/Misc'
import { PlusIcon, PencilIcon, TrashIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'

export default function Profiles() {
  const [searchTag, setSearchTag] = useState('')
  const [activeTag, setActiveTag] = useState('')
  const [createOpen, setCreateOpen] = useState(false)
  const [editProfile, setEditProfile] = useState<Profile | null>(null)
  const [deleteTag, setDeleteTag] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data: profile, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['profile', activeTag],
    queryFn: () => profilesApi.getByTag(activeTag).then((r) => r.data),
    enabled: !!activeTag,
  })

  const deleteMutation = useMutation({
    mutationFn: (tag: string) => profilesApi.delete(tag),
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: ['profile', deleteTag!] })
      setDeleteTag(null)
      if (activeTag === deleteTag) setActiveTag('')
    },
  })

  const handleSearch = () => {
    if (searchTag.trim()) setActiveTag(searchTag.trim())
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="flex-1 flex gap-2">
          <input
            value={searchTag}
            onChange={(e) => setSearchTag(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search by tag..."
            className="flex-1 bg-bg-primary border border-border rounded-md px-3 py-2 text-sm text-text-primary
              placeholder:text-text-muted focus:outline-none focus:border-accent"
          />
          <Button onClick={handleSearch} variant="secondary">
            <MagnifyingGlassIcon className="w-4 h-4" />
            Search
          </Button>
        </div>
        <Button onClick={() => setCreateOpen(true)}>
          <PlusIcon className="w-4 h-4" />
          New Profile
        </Button>
      </div>

      <p className="text-xs text-text-muted">
        Backend only supports lookup by individual tag. No list-all endpoint available.
      </p>

      {isLoading && <LoadingState text="Looking up profile..." />}
      {isError && <ErrorState message={(error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Profile not found'} onRetry={() => refetch()} />}
      {profile && (
        <ProfileCard
          profile={profile}
          onEdit={() => setEditProfile(profile)}
          onDelete={() => setDeleteTag(profile.tag)}
        />
      )}
      {!activeTag && !isLoading && <EmptyState message="Enter a tag to look up a profile" />}

      <CreateModal open={createOpen} onClose={() => setCreateOpen(false)} />
      <EditModal profile={editProfile} onClose={() => setEditProfile(null)} />

      <ConfirmDialog
        open={!!deleteTag}
        onClose={() => setDeleteTag(null)}
        onConfirm={() => deleteTag && deleteMutation.mutate(deleteTag)}
        title="Delete Profile"
        message={`Delete profile "${deleteTag}"? This will also stop all running containers using it.`}
        loading={deleteMutation.isPending}
      />
    </div>
  )
}

function ProfileCard({ profile, onEdit, onDelete }: { profile: Profile; onEdit: () => void; onDelete: () => void }) {
  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4 animate-fade-in">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-text-primary">{profile.name}</h3>
            <code className="text-xs text-accent font-mono bg-bg-primary px-2 py-0.5 rounded">{profile.tag}</code>
          </div>
        </div>
        <div className="flex gap-1">
          <button onClick={onEdit} className="p-1.5 rounded-md text-text-muted hover:text-text-primary hover:bg-bg-hover transition-colors cursor-pointer">
            <PencilIcon className="w-4 h-4" />
          </button>
          <button onClick={onDelete} className="p-1.5 rounded-md text-text-muted hover:text-danger hover:bg-danger/10 transition-colors cursor-pointer">
            <TrashIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t border-border">
        <p className="text-xs text-text-muted mb-1">YAML Config:</p>
        <pre className="bg-bg-primary border border-border rounded-md p-3 text-xs text-text-secondary overflow-x-auto max-h-40 overflow-y-auto font-mono">
          {profile.profile}
        </pre>
      </div>
    </div>
  )
}

function CreateModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [name, setName] = useState('')
  const [tag, setTag] = useState('')
  const [profile, setProfile] = useState('')
  const [error, setError] = useState('')
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: () => profilesApi.create({ name, tag, profile }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      setName(''); setTag(''); setProfile(''); setError('')
      onClose()
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      setError(err?.response?.data?.detail || 'Failed to create profile')
    },
  })

  return (
    <Modal open={open} onClose={onClose} title="Create Profile" wide>
      <div className="space-y-4">
        {error && (
          <div className="bg-danger/10 border border-danger/20 rounded-md px-3 py-2 text-xs text-danger">{error}</div>
        )}
        <div className="grid grid-cols-2 gap-4">
          <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Profile name" />
          <Input label="Tag" value={tag} onChange={(e) => setTag(e.target.value)} placeholder="unique-tag" />
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-text-secondary uppercase tracking-wider">YAML Config</label>
          <textarea
            value={profile}
            onChange={(e) => setProfile(e.target.value)}
            placeholder="Paste YAML config here..."
            rows={12}
            className="bg-bg-primary border border-border rounded-md px-3 py-2 text-sm text-text-primary
              placeholder:text-text-muted focus:outline-none focus:border-accent font-mono resize-y"
          />
        </div>
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button loading={mutation.isPending} onClick={() => mutation.mutate()}>Create</Button>
        </div>
      </div>
    </Modal>
  )
}

function EditModal({ profile, onClose }: { profile: Profile | null; onClose: () => void }) {
  const [name, setName] = useState(profile?.name || '')
  const [prof, setProf] = useState(profile?.profile || '')
  const [error, setError] = useState('')
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: () => profile && profilesApi.update(profile.tag, name, prof),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile', profile?.tag] })
      setError('')
      onClose()
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      setError(err?.response?.data?.detail || 'Failed to update profile')
    },
  })

  if (!profile) return null

  return (
    <Modal open={!!profile} onClose={onClose} title={`Edit: ${profile.tag}`} wide>
      <div className="space-y-4">
        {error && (
          <div className="bg-danger/10 border border-danger/20 rounded-md px-3 py-2 text-xs text-danger">{error}</div>
        )}
        <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} />
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-text-secondary uppercase tracking-wider">YAML Config</label>
          <textarea
            value={prof}
            onChange={(e) => setProf(e.target.value)}
            rows={12}
            className="bg-bg-primary border border-border rounded-md px-3 py-2 text-sm text-text-primary
              focus:outline-none focus:border-accent font-mono resize-y"
          />
        </div>
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button loading={mutation.isPending} onClick={() => mutation.mutate()}>Save</Button>
        </div>
      </div>
    </Modal>
  )
}
