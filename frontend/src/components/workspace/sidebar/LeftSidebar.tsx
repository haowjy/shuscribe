'use client'

import { FolderOpen } from 'lucide-react'
import { SidebarContainer } from '@/components/workspace/shared/SidebarContainer'
import { Explorer } from '@/components/workspace/explorer/Explorer'

export function LeftSidebar({ onHide }: { onHide?: () => void }) {
  return (
    <SidebarContainer
      mode="simple"
      title="My Universe"
      titleIcon={FolderOpen}
      side="left"
      onToggle={onHide}
    >
      <Explorer />
    </SidebarContainer>
  )
}