import { useEffect, useRef, useState } from 'react'
import { ArrowPathIcon, CheckIcon, ChevronDownIcon } from '@heroicons/react/24/outline'
import { AUTO_REFRESH_OPTIONS } from '../../utils/useAutoRefresh'

interface AutoRefreshSelectProps {
  value: number
  onChange: (ms: number) => void
}

/**
 * "Auto refresh" dropdown matching the design system — a themed popover with
 * highlighted active option, instead of a native OS-styled <select>.
 * Off / 5 / 10 / 20 / 30 seconds. The icon spins while auto-refresh is active.
 */
export default function AutoRefreshSelect({ value, onChange }: AutoRefreshSelectProps) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const active = value > 0
  const current = AUTO_REFRESH_OPTIONS.find((o) => o.value === value) ?? AUTO_REFRESH_OPTIONS[0]

  useEffect(() => {
    if (!open) return
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setOpen(false)
    document.addEventListener('mousedown', onClick)
    window.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onClick)
      window.removeEventListener('keydown', onKey)
    }
  }, [open])

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="listbox"
        aria-expanded={open}
        className={`inline-flex items-center h-9 gap-2 pl-2.5 pr-2.5 bg-bg-tertiary border rounded-md
          text-xs font-medium transition-all duration-150 cursor-pointer
          hover:bg-bg-hover hover:border-border-light focus:outline-none focus:ring-2 focus:ring-accent/30
          ${open ? 'border-accent ring-2 ring-accent/30' : 'border-border'}`}
      >
        <ArrowPathIcon
          className={`w-3.5 h-3.5 shrink-0 ${active ? 'text-accent animate-spin' : 'text-text-muted'}`}
          style={active ? { animationDuration: '2.5s' } : undefined}
        />
        <span className="text-text-muted whitespace-nowrap">Auto refresh</span>
        <span className="text-text-primary tabular-nums whitespace-nowrap">{current.label}</span>
        <ChevronDownIcon className={`w-3.5 h-3.5 text-text-muted transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>

      {open && (
        <div
          role="listbox"
          className="absolute right-0 z-30 mt-1.5 w-40 p-1 bg-bg-elevated border border-border-light rounded-lg
            shadow-elevated animate-scale-in origin-top-right"
        >
          {AUTO_REFRESH_OPTIONS.map((opt) => {
            const selected = opt.value === value
            return (
              <button
                key={opt.value}
                role="option"
                aria-selected={selected}
                onClick={() => {
                  onChange(opt.value)
                  setOpen(false)
                }}
                className={`flex w-full items-center justify-between gap-2 px-2.5 h-8 rounded-md text-xs font-medium
                  transition-colors cursor-pointer text-left
                  ${selected
                    ? 'bg-accent/10 text-accent'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'}`}
              >
                {opt.label}
                {selected && <CheckIcon className="w-3.5 h-3.5 shrink-0" />}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
