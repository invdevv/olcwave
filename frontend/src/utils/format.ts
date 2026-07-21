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
