'use client'

import { Button } from '@/components/ui/button'
import { 
  Tooltip, 
  TooltipContent, 
  TooltipTrigger 
} from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'
import type { BottomPanelTab as BottomPanelTabType, TabItem } from '../types'

interface BottomPanelTabProps {
  tab: TabItem
  isActive: boolean
  isCollapsed: boolean
  onTabClick: (tabId: BottomPanelTabType) => void
}

export function BottomPanelTab({ tab, isActive, isCollapsed, onTabClick }: BottomPanelTabProps) {
  const handleClick = () => {
    onTabClick(tab.id)
  }

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant={isActive ? 'secondary' : 'ghost'}
          size="sm"
          className={cn(
            "h-8 px-3 text-xs",
            isActive && "bg-muted/50",
            // In expanded state, add border styling for traditional tab appearance
            !isCollapsed && "rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
          )}
          onClick={handleClick}
          data-state={isActive ? 'active' : 'inactive'}
        >
          <tab.icon className="h-3 w-3 mr-1" />
          {tab.label}
        </Button>
      </TooltipTrigger>
      <TooltipContent side="top">
        <p>
          {tab.label} 
          {isCollapsed ? ' ⌘J' : ''}
        </p>
      </TooltipContent>
    </Tooltip>
  )
}