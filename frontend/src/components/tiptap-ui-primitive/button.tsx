'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  'data-style'?: 'ghost' | 'primary' | 'secondary'
  'data-active-state'?: 'on' | 'off'
  'data-size'?: 'small' | 'default' | 'large' | 'toolbar'
  'data-appearance'?: string
  'data-disabled'?: boolean
  tooltip?: string
  shortcutKeys?: string
}

const buttonVariants = {
  style: {
    ghost: 'bg-transparent hover:bg-muted border-transparent hover:border-border',
    primary: 'bg-primary text-primary-foreground hover:bg-primary/90 border-primary',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80 border-secondary'
  },
  size: {
    small: 'h-8 w-8 text-xs',
    default: 'h-9 w-9 text-sm',
    large: 'h-10 w-10 text-base',
    toolbar: 'h-8 w-auto text-sm'
  },
  activeState: {
    on: 'bg-primary text-primary-foreground border-primary shadow-sm ring-1 ring-primary/20 mx-0.5',
    off: ''
  }
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    'data-style': dataStyle = 'ghost',
    'data-active-state': dataActiveState = 'off',
    'data-size': dataSize = 'toolbar',
    'data-disabled': dataDisabled = false,
    tooltip,
    shortcutKeys,
    disabled,
    children,
    ...props 
  }, ref) => {
    const isActive = dataActiveState === 'on'
    const isDisabled = disabled || dataDisabled

    return (
      <button
        className={cn(
          'inline-flex items-center justify-center rounded-md border transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:bg-muted/80',
          buttonVariants.size[dataSize],
          isActive 
            ? buttonVariants.activeState.on
            : buttonVariants.style[dataStyle],
          isDisabled && 'opacity-50 cursor-not-allowed',
          className
        )}
        ref={ref}
        disabled={isDisabled}
        title={tooltip ? (shortcutKeys ? `${tooltip} (${shortcutKeys})` : tooltip) : undefined}
        aria-pressed={isActive}
        {...props}
      >
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

export { Button, buttonVariants }