import { useCallback, useState } from 'react'

/** Auto-refresh interval options, in milliseconds. `0` means off. */
export const AUTO_REFRESH_OPTIONS: { value: number; label: string }[] = [
  { value: 0, label: 'Off' },
  { value: 5000, label: '5 seconds' },
  { value: 10000, label: '10 seconds' },
  { value: 20000, label: '20 seconds' },
  { value: 30000, label: '30 seconds' },
]

const STORAGE_PREFIX = 'auto-refresh:'

/** Default interval when the user has not chosen one yet (5 seconds). */
const DEFAULT_MS = 5000

function read(key: string): number {
  try {
    const raw = localStorage.getItem(STORAGE_PREFIX + key)
    if (raw === null) return DEFAULT_MS
    const parsed = Number(raw)
    return AUTO_REFRESH_OPTIONS.some((o) => o.value === parsed) ? parsed : DEFAULT_MS
  } catch {
    return DEFAULT_MS
  }
}

/**
 * Persisted auto-refresh interval for a page.
 *
 * @param key unique per page (e.g. 'users', 'containers', 'dashboard')
 * @returns [intervalMs, setInterval] — pass `intervalMs || false` to a
 *          react-query `refetchInterval`. `0` disables auto-refresh.
 */
export function useAutoRefresh(key: string): [number, (ms: number) => void] {
  const [interval, setIntervalState] = useState<number>(() => read(key))

  const set = useCallback(
    (ms: number) => {
      setIntervalState(ms)
      try {
        localStorage.setItem(STORAGE_PREFIX + key, String(ms))
      } catch {
        /* ignore storage failures */
      }
    },
    [key]
  )

  return [interval, set]
}
