import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { StatCard, Card, CardHeader, Skeleton, EmptyState } from '../components/ui/Misc'
import { usersApi } from '../api/users'
import { profilesApi } from '../api/profiles'
import { containersApi } from '../api/containers'
import { formatBytes } from '../utils/format'
import type { User, Profile } from '../types'
import {
  UsersIcon,
  UserCircleIcon,
  ServerIcon,
  LinkIcon,
  ArrowRightIcon,
  MagnifyingGlassIcon,
  ChartBarIcon,
  CubeIcon,
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
  const containersQuery = useQuery({
    queryKey: ['containers-all'],
    queryFn: () => containersApi.getAll().then((r) => r.data),
  })

  const users = usersQuery.data || []
  const profiles = profilesQuery.data || []
  const containers = containersQuery.data || []
  const loading = usersQuery.isLoading || profilesQuery.isLoading

  const activeUsers = users.filter((u) => new Date(u.expires_at) > new Date()).length
  const totalTrafficUsed = users.reduce((sum, u) => sum + (u.traffic_used_bytes || 0), 0)
  const exceededUsers = users.filter(
    (u) => u.traffic_limit_bytes > 0 && u.traffic_used_bytes >= u.traffic_limit_bytes
  ).length

  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-sm font-semibold text-text-secondary mb-4">Overview</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {loading ? (
            Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-[104px] rounded-xl" />)
          ) : (
            <>
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
            </>
          )}
        </div>
      </section>

      <section>
        <h2 className="text-sm font-semibold text-text-secondary mb-4">Total Traffic Usage</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {loading ? (
            Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-[104px] rounded-xl" />)
          ) : (
            <>
              <StatCard
                title="Used"
                value={formatBytes(totalTrafficUsed)}
                subtitle="Across all users"
                icon={<ChartBarIcon className="w-5 h-5" />}
              />
              <StatCard
                title="Users"
                value={users.length}
                subtitle={`${exceededUsers} over limit`}
                icon={<UsersIcon className="w-5 h-5" />}
              />
              <StatCard
                title="Containers"
                value={containers.length}
                subtitle={`${containers.filter((c) => c.status === 'running').length} running`}
                icon={<CubeIcon className="w-5 h-5" />}
              />
              <StatCard
                title="Profiles"
                value={profiles.length}
                subtitle="Active configs"
                icon={<UserCircleIcon className="w-5 h-5" />}
              />
            </>
          )}
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <RecentUsers users={users.slice(0, 5)} loading={loading} />
        <RecentProfiles profiles={profiles.slice(0, 5)} loading={loading} />
      </section>

      <QuickLookup />
    </div>
  )
}

function RowSkeleton() {
  return (
    <div className="px-5 py-3 flex items-center justify-between">
      <Skeleton className="h-3.5 w-32" />
      <Skeleton className="h-3.5 w-16" />
    </div>
  )
}

function RecentUsers({ users, loading }: { users: User[]; loading: boolean }) {
  return (
    <Card>
      <CardHeader
        title="Recent Users"
        action={
          <Link to="/users" className="flex items-center gap-1 text-xs font-medium text-accent hover:text-accent-hover transition-colors">
            View all <ArrowRightIcon className="w-3 h-3" />
          </Link>
        }
      />
      {loading ? (
        <div className="divide-y divide-border">
          {Array.from({ length: 4 }).map((_, i) => <RowSkeleton key={i} />)}
        </div>
      ) : users.length === 0 ? (
        <EmptyState message="No users yet" icon={<UsersIcon className="w-6 h-6" />} />
      ) : (
        <div className="divide-y divide-border">
          {users.map((u) => (
            <div key={u.short_uuid} className="px-5 py-3 flex items-center justify-between hover:bg-bg-hover transition-colors">
              <code className="text-xs font-mono text-accent">{u.short_uuid}</code>
              <span className="text-xs text-text-muted">{new Date(u.created_at).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}

function RecentProfiles({ profiles, loading }: { profiles: Profile[]; loading: boolean }) {
  return (
    <Card>
      <CardHeader
        title="Recent Profiles"
        action={
          <Link to="/profiles" className="flex items-center gap-1 text-xs font-medium text-accent hover:text-accent-hover transition-colors">
            View all <ArrowRightIcon className="w-3 h-3" />
          </Link>
        }
      />
      {loading ? (
        <div className="divide-y divide-border">
          {Array.from({ length: 4 }).map((_, i) => <RowSkeleton key={i} />)}
        </div>
      ) : profiles.length === 0 ? (
        <EmptyState message="No profiles yet" icon={<UserCircleIcon className="w-6 h-6" />} />
      ) : (
        <div className="divide-y divide-border">
          {profiles.map((p) => (
            <div key={p.tag} className="px-5 py-3 flex items-center justify-between hover:bg-bg-hover transition-colors">
              <span className="text-sm text-text-primary">{p.name}</span>
              <code className="text-xs font-mono text-text-muted">{p.tag}</code>
            </div>
          ))}
        </div>
      )}
    </Card>
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
    <section>
      <h2 className="text-sm font-semibold text-text-secondary mb-4">Quick Lookup</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <Card className="p-5">
          <div className="flex items-center gap-2 mb-3">
            <UsersIcon className="w-4 h-4 text-text-muted" />
            <h3 className="text-sm font-medium text-text-primary">Find User</h3>
          </div>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <input
                value={uuid}
                onChange={(e) => setUuid(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && uuid && userQuery.refetch()}
                placeholder="User short UUID"
                className="w-full h-9 bg-bg-tertiary border border-border rounded-md pl-9 pr-3 text-sm text-text-primary
                  placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/30 transition-all"
              />
            </div>
            <button
              onClick={() => uuid && userQuery.refetch()}
              disabled={!uuid}
              className="h-9 px-3.5 text-sm font-medium bg-bg-tertiary border border-border rounded-md
                text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-colors cursor-pointer
                disabled:opacity-40 disabled:pointer-events-none"
            >
              Lookup
            </button>
          </div>
          {userQuery.data && (
            <div className="mt-3 bg-bg-tertiary border border-border rounded-lg p-3 text-xs space-y-1.5 animate-fade-in">
              <Field label="UUID" value={userQuery.data.short_uuid} mono />
              <Field label="Created" value={new Date(userQuery.data.created_at).toLocaleString()} />
              <Field label="Expires" value={new Date(userQuery.data.expires_at).toLocaleString()} />
            </div>
          )}
          {userQuery.isError && <p className="mt-3 text-xs text-danger">User not found</p>}
        </Card>

        <Card className="p-5">
          <div className="flex items-center gap-2 mb-3">
            <UserCircleIcon className="w-4 h-4 text-text-muted" />
            <h3 className="text-sm font-medium text-text-primary">Find Profile</h3>
          </div>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <input
                value={tag}
                onChange={(e) => setTag(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && tag && profileQuery.refetch()}
                placeholder="Profile tag"
                className="w-full h-9 bg-bg-tertiary border border-border rounded-md pl-9 pr-3 text-sm text-text-primary
                  placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/30 transition-all"
              />
            </div>
            <button
              onClick={() => tag && profileQuery.refetch()}
              disabled={!tag}
              className="h-9 px-3.5 text-sm font-medium bg-bg-tertiary border border-border rounded-md
                text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-colors cursor-pointer
                disabled:opacity-40 disabled:pointer-events-none"
            >
              Lookup
            </button>
          </div>
          {profileQuery.data && (
            <div className="mt-3 bg-bg-tertiary border border-border rounded-lg p-3 text-xs space-y-1.5 animate-fade-in">
              <Field label="Name" value={profileQuery.data.name} />
              <Field label="Tag" value={profileQuery.data.tag} mono />
            </div>
          )}
          {profileQuery.isError && <p className="mt-3 text-xs text-danger">Profile not found</p>}
        </Card>
      </div>
    </section>
  )
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex justify-between gap-3">
      <span className="text-text-muted">{label}</span>
      <span className={`text-text-primary text-right truncate ${mono ? 'font-mono' : ''}`}>{value}</span>
    </div>
  )
}
