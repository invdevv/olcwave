import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { StatCard } from '../components/ui/Misc'
import { usersApi } from '../api/users'
import { profilesApi } from '../api/profiles'
import {
  UsersIcon,
  UserCircleIcon,
  ServerIcon,
  LinkIcon,
} from '@heroicons/react/24/outline'

export default function Dashboard() {
  const usersQuery = useQuery({
    queryKey: ['users-all'],
    queryFn: () => usersApi.getAll().then((r) => r.data),
  })
  const profilesQuery = useQuery({
    queryKey: ['profiles-all'],
    queryFn: () => profilesApi.getAll().then((r) => r.data),
  })

  const users = usersQuery.data || []
  const profiles = profilesQuery.data || []

  const activeUsers = users.filter((u) => new Date(u.expires_at) > new Date()).length

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">Overview</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <StatCard
            title="Users"
            value={users.length}
            subtitle={`${activeUsers} active`}
            icon={<UsersIcon className="w-5 h-5" />}
          />
          <StatCard
            title="Profiles"
            value={profiles.length}
            subtitle={`${profiles.length} configs`}
            icon={<UserCircleIcon className="w-5 h-5" />}
          />
          <StatCard
            title="Status"
            value="Online"
            subtitle="API responding"
            icon={<ServerIcon className="w-5 h-5" />}
          />
          <StatCard
            title="Subscriptions"
            value={users.length}
            subtitle="Public links"
            icon={<LinkIcon className="w-5 h-5" />}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <RecentUsers users={users.slice(0, 5)} />
        <RecentProfiles profiles={profiles.slice(0, 5)} />
      </div>

      <QuickLookup />
    </div>
  )
}

function RecentUsers({ users }: { users: import('../types').User[] }) {
  return (
    <div className="bg-bg-secondary border border-border rounded-lg">
      <div className="px-4 py-2.5 border-b border-border flex items-center justify-between">
        <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider">Recent Users</h3>
        <a href="/users" className="text-xs text-accent hover:text-accent-hover cursor-pointer">View all</a>
      </div>
      {users.length === 0 ? (
        <p className="px-4 py-6 text-xs text-text-muted text-center">No users yet</p>
      ) : (
        <div className="divide-y divide-border">
          {users.map((u) => (
            <div key={u.short_uuid} className="px-4 py-2.5 flex items-center justify-between hover:bg-bg-hover transition-colors">
              <code className="text-xs font-mono text-accent">{u.short_uuid}</code>
              <span className="text-xs text-text-muted">{new Date(u.created_at).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function RecentProfiles({ profiles }: { profiles: import('../types').Profile[] }) {
  return (
    <div className="bg-bg-secondary border border-border rounded-lg">
      <div className="px-4 py-2.5 border-b border-border flex items-center justify-between">
        <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider">Recent Profiles</h3>
        <a href="/profiles" className="text-xs text-accent hover:text-accent-hover cursor-pointer">View all</a>
      </div>
      {profiles.length === 0 ? (
        <p className="px-4 py-6 text-xs text-text-muted text-center">No profiles yet</p>
      ) : (
        <div className="divide-y divide-border">
          {profiles.map((p) => (
            <div key={p.tag} className="px-4 py-2.5 flex items-center justify-between hover:bg-bg-hover transition-colors">
              <span className="text-sm text-text-primary">{p.name}</span>
              <code className="text-xs font-mono text-text-muted">{p.tag}</code>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function QuickLookup() {
  const [uuid, setUuid] = useState('')
  const [tag, setTag] = useState('')

  const userQuery = useQuery({
    queryKey: ['user-lookup-dash', uuid],
    queryFn: () => usersApi.getByShortUuid(uuid).then((r) => r.data),
    enabled: false,
  })

  const profileQuery = useQuery({
    queryKey: ['profile-lookup-dash', tag],
    queryFn: () => profilesApi.getByTag(tag).then((r) => r.data),
    enabled: false,
  })

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4">
      <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">Quick Lookup</h3>
      <div className="space-y-3">
        <div className="flex gap-2">
          <input
            value={uuid}
            onChange={(e) => setUuid(e.target.value)}
            placeholder="User short UUID"
            className="flex-1 bg-bg-primary border border-border rounded-md px-3 py-1.5 text-sm text-text-primary
              placeholder:text-text-muted focus:outline-none focus:border-accent"
          />
          <button
            onClick={() => uuid && userQuery.refetch()}
            disabled={!uuid}
            className="px-3 py-1.5 text-xs font-medium bg-bg-tertiary border border-border rounded-md
              text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-colors cursor-pointer
              disabled:opacity-40"
          >
            Lookup
          </button>
        </div>
        {userQuery.data && (
          <div className="bg-bg-primary border border-border rounded-md p-3 text-xs space-y-1 animate-fade-in">
            <div><span className="text-text-muted">UUID:</span> <span className="text-text-primary font-mono">{userQuery.data.short_uuid}</span></div>
            <div><span className="text-text-muted">Created:</span> <span className="text-text-primary">{new Date(userQuery.data.created_at).toLocaleDateString()}</span></div>
            <div><span className="text-text-muted">Expires:</span> <span className="text-text-primary">{new Date(userQuery.data.expires_at).toLocaleDateString()}</span></div>
          </div>
        )}
        {userQuery.isError && <p className="text-xs text-danger">User not found</p>}

        <div className="flex gap-2">
          <input
            value={tag}
            onChange={(e) => setTag(e.target.value)}
            placeholder="Profile tag"
            className="flex-1 bg-bg-primary border border-border rounded-md px-3 py-1.5 text-sm text-text-primary
              placeholder:text-text-muted focus:outline-none focus:border-accent"
          />
          <button
            onClick={() => tag && profileQuery.refetch()}
            disabled={!tag}
            className="px-3 py-1.5 text-xs font-medium bg-bg-tertiary border border-border rounded-md
              text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-colors cursor-pointer
              disabled:opacity-40"
          >
            Lookup
          </button>
        </div>
        {profileQuery.data && (
          <div className="bg-bg-primary border border-border rounded-md p-3 text-xs space-y-1 animate-fade-in">
            <div><span className="text-text-muted">Name:</span> <span className="text-text-primary">{profileQuery.data.name}</span></div>
            <div><span className="text-text-muted">Tag:</span> <span className="text-text-primary font-mono">{profileQuery.data.tag}</span></div>
          </div>
        )}
        {profileQuery.isError && <p className="text-xs text-danger">Profile not found</p>}
      </div>
    </div>
  )
}
