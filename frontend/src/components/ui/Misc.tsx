import { type ReactNode } from 'react'
import { InboxIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'

interface CardProps {
  children: ReactNode
  className?: string
}

export function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`bg-bg-secondary border border-border rounded-xl shadow-soft ${className}`}>
      {children}
    </div>
  )
}

interface CardHeaderProps {
  title: string
  action?: ReactNode
}

export function CardHeader({ title, action }: CardHeaderProps) {
  return (
    <div className="px-5 py-3.5 border-b border-border flex items-center justify-between gap-3">
      <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">{title}</h3>
      {action}
    </div>
  )
}

interface TabsProps {
  tabs: { key: string; label: string }[]
  active: string
  onChange: (key: string) => void
}

export function Tabs({ tabs, active, onChange }: TabsProps) {
  return (
    <div className="flex gap-1 border-b border-border">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={`relative px-3.5 py-2.5 text-sm font-medium transition-colors cursor-pointer
            ${active === tab.key
              ? 'text-text-primary'
              : 'text-text-secondary hover:text-text-primary'}`}
        >
          {tab.label}
          {active === tab.key && (
            <span className="absolute inset-x-0 -bottom-px h-0.5 bg-accent rounded-full" />
          )}
        </button>
      ))}
    </div>
  )
}

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: ReactNode
  trend?: 'up' | 'down' | 'neutral'
}

export function StatCard({ title, value, subtitle, icon }: StatCardProps) {
  return (
    <div className="group bg-bg-secondary border border-border rounded-xl p-5 shadow-soft
      transition-all duration-200 hover:border-border-light hover:-translate-y-0.5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium text-text-muted uppercase tracking-wider">{title}</p>
          <p className="text-3xl font-bold text-text-primary mt-2 tracking-tight tabular-nums">{value}</p>
          {subtitle && <p className="text-xs text-text-secondary mt-1.5">{subtitle}</p>}
        </div>
        {icon && (
          <div className="shrink-0 flex items-center justify-center w-10 h-10 rounded-lg bg-accent/10 text-accent
            transition-colors group-hover:bg-accent/15">
            {icon}
          </div>
        )}
      </div>
    </div>
  )
}

export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-md ${className}`} />
}

export function EmptyState({
  message = 'No data available',
  hint,
  icon,
  action,
}: {
  message?: string
  hint?: string
  icon?: ReactNode
  action?: ReactNode
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-bg-tertiary text-text-muted mb-4">
        {icon || <InboxIcon className="w-6 h-6" />}
      </div>
      <p className="text-sm font-medium text-text-secondary">{message}</p>
      {hint && <p className="text-xs text-text-muted mt-1.5 max-w-xs">{hint}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}

export function LoadingState({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="w-7 h-7 border-2 border-accent border-t-transparent rounded-full animate-spin mb-3" />
      <p className="text-sm text-text-muted">{text}</p>
    </div>
  )
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-danger/10 text-danger mb-4">
        <ExclamationTriangleIcon className="w-6 h-6" />
      </div>
      <p className="text-sm font-medium text-text-primary">Something went wrong</p>
      <p className="text-xs text-text-muted mt-1.5 max-w-sm">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 text-xs font-medium text-accent hover:text-accent-hover cursor-pointer transition-colors"
        >
          Try again
        </button>
      )}
    </div>
  )
}
