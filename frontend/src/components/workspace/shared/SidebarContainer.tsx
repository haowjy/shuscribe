'use client'

import { ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'
import { PanelLeftClose, PanelRightClose, LucideIcon } from 'lucide-react'

// Tab configuration for tabbed sidebars
interface SidebarTab {
  id: string
  label: string
  icon: LucideIcon
}

// Props for the container
interface SidebarContainerProps {
  // Container mode
  mode: 'tabbed' | 'simple'
  
  // Tabbed mode props
  tabs?: SidebarTab[]
  activeTabId?: string
  onTabSelect?: (tabId: string) => void
  
  // Simple mode props  
  title?: string
  titleIcon?: LucideIcon
  
  // Toggle button
  side: 'left' | 'right'
  onToggle?: () => void
  
  // Content
  children: ReactNode
  className?: string
}

export function SidebarContainer({
  mode,
  tabs = [],
  activeTabId,
  onTabSelect,
  title,
  titleIcon: TitleIcon,
  side,
  onToggle,
  children,
  className
}: SidebarContainerProps) {
  return (
    <div className={cn("h-full flex flex-col bg-background border-border", 
      side === 'left' ? "border-r" : "border-l", 
      className
    )}>
      {/* Header with tabs or title */}
      <div className="flex items-center h-10 min-h-10">
        {/* Inner-edge toggle for right sidebar (appears on left side of header) */}
        {side === 'right' && onToggle && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 m-1 rounded-md shrink-0"
                onClick={onToggle}
                aria-label="Hide Sidebar"
              >
                <PanelRightClose className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              <p>Hide Sidebar</p>
            </TooltipContent>
          </Tooltip>
        )}

        {/* Content area - tabs or title */}
        <div className="flex-1 flex items-center min-w-0">
          {mode === 'tabbed' ? (
            // Tabbed mode - show tabs
            tabs.map((tab, index) => (
              <Button
                key={tab.id}
                variant={activeTabId === tab.id ? 'secondary' : 'ghost'}
                size="sm"
                className={cn(
                  "h-7 text-xs rounded-md flex-1 min-w-0 m-1",
                  activeTabId === tab.id && "bg-muted/50 shadow-none"
                )}
                onClick={() => onTabSelect?.(tab.id)}
              >
                <tab.icon className="h-3 w-3 mr-1 shrink-0" />
                <span className="truncate">{tab.label}</span>
              </Button>
            ))
          ) : (
            // Simple mode - show title
            <div className="h-full flex items-center px-3 text-sm font-medium text-foreground">
              {TitleIcon && <TitleIcon className="h-4 w-4 mr-2 shrink-0" />}
              <span className="truncate">{title}</span>
            </div>
          )}
        </div>

        {/* Inner-edge toggle for left sidebar (appears on right side of header) */}
        {side === 'left' && onToggle && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 m-1 rounded-md shrink-0"
                onClick={onToggle}
                aria-label="Hide Sidebar"
              >
                <PanelLeftClose className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              <p>Hide Sidebar</p>
            </TooltipContent>
          </Tooltip>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-h-0 overflow-hidden">
        {children}
      </div>
    </div>
  )
}

// Re-export types for convenience
export type { SidebarTab }