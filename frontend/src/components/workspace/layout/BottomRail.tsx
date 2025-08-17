'use client'

import React from 'react'
import { Bot, Link, Tags, ChevronUp } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { 
  Tooltip, 
  TooltipContent, 
  TooltipProvider, 
  TooltipTrigger 
} from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'

type BottomRailTab = 'ai-tools' | 'links' | 'tags'

interface RailItem {
  id: BottomRailTab
  label: string
  icon: React.ComponentType<{ className?: string }>
  shortcut?: string
}

interface BottomRailProps {
  activeTab?: BottomRailTab
  onTabChange: (tab: BottomRailTab) => void
  onToggle: () => void
  className?: string
}

const railItems: RailItem[] = [
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

export function BottomRail({ 
  activeTab = 'ai-tools', 
  onTabChange, 
  onToggle, 
  className 
}: BottomRailProps) {
  const handleTabClick = (tabId: BottomRailTab) => {
    if (activeTab === tabId) {
      // If clicking the active tab, toggle the panel
      onToggle()
    } else {
      // Switch to the new tab and ensure panel is open
      onTabChange(tabId)
    }
  }

  return (
    <TooltipProvider delayDuration={300}>
      <div className={cn(
        "flex items-center bg-background border-t border-border h-12 px-2",
        className
      )}>
        {/* Rail Tab Items */}
        <div className="flex items-center gap-1">
          {railItems.map((item) => (
            <Tooltip key={item.id}>
              <TooltipTrigger asChild>
                <Button
                  variant={activeTab === item.id ? 'secondary' : 'ghost'}
                  size="icon"
                  className={cn(
                    "h-8 w-8 flex-shrink-0",
                    activeTab === item.id && "bg-muted shadow-none"
                  )}
                  onClick={() => handleTabClick(item.id)}
                  aria-label={item.label}
                >
                  <item.icon className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="top">
                <p>
                  {item.label}
                  {item.shortcut && ` ${item.shortcut}`}
                </p>
              </TooltipContent>
            </Tooltip>
          ))}
        </div>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Toggle Button */}
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={onToggle}
              aria-label="Toggle Panel"
            >
              <ChevronUp className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="top">
            <p>Open Panel ⌘J</p>
          </TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  )
}

// Re-export types for convenience
export type { BottomRailTab }