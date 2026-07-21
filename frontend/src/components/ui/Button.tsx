import { type ButtonHTMLAttributes, forwardRef } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
}

const variants = {
  primary:
    'bg-accent text-white shadow-soft hover:bg-accent-hover focus-visible:ring-accent/50',
  secondary:
    'bg-bg-tertiary text-text-primary border border-border hover:bg-bg-hover hover:border-border-light focus-visible:ring-border-light',
  danger:
    'bg-danger/10 text-danger border border-danger/20 hover:bg-danger/20 hover:border-danger/40 focus-visible:ring-danger/40',
  ghost:
    'text-text-secondary hover:text-text-primary hover:bg-bg-hover focus-visible:ring-border-light',
}

const sizes = {
  sm: 'h-7 px-2.5 text-xs gap-1',
  md: 'h-8.5 px-3.5 text-sm gap-1.5',
  lg: 'h-10 px-4.5 text-sm gap-2',
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', loading, className = '', children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={`inline-flex items-center justify-center rounded-md font-medium
          transition-all duration-150 cursor-pointer whitespace-nowrap
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-0
          active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none disabled:active:scale-100
          ${variants[variant]} ${sizes[size]} ${className}`}
        {...props}
      >
        {loading && (
          <svg className="animate-spin h-3.5 w-3.5 shrink-0" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        )}
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'
export default Button
