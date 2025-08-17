'use client'

import { Button } from '@/components/ui/button'
import { 
  Tooltip, 
  TooltipContent, 
  TooltipTrigger 
} from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'

interface PanelToggleButtonProps {
  icon: React.ComponentType<{ className?: string }>
  position: 'left' | 'right' | 'bottom'
  isCollapsed: boolean
  onToggle: () => void
  label: string
  shortcut?: string
  className?: string
}

const positionStyles = {
  left: {
    button: "h-12 px-1 rounded-r-md rounded-l-none bg-background/95 backdrop-blur-sm border border-l-0 border-border",
    container: "absolute left-0 top-1/2 -translate-y-1/2 z-20",
    tooltipSide: "right" as const
  },
  right: {
    button: "h-12 px-1 rounded-l-md rounded-r-none bg-background/95 backdrop-blur-sm border border-r-0 border-border",
    container: "absolute right-0 top-1/2 -translate-y-1/2 z-20",
    tooltipSide: "left" as const
  },
  bottom: {
    button: "w-12 px-1 rounded-t-md rounded-b-none bg-background/95 backdrop-blur-sm border border-b-0 border-border",
    container: "absolute bottom-0 left-1/2 -translate-x-1/2 z-20",
    tooltipSide: "top" as const
  }
}

export function PanelToggleButton({
  icon: Icon,
  position,
  isCollapsed,
  onToggle,
  label,
  shortcut,
  className
}: PanelToggleButtonProps) {
  if (!isCollapsed) return null

  const styles = positionStyles[position]

  return (
    <div className={cn(styles.container, className)}>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className={cn(
              styles.button,
              "text-muted-foreground hover:text-foreground"
            )}
            onClick={onToggle}
            aria-label={label}
          >
            <Icon className="h-4 w-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent side={styles.tooltipSide}>
          <p>
            {label}
            {shortcut && ` ${shortcut}`}
          </p>
        </TooltipContent>
      </Tooltip>
    </div>
  )
}