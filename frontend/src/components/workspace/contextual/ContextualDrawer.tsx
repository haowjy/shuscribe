'use client'

import { LeftSidebar } from '@/components/workspace/sidebar/LeftSidebar'
import type { RailMode } from '@/components/workspace/layout/types'

interface ContextualDrawerProps {
  mode: RailMode
  onClose: () => void
}

export function ContextualDrawer({ mode, onClose }: ContextualDrawerProps) {
  switch (mode) {
    case 'workspace':
      return <LeftSidebar onHide={onClose} />
    case 'component-gallery':
    case 'devtools':
    case 'settings':
      // These modes render their own full-page components, so the sidebar is not used
      return null
    default:
      return <LeftSidebar onHide={onClose} />
  }
}