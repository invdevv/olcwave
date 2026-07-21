import { useCallback, useState } from 'react'
import type { ToastData } from './Toast'

export function useToasts() {
  const [toasts, setToasts] = useState<ToastData[]>([])

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const push = useCallback((type: ToastData['type'], message: string) => {
    setToasts((prev) => [...prev, { id: Date.now() + Math.random(), type, message }])
  }, [])

  const success = useCallback((message: string) => push('success', message), [push])
  const error = useCallback((message: string) => push('error', message), [push])

  return { toasts, dismiss, success, error }
}
