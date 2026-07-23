import { useState, useMemo, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { profilesApi } from '../api/profiles'
import type { Profile } from '../types'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Modal from '../components/ui/Modal'
import ConfirmDialog from '../components/ui/ConfirmDialog'
import { Card, ErrorState, EmptyState, Skeleton } from '../components/ui/Misc'
import {
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  ArrowPathIcon,
  UserCircleIcon,
  ExclamationCircleIcon,
  QuestionMarkCircleIcon,
} from '@heroicons/react/24/outline'

export default function Profiles() {
  const [search, setSearch] = useState('')
  const [createOpen, setCreateOpen] = useState(false)
  const [editProfile, setEditProfile] = useState<Profile | null>(null)
  const [deleteProfile, setDeleteProfile] = useState<Profile | null>(null)
  const queryClient = useQueryClient()

  const { data: profiles, isLoading, isError, error, refetch, isFetching } = useQuery({
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
      (p) => p.name.toLowerCase().includes(q) || p.tag.toLowerCase().includes(q)
    )
  }, [profiles, search])

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter profiles..."
            className="w-full h-9 bg-bg-tertiary border border-border rounded-md pl-9 pr-3 text-sm text-text-primary
              placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/30 transition-all"
          />
        </div>
        <span className="text-xs text-text-muted tabular-nums">{filtered.length} profiles</span>
        <Button variant="secondary" onClick={() => refetch()}>
          <ArrowPathIcon className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
        <Button onClick={() => setCreateOpen(true)}>
          <PlusIcon className="w-4 h-4" />
          New Profile
        </Button>
      </div>

      {isError ? (
        <Card>
          <ErrorState
            message={(error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to load profiles'}
            onRetry={() => refetch()}
          />
        </Card>
      ) : (
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left bg-bg-tertiary/40">
                  <Th>Name</Th>
                  <Th>Tag</Th>
                  <Th>Config Preview</Th>
                  <Th className="text-right">Actions</Th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {isLoading &&
                  Array.from({ length: 5 }).map((_, i) => (
                    <tr key={i}>
                      <td className="px-5 py-3"><Skeleton className="h-4 w-28" /></td>
                      <td className="px-5 py-3"><Skeleton className="h-5 w-20 rounded" /></td>
                      <td className="px-5 py-3"><Skeleton className="h-4 w-full max-w-xs" /></td>
                      <td className="px-5 py-3"><Skeleton className="h-4 w-12 ml-auto" /></td>
                    </tr>
                  ))}
                {!isLoading && filtered.length === 0 && (
                  <tr>
                    <td colSpan={4}>
                      <EmptyState
                        message={profiles?.length === 0 ? 'No profiles yet' : 'No matching profiles'}
                        hint={profiles?.length === 0 ? 'Create your first configuration profile to get started.' : 'Try adjusting your search filter.'}
                        icon={<UserCircleIcon className="w-6 h-6" />}
                        action={
                          profiles?.length === 0 ? (
                            <Button size="sm" onClick={() => setCreateOpen(true)}>
                              <PlusIcon className="w-4 h-4" />
                              New Profile
                            </Button>
                          ) : undefined
                        }
                      />
                    </td>
                  </tr>
                )}
                {!isLoading &&
                  filtered.map((profile) => (
                    <tr key={profile.tag} className="hover:bg-bg-hover transition-colors group">
                      <td className="px-5 py-3">
                        <span className="text-sm text-text-primary font-medium">{profile.name}</span>
                      </td>
                      <td className="px-5 py-3">
                        <code className="text-xs font-mono text-accent bg-accent/10 px-2 py-0.5 rounded">{profile.tag}</code>
                      </td>
                      <td className="px-5 py-3 max-w-xs">
                        <span className="text-xs text-text-muted font-mono truncate block">{profile.profile.slice(0, 80)}…</span>
                      </td>
                      <td className="px-5 py-3 text-right">
                        <div className="flex items-center justify-end gap-1 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
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
        </Card>
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

function Th({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <th className={`px-5 py-3 text-xs font-semibold text-text-muted uppercase tracking-wider ${className}`}>
      {children}
    </th>
  )
}

function FormError({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-2 bg-danger/10 border border-danger/20 rounded-lg px-3 py-2.5 text-sm text-danger">
      <ExclamationCircleIcon className="w-4 h-4 shrink-0" />
      <span>{message}</span>
    </div>
  )
}

function ProfileHelpModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <Modal open={open} onClose={onClose} title="Как создать профиль">
      <div className="space-y-4 text-sm text-text-primary">
        <section>
          <p className="font-semibold text-text-primary mb-1">Что такое профиль?</p>
          <p className="text-text-secondary">Профиль - переиспользуемый YAML-шаблон конфигурации OLCRTC. На его основе для каждого подписчика автоматически создаётся отдельный контейнер.</p>
        </section>
        <section>
          <p className="font-semibold text-text-primary mb-1">Как создать профиль?</p>
          <ol className="list-decimal list-inside space-y-1 text-text-secondary">
            <li>Введите отображаемое имя (например, <code className="text-xs font-mono text-accent bg-accent/10 px-1 rounded">Germany - VP8</code>).</li>
            <li>Введите тег - короткий уникальный идентификатор без символа <code className="text-xs font-mono text-accent bg-accent/10 px-1 rounded">-</code> (например, <code className="text-xs font-mono text-accent bg-accent/10 px-1 rounded">de_vp8</code>).</li>
            <li>Вставьте YAML-конфигурацию в поле ниже и нажмите <strong>Create Profile</strong>.</li>
          </ol>
        </section>
        <section>
          <p className="font-semibold text-text-primary mb-1">Важные параметры</p>
          <ul className="space-y-1 text-text-secondary">
            <li><code className="text-xs font-mono text-accent bg-accent/10 px-1 rounded">tag</code> - уникальный идентификатор; <span className="text-warning">не используйте</span> символ <code className="text-xs font-mono text-accent bg-accent/10 px-1 rounded">-</code>, иначе система трафика не сможет определить владельца контейнера.</li>
            <li><code className="text-xs font-mono text-accent bg-accent/10 px-1 rounded">crypto.key</code> - оставьте пустым (<code className="text-xs font-mono text-accent bg-accent/10 px-1 rounded">key: ""</code>); панель сама генерирует уникальный ключ для каждого пользователя.</li>
            <li><code className="text-xs font-mono text-accent bg-accent/10 px-1 rounded">room.id</code> - для Jitsi укажите только базовый URL сервера; панель добавит случайное имя комнаты автоматически.</li>
            <li><code className="text-xs font-mono text-accent bg-accent/10 px-1 rounded">net.transport</code> - один из: <code className="text-xs font-mono text-accent bg-accent/10 px-1 rounded">datachannel</code>, <code className="text-xs font-mono text-accent bg-accent/10 px-1 rounded">vp8channel</code>, <code className="text-xs font-mono text-accent bg-accent/10 px-1 rounded">seichannel</code>, <code className="text-xs font-mono text-accent bg-accent/10 px-1 rounded">videochannel</code>.</li>
          </ul>
        </section>
        <section className="bg-bg-tertiary rounded-lg px-3 py-2.5">
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-1.5">Минимальный пример</p>
          <pre className="text-xs font-mono text-text-secondary leading-relaxed whitespace-pre">{`mode: srv
auth:
  provider: jitsi
room:
  id: "https://jitsi.example.org"
crypto:
  key: ""
net:
  transport: datachannel
  dns: "8.8.8.8:53"
data: data`}</pre>
        </section>
        <p className="text-xs text-text-muted">Редактирование профиля останавливает все контейнеры с этим тегом - они пересоздадутся при следующем обновлении подписки.</p>
      </div>
    </Modal>
  )
}

function CreateProfileModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [name, setName] = useState('')
  const [tag, setTag] = useState('')
  const [config, setConfig] = useState('')
  const [error, setError] = useState('')
  const [helpOpen, setHelpOpen] = useState(false)
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
    <>
      <Modal
        open={open}
        onClose={() => { reset(); onClose() }}
        title="Create Profile"
        description="Add a new configuration profile"
        wide
        headerAction={
          <button
            onClick={() => setHelpOpen(true)}
            className="flex items-center justify-center w-6 h-6 rounded-full bg-success/15 text-success hover:bg-success/25 transition-colors cursor-pointer"
            title="Как создать профиль"
          >
            <QuestionMarkCircleIcon className="w-5 h-5" />
          </button>
        }
      >
        <div className="space-y-4">
          {error && <FormError message={error} />}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Display name" />
            <Input label="Tag" value={tag} onChange={(e) => setTag(e.target.value)} placeholder="unique_tag" />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-text-secondary">YAML Config</label>
            <textarea
              value={config}
              onChange={(e) => setConfig(e.target.value)}
              placeholder="Paste YAML configuration here..."
              rows={16}
              className="bg-bg-tertiary border border-border rounded-md px-3 py-2.5 text-sm text-text-primary leading-relaxed
                placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/30
                font-mono resize-y transition-all"
              spellCheck={false}
            />
          </div>
          <div className="flex justify-end gap-2 pt-1">
            <Button variant="secondary" onClick={() => { reset(); onClose() }}>Cancel</Button>
            <Button loading={mutation.isPending} onClick={() => mutation.mutate()}>Create Profile</Button>
          </div>
        </div>
      </Modal>
      <ProfileHelpModal open={helpOpen} onClose={() => setHelpOpen(false)} />
    </>
  )
}

function EditProfileModal({ profile, onClose }: { profile: Profile | null; onClose: () => void }) {
  const [name, setName] = useState('')
  const [config, setConfig] = useState('')
  const [error, setError] = useState('')
  const [helpOpen, setHelpOpen] = useState(false)
  const queryClient = useQueryClient()

  useEffect(() => {
    if (profile) {
      setName(profile.name)
      setConfig(profile.profile)
      setError('')
    }
  }, [profile])

  const mutation = useMutation({
    mutationFn: () => profilesApi.update(profile!.tag, name, config),
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
    <>
      <Modal
        open={!!profile}
        onClose={onClose}
        title={`Edit: ${profile.name}`}
        description={`Tag: ${profile.tag}`}
        wide
        headerAction={
            <button
              onClick={() => setHelpOpen(true)}
              className="flex items-center justify-center w-6 h-6 rounded-full bg-success/15 text-success hover:bg-success/25 transition-colors cursor-pointer"
              title="Как создать профиль"
            >
              <QuestionMarkCircleIcon className="w-5 h-5" />
            </button>
          }
      >
        <div className="space-y-4">
          {error && <FormError message={error} />}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} />
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-text-secondary">Tag (read-only)</label>
              <div className="h-9 flex items-center bg-bg-primary border border-border rounded-md px-3 text-sm font-mono text-text-muted">
                {profile.tag}
              </div>
            </div>
          </div>
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-text-secondary">YAML Config</label>
              <span className="text-xs text-text-muted tabular-nums">{config.length} chars</span>
            </div>
            <textarea
              value={config}
              onChange={(e) => setConfig(e.target.value)}
              rows={18}
              className="bg-bg-tertiary border border-border rounded-md px-3 py-2.5 text-sm text-text-primary leading-relaxed
                focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/30
                font-mono resize-y transition-all"
              spellCheck={false}
            />
          </div>
          <div className="flex justify-end gap-2 pt-1">
            <Button variant="secondary" onClick={onClose}>Cancel</Button>
            <Button loading={mutation.isPending} onClick={() => mutation.mutate()}>Save Changes</Button>
          </div>
        </div>
      </Modal>
      <ProfileHelpModal open={helpOpen} onClose={() => setHelpOpen(false)} />
    </>
  )
}
