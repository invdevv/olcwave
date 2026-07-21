import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { StatCard } from '../components/ui/Misc'
import { usersApi } from '../api/users'
import { profilesApi } from '../api/profiles'
import {
  LinkIcon,
  ServerIcon,
} from '@heroicons/react/24/outline'

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">System Overview</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <StatCard
            title="Status"
            value="Online"
            subtitle="API responding"
            icon={<ServerIcon className="w-5 h-5" />}
          />
          <StatCard
            title="Note"
            value="—"
            subtitle="Backend has no aggregate stats endpoint"
            icon={<LinkIcon className="w-5 h-5" />}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <QuickLookup />
        <RecentInfo />
      </div>
    </div>
  )
}

function QuickLookup() {
  const [uuid, setUuid] = useState('')
  const [tag, setTag] = useState('')

  const userQuery = useQuery({
    queryKey: ['user-lookup', uuid],
    queryFn: () => usersApi.getByShortUuid(uuid).then((r) => r.data),
    enabled: false,
  })

  const profileQuery = useQuery({
    queryKey: ['profile-lookup', tag],
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

function RecentInfo() {
  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4">
      <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">About</h3>
      <div className="space-y-2 text-xs text-text-secondary">
        <p>OLC WebRTC subscription manager with Remnawave integration.</p>
        <div className="border-t border-border pt-2 mt-2">
          <p className="text-text-muted uppercase tracking-wider mb-1">Backend Capabilities</p>
          <ul className="space-y-1 list-disc list-inside">
            <li>User management (lookup by short UUID)</li>
            <li>Profile management (CRUD by tag)</li>
            <li>Public subscription endpoint</li>
            <li>Docker container orchestration</li>
          </ul>
        </div>
        <div className="border-t border-border pt-2 mt-2">
          <p className="text-text-muted uppercase tracking-wider mb-1">Limitations</p>
          <ul className="space-y-1 list-disc list-inside text-warning/80">
            <li>No "list all users" endpoint</li>
            <li>No "list all profiles" endpoint</li>
            <li>Database wiped on backend restart</li>
          </ul>
        </div>
      </div>
    </div>
  )
}


