import { useState, useMemo, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { profilesApi } from '../api/profiles'
import type { Profile } from '../types'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Input from '../components/ui/Input'
import Modal from '../components/ui/Modal'
import ConfirmDialog from '../components/ui/ConfirmDialog'
import { LoadingState, ErrorState } from '../components/ui/Misc'
import { MagnifyingGlassIcon, PencilIcon, TrashIcon, PlusIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

export default function Profiles() {
  const [search, setSearch] = useState('')
  const [createOpen, setCreateOpen] = useState(false)
  const [editProfile, setEditProfile] = useState<Profile | null>(null)
  const [deleteProfile, setDeleteProfile] = useState<Profile | null>(null)
  const queryClient = useQueryClient()

  const { data: profiles, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['profiles-all'],
    queryFn: () => profilesApi.getAll().then((r) => r.data),
  })

  const deleteMutation = useMutation({
    mutationFn: (tag: string) => profilesApi.delete(tag),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profiles-all'] })
      setDeleteProfile(null)
    },
  })

  const filtered = useMemo(() => {
    if (!profiles) return []
    const q = search.toLowerCase()
    return profiles.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.tag.toLowerCase().includes(q)
    )
  }, [profiles, search])

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter profiles..."
            className="w-full bg-bg-primary border border-border rounded-md pl-9 pr-3 py-2 text-sm text-text-primary
              placeholder:text-text-muted focus:outline-none focus:border-accent"
          />
        </div>
        <Button variant="secondary" onClick={() => refetch()}>
          <ArrowPathIcon className="w-4 h-4" />
          Refresh
        </Button>
        <Button onClick={() => setCreateOpen(true)}>
          <PlusIcon className="w-4 h-4" />
          New Profile
        </Button>
        <span className="text-xs text-text-muted">{filtered.length} profiles</span>
      </div>

      {isLoading && <LoadingState text="Loading profiles..." />}
      {isError && <ErrorState message={(error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to load profiles'} onRetry={() => refetch()} />}

      {!isLoading && !isError && (
        <div className="bg-bg-secondary border border-border rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                <th className="px-4 py-2.5 text-xs font-semibold text-text-muted uppercase tracking-wider">Name</th>
                <th className="px-4 py-2.5 text-xs font-semibold text-text-muted uppercase tracking-wider">Tag</th>
                <th className="px-4 py-2.5 text-xs font-semibold text-text-muted uppercase tracking-wider">Config Preview</th>
                <th className="px-4 py-2.5 text-xs font-semibold text-text-muted uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-text-muted text-xs">
                    {profiles?.length === 0 ? 'No profiles yet' : 'No matches'}
                  </td>
                </tr>
              )}
              {filtered.map((profile) => (
                <tr key={profile.tag} className="hover:bg-bg-hover transition-colors group">
                  <td className="px-4 py-2.5">
                    <span className="text-sm text-text-primary font-medium">{profile.name}</span>
                  </td>
                  <td className="px-4 py-2.5">
                    <code className="text-xs font-mono text-accent bg-bg-primary px-2 py-0.5 rounded">{profile.tag}</code>
                  </td>
                  <td className="px-4 py-2.5 max-w-xs">
                    <span className="text-xs text-text-muted font-mono truncate block">{profile.profile.slice(0, 80)}...</span>
                  </td>
                  <td className="px-4 py-2.5 text-right">
                    <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => setEditProfile(profile)}
                        className="p-1.5 rounded-md text-text-muted hover:text-text-primary hover:bg-bg-tertiary transition-colors cursor-pointer"
                        title="Edit"
                      >
                        <PencilIcon className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setDeleteProfile(profile)}
                        className="p-1.5 rounded-md text-text-muted hover:text-danger hover:bg-danger/10 transition-colors cursor-pointer"
                        title="Delete"
                      >
                        <TrashIcon className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <CreateProfileModal open={createOpen} onClose={() => setCreateOpen(false)} />
      <EditProfileModal profile={editProfile} onClose={() => setEditProfile(null)} />
      <ConfirmDialog
        open={!!deleteProfile}
        onClose={() => setDeleteProfile(null)}
        onConfirm={() => deleteProfile && deleteMutation.mutate(deleteProfile.tag)}
        title="Delete Profile"
        message={`Delete profile "${deleteProfile?.tag}"? This will stop all running containers using this profile.`}
        loading={deleteMutation.isPending}
      />
    </div>
  )
}

function CreateProfileModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [name, setName] = useState('')
  const [tag, setTag] = useState('')
  const [config, setConfig] = useState('')
  const [error, setError] = useState('')
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: () => profilesApi.create({ name, tag, profile: config }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profiles-all'] })
      reset()
      onClose()
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      setError(err?.response?.data?.detail || 'Failed to create profile')
    },
  })

  const reset = () => { setName(''); setTag(''); setConfig(''); setError('') }

  return (
    <Modal open={open} onClose={() => { reset(); onClose() }} title="Create Profile" wide>
      <div className="space-y-4">
        {error && (
          <div className="bg-danger/10 border border-danger/20 rounded-md px-3 py-2 text-xs text-danger">{error}</div>
        )}
        <div className="grid grid-cols-2 gap-4">
          <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Display name" />
          <Input label="Tag" value={tag} onChange={(e) => setTag(e.target.value)} placeholder="unique-tag" />
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-text-secondary uppercase tracking-wider">YAML Config</label>
          <textarea
            value={config}
            onChange={(e) => setConfig(e.target.value)}
            placeholder="Paste YAML configuration here..."
            rows={16}
            className="bg-bg-primary border border-border rounded-md px-3 py-2 text-sm text-text-primary
              placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30
              font-mono resize-y transition-colors"
            spellCheck={false}
          />
        </div>
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={() => { reset(); onClose() }}>Cancel</Button>
          <Button loading={mutation.isPending} onClick={() => mutation.mutate()}>Create</Button>
        </div>
      </div>
    </Modal>
  )
}

function EditProfileModal({ profile, onClose }: { profile: Profile | null; onClose: () => void }) {
  const [name, setName] = useState('')
  const [config, setConfig] = useState('')
  const [error, setError] = useState('')
  const queryClient = useQueryClient()

  useEffect(() => {
    if (profile) {
      setName(profile.name)
      setConfig(profile.profile)
      setError('')
    }
  }, [profile])

  const mutation = useMutation({
    mutationFn: () => profile && profilesApi.update(profile.tag, name, config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profiles-all'] })
      setError('')
      onClose()
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      setError(err?.response?.data?.detail || 'Failed to update profile')
    },
  })

  if (!profile) return null

  return (
    <Modal open={!!profile} onClose={onClose} title={`Edit: ${profile.name}`} wide>
      <div className="space-y-4">
        {error && (
          <div className="bg-danger/10 border border-danger/20 rounded-md px-3 py-2 text-xs text-danger">{error}</div>
        )}
        <div className="flex items-center gap-3">
          <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} className="flex-1" />
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-text-secondary uppercase tracking-wider">Tag (read-only)</label>
            <div className="bg-bg-primary border border-border rounded-md px-3 py-2 text-sm font-mono text-text-muted">
              {profile.tag}
            </div>
          </div>
        </div>
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-text-secondary uppercase tracking-wider">YAML Config</label>
            <span className="text-xs text-text-muted">{config.length} chars</span>
          </div>
          <textarea
            value={config}
            onChange={(e) => setConfig(e.target.value)}
            rows={20}
            className="bg-bg-primary border border-border rounded-md px-3 py-2 text-sm text-text-primary
              focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30
              font-mono resize-y transition-colors"
            spellCheck={false}
          />
        </div>
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button loading={mutation.isPending} onClick={() => mutation.mutate()}>Save Changes</Button>
        </div>
      </div>
    </Modal>
  )
}
