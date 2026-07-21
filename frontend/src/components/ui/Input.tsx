import { type InputHTMLAttributes, forwardRef } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, className = '', ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label className="text-xs font-medium text-text-secondary">{label}</label>
        )}
        <input
          ref={ref}
          className={`h-9 bg-bg-tertiary border rounded-md px-3 text-sm text-text-primary
            placeholder:text-text-muted transition-all duration-150
            focus:outline-none focus:ring-2 focus:ring-accent/30
            ${error ? 'border-danger focus:border-danger focus:ring-danger/25' : 'border-border focus:border-accent'}
            ${className}`}
          {...props}
        />
        {error ? (
          <span className="text-xs text-danger">{error}</span>
        ) : (
          hint && <span className="text-xs text-text-muted">{hint}</span>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'
export default Input
