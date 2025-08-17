'use client'

import React from 'react'
import { EditorTabs } from '@/components/editor/tabs/EditorTabs'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { PanelLeftClose, PanelRightClose } from 'lucide-react'

// Simple tab for sidebars (Files/Search, Chat/Tools)
interface SimpleTab {
  id: string
  label: string
  icon: React.ComponentType<{ className?: string }>
}

// Advanced tab for editor (with close buttons, unsaved changes)
interface AdvancedTab {
  id: string
  name: string
  hasUnsavedChanges?: boolean
}

interface TabBarProps {
  mode: 'simple' | 'advanced'
  // Simple mode props
  simpleTabs?: SimpleTab[]
  onHideSidebar?: () => void
  hideSide?: 'left' | 'right'
  // Advanced mode props  
  advancedTabs?: AdvancedTab[]
  activeTabId: string
  onTabSelect: (tabId: string) => void
  onTabClose?: (tabId: string) => void
  onNewTab?: () => void
  onReorderTabs?: (fromIndex: number, toIndex: number) => void
  onToggleRightSidebar?: () => void
  isRightSidebarCollapsed?: boolean
  className?: string
}

export function TabBar({
  mode,
  simpleTabs = [],
  advancedTabs = [],
  activeTabId,
  onTabSelect,
  onTabClose,
  onNewTab,
  onReorderTabs,
  onToggleRightSidebar,
  isRightSidebarCollapsed,
  className,
  onHideSidebar,
  hideSide
}: TabBarProps) {
  if (mode === 'simple') {
    return (
      <div className={cn("flex items-stretch h-full min-w-0", className)}>
        {/* Optional left-side hide button */}
        {onHideSidebar && hideSide === 'left' && (
          <Button
            variant="ghost"
            size="sm"
            className="h-full w-10 rounded-none border-r border-border text-muted-foreground hover:text-foreground"
            onClick={onHideSidebar}
            aria-label="Hide Sidebar"
          >
            <PanelLeftClose className="h-4 w-4" />
          </Button>
        )}

        {/* Tabs container */}
        <div className="flex-1 flex items-stretch min-w-0">
          {simpleTabs.map((tab, index) => (
            <Button
              key={tab.id}
              variant={activeTabId === tab.id ? 'secondary' : 'ghost'}
              size="sm"
              className={cn(
                "h-full text-xs rounded-none flex-1",
                index < simpleTabs.length - 1 && "border-r border-border",
                activeTabId === tab.id && "bg-muted/50 shadow-none"
              )}
              onClick={() => onTabSelect(tab.id)}
            >
              <tab.icon className="h-3 w-3 mr-1" />
              {tab.label}
            </Button>
          ))}
        </div>

        {/* Optional right-side hide button */}
        {onHideSidebar && hideSide === 'right' && (
          <Button
            variant="ghost"
            size="sm"
            className="h-full w-10 rounded-none border-l border-border text-muted-foreground hover:text-foreground"
            onClick={onHideSidebar}
            aria-label="Hide Sidebar"
          >
            <PanelRightClose className="h-4 w-4" />
          </Button>
        )}
      </div>
    )
  }

  // Advanced mode for editor tabs - use EditorTabs component
  return (
    <div className={cn("h-full w-full min-w-0 max-w-full overflow-hidden", className)}>
      <EditorTabs
        tabs={advancedTabs.map(tab => ({
          id: tab.id,
          name: tab.name,
          hasUnsavedChanges: tab.hasUnsavedChanges || false
        }))}
        activeTabId={activeTabId}
        onTabSelect={onTabSelect}
        onTabClose={onTabClose || (() => {})}
        onNewTab={onNewTab || (() => {})}
        onReorderTabs={onReorderTabs}
        onToggleRightSidebar={onToggleRightSidebar}
        isRightSidebarCollapsed={isRightSidebarCollapsed}
      />
    </div>
  )
}

// Re-export types for convenience
export type { SimpleTab, AdvancedTab }