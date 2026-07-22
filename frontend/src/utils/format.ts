const UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

/** Format a byte count into a human-readable string (base 1024). */
export function formatBytes(bytes: number, decimals = 1): string {
  if (!bytes || bytes <= 0) return '0 B'
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), UNITS.length - 1)
  const value = bytes / Math.pow(1024, i)
  return `${value.toFixed(i === 0 ? 0 : decimals)} ${UNITS[i]}`
}

/** Format a bytes-per-second rate into a human-readable speed. */
export function formatRate(bytesPerSecond: number): string {
  return `${formatBytes(bytesPerSecond)}/s`
}

/** Format elapsed time since a start date as a compact duration, e.g. "5h 23m". */
export function formatUptime(since: Date, now: Date = new Date()): string {
  let seconds = Math.floor((now.getTime() - since.getTime()) / 1000)
  if (!Number.isFinite(seconds) || seconds < 0) return '—'
  const days = Math.floor(seconds / 86400)
  seconds -= days * 86400
  const hours = Math.floor(seconds / 3600)
  seconds -= hours * 3600
  const minutes = Math.floor(seconds / 60)
  seconds -= minutes * 60
  if (days > 0) return `${days}d ${hours}h`
  if (hours > 0) return `${hours}h ${minutes}m`
  if (minutes > 0) return `${minutes}m ${seconds}s`
  return `${seconds}s`
}

/** Convert a byte count into whole gigabytes (for input fields). */
export function bytesToGB(bytes: number): number {
  return bytes / (1024 * 1024 * 1024)
}

/** Convert gigabytes into bytes. */
export function gbToBytes(gb: number): number {
  return Math.round(gb * 1024 * 1024 * 1024)
}

/** Percentage of the limit used (0-100). Returns 0 for unlimited/no-limit. */
export function trafficPercent(used: number, limit: number): number {
  if (!limit || limit <= 0) return 0
  return Math.min(100, Math.round((used / limit) * 100))
}

/** Tailwind color token for a usage percentage. */
export type TrafficLevel = 'success' | 'warning' | 'danger'

export function trafficLevel(percent: number): TrafficLevel {
  if (percent >= 90) return 'danger'
  if (percent >= 70) return 'warning'
  return 'success'
}

/**
 * Build a user's subscription URL from the `VITE_SUB_URL_TEMPLATE` template,
 * replacing every `{uuid}` placeholder with the given short UUID.
 * Falls back to `<origin>/sub/{uuid}` when the template is not configured.
 */
export function buildSubUrl(shortUuid: string): string {
  const template = import.meta.env.VITE_SUB_URL_TEMPLATE?.trim()
  if (!template) return `${window.location.origin}/sub/${shortUuid}`
  return template.replaceAll('{uuid}', shortUuid)
}

