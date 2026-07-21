import { trafficLevel, type TrafficLevel } from '../../utils/format'

interface ProgressBarProps {
  percent: number
  /** Override the auto-computed color level. */
  level?: TrafficLevel
  /** Render the infinity/unlimited state. */
  unlimited?: boolean
  className?: string
}

const fills: Record<TrafficLevel, string> = {
  success: 'bg-success',
  warning: 'bg-warning',
  danger: 'bg-danger',
}

export default function ProgressBar({ percent, level, unlimited, className = '' }: ProgressBarProps) {
  if (unlimited) {
    return (
      <div className={`h-1.5 w-full rounded-full bg-bg-tertiary overflow-hidden ${className}`}>
        <div className="h-full w-full bg-accent/30" />
      </div>
    )
  }

  const clamped = Math.max(0, Math.min(100, percent))
  const color = fills[level ?? trafficLevel(clamped)]

  return (
    <div className={`h-1.5 w-full rounded-full bg-bg-tertiary overflow-hidden ${className}`}>
      <div
        className={`h-full rounded-full transition-all duration-300 ${color}`}
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}
