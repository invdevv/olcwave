import { type SelectHTMLAttributes, forwardRef } from 'react'
import { ChevronUpDownIcon } from '@heroicons/react/24/outline'

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  options: { value: string; label: string }[]
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, options, className = '', ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label className="text-xs font-medium text-text-secondary">{label}</label>
        )}
        <div className="relative">
          <select
            ref={ref}
            className={`h-9 w-full appearance-none bg-bg-tertiary border border-border rounded-md
              pl-3 pr-9 text-sm text-text-primary transition-all duration-150 cursor-pointer
              focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/30 ${className}`}
            {...props}
          >
            {options.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-bg-elevated">
                {opt.label}
              </option>
            ))}
          </select>
          <ChevronUpDownIcon className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
        </div>
      </div>
    )
  }
)

Select.displayName = 'Select'
export default Select
