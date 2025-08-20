'use client'

import { LeftSidebar } from '@/components/workspace/sidebar/LeftSidebar'
import type { RailMode } from '@/components/workspace/layout/types'

interface ContextualDrawerProps {
  mode: RailMode
  projectId: string
  onClose: () => void
}

export function ContextualDrawer({ mode, projectId, onClose }: ContextualDrawerProps) {
  switch (mode) {
    case 'workspace':
      return <LeftSidebar projectId={projectId} onHide={onClose} />
    case 'component-gallery':
    case 'devtools':
    case 'settings':
      // These modes render their own full-page components, so the sidebar is not used
      return null
    default:
      return <LeftSidebar projectId={projectId} onHide={onClose} />
  }
}