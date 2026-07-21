import { useEffect } from 'react'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import Button from './Button'

interface ConfirmDialogProps {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  confirmLabel?: string
  loading?: boolean
}

export default function ConfirmDialog({
  open, onClose, onConfirm, title, message, confirmLabel = 'Delete', loading,
}: ConfirmDialogProps) {
  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && !loading && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, loading, onClose])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm animate-fade-in" onClick={() => !loading && onClose()} />
      <div className="relative bg-bg-secondary border border-border-light rounded-xl shadow-elevated w-full max-w-sm animate-scale-in">
        <div className="p-5">
          <div className="flex gap-3.5">
            <div className="shrink-0 flex items-center justify-center w-9 h-9 rounded-full bg-danger/10">
              <ExclamationTriangleIcon className="w-5 h-5 text-danger" />
            </div>
            <div className="pt-0.5">
              <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
              <p className="text-sm text-text-secondary mt-1 leading-relaxed">{message}</p>
            </div>
          </div>
        </div>
        <div className="flex justify-end gap-2 px-5 py-3.5 border-t border-border bg-bg-primary/40 rounded-b-xl">
          <Button variant="secondary" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className="inline-flex items-center justify-center gap-1.5 h-8.5 px-3.5 text-sm font-medium rounded-md
              bg-danger text-white shadow-soft transition-all duration-150 cursor-pointer active:scale-[0.98]
              hover:bg-red-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-danger/50
              disabled:opacity-50 disabled:pointer-events-none"
          >
            {loading && (
              <svg className="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            )}
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
