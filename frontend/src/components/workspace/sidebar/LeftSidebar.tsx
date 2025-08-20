'use client'

import { FolderOpen } from 'lucide-react'
import { SidebarContainer } from '@/components/workspace/shared/SidebarContainer'
import { Explorer } from '@/components/workspace/explorer/Explorer'

interface LeftSidebarProps {
  projectId: string
  onHide?: () => void
}

export function LeftSidebar({ projectId, onHide }: LeftSidebarProps) {
  return (
    <SidebarContainer
      mode="simple"
      title="My Universe"
      titleIcon={FolderOpen}
      side="left"
      onToggle={onHide}
    >
      <Explorer projectId={projectId} />
    </SidebarContainer>
  )
}