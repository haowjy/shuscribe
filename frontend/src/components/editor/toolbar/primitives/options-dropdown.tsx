'use client'

import React from 'react'
import { DropdownMenuItem } from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'
import { DropdownToolbarButton } from './dropdown-toolbar-button'

export interface DropdownOption {
  id: string
  label: string
  icon: React.ComponentType<{ size?: number }>
  onSelect: () => void
  className?: string
}

export interface OptionsDropdownProps {
  trigger: React.ReactNode
  tooltip?: string
  open?: boolean
  onOpenChange?: (open: boolean) => void
  className?: string
  contentClassName?: string
  onCloseAutoFocus?: (event: Event) => void
  options: DropdownOption[]
}

export const OptionsDropdown = React.memo<OptionsDropdownProps>(({
  trigger,
  tooltip,
  open,
  onOpenChange,
  className,
  contentClassName,
  onCloseAutoFocus,
  options,
}) => {
  return (
    <DropdownToolbarButton
      trigger={trigger}
      tooltip={tooltip}
      open={open}
      onOpenChange={onOpenChange}
      className={className}
      contentClassName={contentClassName}
      onCloseAutoFocus={onCloseAutoFocus}
    >
      {options.map((option) => {
        const OptionIcon = option.icon
        return (
          <DropdownMenuItem
            key={option.id}
            onSelect={option.onSelect}
            className={cn("flex items-center gap-2", option.className)}
          >
            <OptionIcon size={16} />
            <span>{option.label}</span>
          </DropdownMenuItem>
        )
      })}
    </DropdownToolbarButton>
  )
})

OptionsDropdown.displayName = 'OptionsDropdown'
