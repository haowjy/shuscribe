'use client'

import React from 'react'

export interface ToolbarGroupsProps {
  children: React.ReactNode
}

export const ToolbarGroups = React.memo<ToolbarGroupsProps>(({ children }) => {
  const items = React.Children.toArray(children).filter(Boolean)
  
  return (
    <>
      {items.map((child, index) => (
        <React.Fragment key={index}>
          <div className="flex items-center gap-1">
            {child}
          </div>
          {index < items.length - 1 && <ToolbarSeparator />}
        </React.Fragment>
      ))}
    </>
  )
})

ToolbarGroups.displayName = 'ToolbarGroups'

export const ToolbarSeparator = React.memo(() => (
  <div className="w-px h-6 bg-border mx-1" />
))

ToolbarSeparator.displayName = 'ToolbarSeparator'
