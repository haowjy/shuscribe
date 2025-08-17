'use client'

import { PanelRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { 
  Tooltip, 
  TooltipContent, 
  TooltipTrigger 
} from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'

interface SidebarToggleButtonProps {
  onToggle: () => void
  isCollapsed: boolean
}

export function SidebarToggleButton({ onToggle, isCollapsed }: SidebarToggleButtonProps) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className={cn(
            "h-7 w-7 flex-shrink-0 ml-1 border-l border-border/50",
            !isCollapsed && "bg-muted"
          )}
        >
          <PanelRight className="h-3 w-3" />
        </Button>
      </TooltipTrigger>
      <TooltipContent side="bottom">
        <p>{isCollapsed ? 'Show' : 'Hide'} AI Chat ⌘\</p>
      </TooltipContent>
    </Tooltip>
  )
}