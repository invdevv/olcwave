import { type InputHTMLAttributes, forwardRef } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label className="text-xs font-medium text-text-secondary uppercase tracking-wider">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`bg-bg-primary border border-border rounded-md px-3 py-2 text-sm text-text-primary
            placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30
            transition-colors ${error ? 'border-danger' : ''} ${className}`}
          {...props}
        />
        {error && <span className="text-xs text-danger">{error}</span>}
      </div>
    )
  }
)

Input.displayName = 'Input'
export default Input
