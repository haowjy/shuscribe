'use client'

import { ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { 
  Tooltip, 
  TooltipContent, 
  TooltipTrigger 
} from '@/components/ui/tooltip'
import { PanelLeftOpen, PanelRightOpen } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SidebarControl {
  isOpen: boolean
  onToggle: () => void
  label?: string
  shortcut?: string
}

interface ContentAreaContainerProps {
  // Content
  headerContent?: ReactNode
  children: ReactNode // main content
  footerContent?: ReactNode
  
  // Sidebar controls
  leftSidebar?: SidebarControl
  rightSidebar?: SidebarControl
  
  // Layout control
  headerClassName?: string
  // If true (default), center header content; when false, left-align
  centerHeader?: boolean
  
  className?: string
}

export function ContentAreaContainer({
  headerContent,
  children,
  footerContent,
  leftSidebar,
  rightSidebar,
  headerClassName,
  centerHeader = true,
  className
}: ContentAreaContainerProps) {
  return (
    <div className={cn("flex flex-col h-full min-w-0", className)}>
      {/* Header with toggle buttons */}
      <div className="flex items-center justify-between h-10 min-h-10 min-w-0">
        {/* Left sidebar toggle - only show if sidebar is closed */}
        <div className="flex items-center h-8 border-b border-border">
          {leftSidebar && !leftSidebar.isOpen && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 m-1 rounded-md"
                  onClick={leftSidebar.onToggle}
                >
                  <PanelLeftOpen className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="bottom">
                <p>
                  {leftSidebar.label || 'Open Sidebar'}
                  {leftSidebar.shortcut && ` ${leftSidebar.shortcut}`}
                </p>
              </TooltipContent>
            </Tooltip>
          )}
        </div>

        {/* Header content - takes remaining space */}
        <div className={cn(
          "flex-1 flex items-center min-w-0",
          centerHeader ? "justify-center" : "justify-start",
          headerClassName
        )}>
          {headerContent}
        </div>

        {/* Right sidebar toggle - only show if sidebar is closed */}
        <div className="flex items-center h-8 border-b border-border">
          {rightSidebar && !rightSidebar.isOpen && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 m-1 rounded-md"
                  onClick={rightSidebar.onToggle}
                >
                  <PanelRightOpen className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="bottom">
                <p>
                  {rightSidebar.label || 'Open Sidebar'}
                  {rightSidebar.shortcut && ` ${rightSidebar.shortcut}`}
                </p>
              </TooltipContent>
            </Tooltip>
          )}
        </div>
      </div>

      {/* Main content area */}
      <div className="flex-1 min-h-0 min-w-0">
        {children}
      </div>

      {/* Optional footer content */}
      {footerContent && (
        <div className="flex items-center justify-between border-t border-border bg-background">
          <div className="flex-1 flex items-center min-w-0 px-3 py-2">
            {footerContent}
          </div>
        </div>
      )}
    </div>
  )
}