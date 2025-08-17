'use client'

import React from 'react'
import { Button } from "@/components/editor-primitives/button"

interface DynamicFormatButtonProps {
  isActive: boolean
  command: () => void
  icon: React.ComponentType<{ size?: number }>
  tooltip: string
  shortcutKeys?: string
}

export function DynamicFormatButton({
  isActive,
  command,
  icon: Icon,
  tooltip,
  shortcutKeys,
}: DynamicFormatButtonProps) {
  if (!isActive) {
    return null
  }

  return (
    <Button
      onClick={command}
      data-active-state="on"
      tooltip={tooltip}
      shortcutKeys={shortcutKeys}
      className="transition-colors"
    >
      <Icon size={16} />
    </Button>
  )
}