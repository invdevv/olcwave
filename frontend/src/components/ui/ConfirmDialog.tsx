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
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-bg-secondary border border-border rounded-lg shadow-xl w-full max-w-sm mx-4 animate-fade-in">
        <div className="p-4">
          <h3 className="text-sm font-semibold text-text-primary mb-2">{title}</h3>
          <p className="text-sm text-text-secondary">{message}</p>
        </div>
        <div className="flex justify-end gap-2 px-4 py-3 border-t border-border">
          <button
            onClick={onClose}
            disabled={loading}
            className="px-3 py-1.5 text-sm rounded-md bg-bg-tertiary text-text-primary border border-border
              hover:bg-bg-hover transition-colors cursor-pointer"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className="px-3 py-1.5 text-sm rounded-md bg-danger text-white hover:bg-red-600
              transition-colors cursor-pointer disabled:opacity-50"
          >
            {loading ? 'Deleting...' : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
