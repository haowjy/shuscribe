'use client'

import { Button } from '@/components/ui/button'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { ChevronsLeft, ChevronsRight } from 'lucide-react'
import { cn } from '@/lib/utils'

interface PanelCloseButtonProps {
  position: 'left' | 'right'
  onClose: () => void
  label?: string
  className?: string
}

const positionStyles = {
  left: {
    container: 'absolute right-0 top-1/2 -translate-y-1/2 z-30',
    button: 'h-12 px-1 rounded-l-md rounded-r-none bg-background/95 backdrop-blur-sm border border-r-0 border-border',
    tooltipSide: 'left' as const,
    Icon: ChevronsLeft
  },
  right: {
    container: 'absolute left-0 top-1/2 -translate-y-1/2 z-30',
    button: 'h-12 px-1 rounded-r-md rounded-l-none bg-background/95 backdrop-blur-sm border border-l-0 border-border',
    tooltipSide: 'right' as const,
    Icon: ChevronsRight
  }
}

export function PanelCloseButton({
  position,
  onClose,
  label = 'Close Sidebar',
  className
}: PanelCloseButtonProps) {
  const styles = positionStyles[position]
  const Icon = styles.Icon

  return (
    <div className={cn(styles.container, className)}>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className={cn(styles.button, 'text-muted-foreground hover:text-foreground')}
            onClick={onClose}
            aria-label={label}
          >
            <Icon className="h-4 w-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent side={styles.tooltipSide}>
          <p>{label}</p>
        </TooltipContent>
      </Tooltip>
    </div>
  )
}


