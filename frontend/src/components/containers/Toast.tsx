import { useEffect } from 'react'
import { CheckCircleIcon, ExclamationCircleIcon, XMarkIcon } from '@heroicons/react/24/outline'

export interface ToastData {
  id: number
  type: 'success' | 'error'
  message: string
}

export function ToastContainer({ toasts, onDismiss }: { toasts: ToastData[]; onDismiss: (id: number) => void }) {
  return (
    <div className="fixed bottom-6 right-6 z-[60] flex flex-col gap-2 w-full max-w-sm pointer-events-none">
      {toasts.map((t) => (
        <Toast key={t.id} toast={t} onDismiss={onDismiss} />
      ))}
    </div>
  )
}

function Toast({ toast, onDismiss }: { toast: ToastData; onDismiss: (id: number) => void }) {
  useEffect(() => {
    const timer = setTimeout(() => onDismiss(toast.id), 4000)
    return () => clearTimeout(timer)
  }, [toast.id, onDismiss])

  const isSuccess = toast.type === 'success'

  return (
    <div
      className={`pointer-events-auto flex items-start gap-2.5 px-3.5 py-3 rounded-lg border shadow-elevated
        animate-slide-in backdrop-blur-md
        ${isSuccess ? 'bg-success/10 border-success/20' : 'bg-danger/10 border-danger/20'}`}
    >
      {isSuccess ? (
        <CheckCircleIcon className="w-4.5 h-4.5 shrink-0 text-success mt-px" />
      ) : (
        <ExclamationCircleIcon className="w-4.5 h-4.5 shrink-0 text-danger mt-px" />
      )}
      <p className={`flex-1 text-xs leading-relaxed ${isSuccess ? 'text-success' : 'text-danger'}`}>{toast.message}</p>
      <button
        onClick={() => onDismiss(toast.id)}
        className="shrink-0 text-text-muted hover:text-text-primary transition-colors cursor-pointer"
      >
        <XMarkIcon className="w-3.5 h-3.5" />
      </button>
    </div>
  )
}
