'use client'

import React from 'react'
import { Button } from '@/components/tiptap-ui-primitive/button'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'
import type { DropdownToolbarButtonProps } from '../../types/editor.types'

export const DropdownToolbarButton = React.memo<DropdownToolbarButtonProps>(({
  trigger,
  children,
  tooltip,
  open,
  onOpenChange,
  align = "start",
  className,
  contentClassName,
  onCloseAutoFocus,
}) => {
  return (
    <DropdownMenu open={open} onOpenChange={onOpenChange}>
      <DropdownMenuTrigger asChild>
        <Button
          tooltip={tooltip}
          className={cn(
            "w-auto px-3 justify-between focus-visible:ring-0 focus-visible:ring-offset-0",
            className
          )}
          data-active-state={open ? "on" : "off"}
        >
          {trigger}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align={align}
        className={cn("p-2", contentClassName)}
        onCloseAutoFocus={onCloseAutoFocus}
      >
        {children}
      </DropdownMenuContent>
    </DropdownMenu>
  )
})

DropdownToolbarButton.displayName = 'DropdownToolbarButton'