'use client'

import React, { useState } from 'react'
import { Bot, Link, Tags, ChevronDown, ChevronUp } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { 
  Tooltip, 
  TooltipContent, 
  TooltipProvider, 
  TooltipTrigger 
} from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'
import { AIToolsPanel } from './tabs/AIToolsPanel'
import { LinksPanel } from './tabs/LinksPanel'
import { TagsPanel } from './tabs/TagsPanel'
import { BottomPanelTab } from './components/BottomPanelTab'
import type { BottomPanelProps, BottomPanelTab as BottomPanelTabType, TabItem } from './types'

const tabs: TabItem[] = [
  {
    id: 'ai-tools',
    label: 'AI Tools',
    icon: Bot
  },
  {
    id: 'links',
    label: 'Links',
    icon: Link
  },
  {
    id: 'tags',
    label: 'Tags',
    icon: Tags
  }
]

export function BottomPanel({ 
  isCollapsed, 
  onToggle, 
  activeTab,
  onTabChange,
  className 
}: BottomPanelProps) {
  // Internal active tab state (uncontrolled mode)
  const [internalActiveTab, setInternalActiveTab] = useState<BottomPanelTabType>('ai-tools')

  const currentActiveTab: BottomPanelTabType = activeTab ?? internalActiveTab

  // Handle tab clicks - expand panel if collapsed, then switch tab
  const handleTabClick = (tabId: BottomPanelTabType) => {
    if (isCollapsed) {
      onToggle() // Expand the panel
    }
    if (onTabChange) {
      onTabChange(tabId)
    } else {
      setInternalActiveTab(tabId)
    }
  }

  const renderTabContent = () => {
    switch (currentActiveTab) {
      case 'ai-tools':
        return <AIToolsPanel />
      case 'links':
        return <LinksPanel />
      case 'tags':
        return <TagsPanel />
      default:
        return <AIToolsPanel />
    }
  }

  return (
    <TooltipProvider delayDuration={300}>
      <div className={cn("bg-background border-t border-border", className)}>
        {/* Unified Tab Bar - works for both collapsed and expanded states */}
        <div className={cn(
          "flex items-center justify-between px-4 py-2",
          isCollapsed ? "h-12" : "h-10 border-b border-border px-2"
        )}>
          <div className={cn(
            "flex items-center",
            isCollapsed ? "gap-2" : "gap-0"
          )}>
            {tabs.map((tab) => (
              <BottomPanelTab
                key={tab.id}
                tab={tab}
                isActive={currentActiveTab === tab.id}
                isCollapsed={isCollapsed}
                onTabClick={handleTabClick}
              />
            ))}
          </div>
          
          {/* Toggle button - show appropriate icon based on state */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={onToggle}
              >
                {isCollapsed ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="top">
              <p>{isCollapsed ? 'Expand' : 'Collapse'} Panel ⌘J</p>
            </TooltipContent>
          </Tooltip>
        </div>

        {/* Tab Content - only show when expanded */}
        {!isCollapsed && (
          <div className="h-full overflow-y-auto">
            {renderTabContent()}
          </div>
        )}
      </div>
    </TooltipProvider>
  )
}

// Re-export types for convenience
export type { BottomPanelTab, BottomPanelProps } from './types'