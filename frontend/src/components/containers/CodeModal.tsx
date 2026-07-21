import { useState } from 'react'
import Modal from '../ui/Modal'
import { LoadingState, ErrorState } from '../ui/Misc'
import {
  ClipboardDocumentIcon,
  CheckIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'

interface CodeModalProps {
  open: boolean
  onClose: () => void
  title: string
  description?: string
  content: string
  loading?: boolean
  error?: string
  onRefresh?: () => void
  refreshing?: boolean
}

export default function CodeModal({
  open,
  onClose,
  title,
  description,
  content,
  loading,
  error,
  onRefresh,
  refreshing,
}: CodeModalProps) {
  const [copied, setCopied] = useState(false)

  const copy = () => {
    navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 1200)
  }

  return (
    <Modal open={open} onClose={onClose} title={title} description={description} wide>
      <div className="space-y-3">
        <div className="flex items-center justify-end gap-1.5">
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="inline-flex items-center gap-1.5 px-2.5 h-7 text-xs font-medium rounded-md
                text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-colors cursor-pointer"
              title="Refresh"
            >
              <ArrowPathIcon className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          )}
          <button
            onClick={copy}
            disabled={!content}
            className="inline-flex items-center gap-1.5 px-2.5 h-7 text-xs font-medium rounded-md
              text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-colors cursor-pointer
              disabled:opacity-40 disabled:pointer-events-none"
            title="Copy to clipboard"
          >
            {copied ? <CheckIcon className="w-3.5 h-3.5 text-success" /> : <ClipboardDocumentIcon className="w-3.5 h-3.5" />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>

        {loading ? (
          <div className="bg-bg-primary border border-border rounded-lg">
            <LoadingState text="Loading..." />
          </div>
        ) : error ? (
          <div className="bg-bg-primary border border-border rounded-lg">
            <ErrorState message={error} onRetry={onRefresh} />
          </div>
        ) : (
          <pre className="bg-bg-primary border border-border rounded-lg p-4 text-xs font-mono leading-relaxed
            text-text-secondary overflow-auto max-h-[60vh] whitespace-pre-wrap break-words">
            {content || 'No content'}
          </pre>
        )}
      </div>
    </Modal>
  )
}
