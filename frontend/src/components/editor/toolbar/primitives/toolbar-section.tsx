'use client'

import React from 'react'
import { cn } from '@/lib/utils'
import type { ToolbarSectionProps } from '../../types/editor.types'

export const ToolbarSection = React.memo<ToolbarSectionProps>(({ 
  children, 
  className 
}) => {
  return (
    <>
      <div className={cn("flex items-center gap-1", className)}>
        {children}
      </div>
      <ToolbarSeparator />
    </>
  )
})

ToolbarSection.displayName = 'ToolbarSection'

export const ToolbarSeparator = React.memo(() => (
  <div className="w-px h-6 bg-border mx-1" />
))

ToolbarSeparator.displayName = 'ToolbarSeparator'