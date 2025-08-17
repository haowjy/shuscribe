'use client'

import { X } from 'lucide-react'
import { 
  Tooltip, 
  TooltipContent, 
  TooltipTrigger 
} from '@/components/ui/tooltip'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { cn } from '@/lib/utils'
import { formatTabLabel } from '../utils/labels'
import type { Tab } from '../types'

interface TabItemProps {
  tab: Tab
  isActive: boolean
  onSelect: (tabId: string) => void
  onClose: (tabId: string) => void
  showLeftDivider?: boolean
  showLeftEdge?: boolean
  showRightEdge?: boolean
}

export function TabItem({ tab, isActive, onSelect, onClose, showLeftDivider = false, showLeftEdge = false, showRightEdge = false }: TabItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: tab.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  const handleTabClick = (event: React.MouseEvent) => {
    if (event.button === 1) { // Middle click
      event.preventDefault()
      onClose(tab.id)
    } else {
      onSelect(tab.id)
    }
  }

  const handleCloseClick = (event: React.MouseEvent) => {
    event.stopPropagation()
    onClose(tab.id)
  }

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <button
          ref={setNodeRef}
          style={style}
          onClick={handleTabClick}
          onMouseDown={(e) => e.button === 1 && e.preventDefault()} // Prevent middle-click default
          className={cn(
            "relative flex items-center text-xs rounded-t-md transition-colors group whitespace-nowrap shrink-0 h-8 pl-3 pr-2 w-30",
            isActive
              ? "bg-background text-foreground border border-border border-b-0 z-10"
              : "bg-muted/20 text-muted-foreground hover:bg-muted/30 border border-transparent border-b-0",
            isDragging && "opacity-50",
            showLeftDivider && "border-l-0 before:content-[''] before:absolute before:left-0 before:top-1 before:bottom-1 before:w-px before:bg-border",
            showLeftEdge && !isActive && "before:content-[''] before:absolute before:left-0 before:top-1 before:bottom-1 before:w-px before:bg-border",
            showRightEdge && !isActive && "after:content-[''] after:absolute after:right-0 after:top-1 after:bottom-1 after:w-px after:bg-border"
          )}
          {...attributes}
          {...listeners}
        >
          {/* Unsaved dot to the left of label */}
          {/* Unsaved indicator removed: autosave is default */}
          <span className="truncate min-w-0 flex-1">{formatTabLabel(tab.name)}</span>
          {/* Close button on hover/active */}
          <span
            role="button"
            tabIndex={isActive ? 0 : -1}
            className={cn(
              "ml-1 flex items-center justify-center transition-opacity opacity-0 pointer-events-none h-4 w-4",
              isActive && "opacity-100 pointer-events-auto cursor-pointer",
              "group-hover:opacity-100 group-hover:pointer-events-auto cursor-pointer"
            )}
            onClick={handleCloseClick}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleCloseClick(e as any) }}
            aria-label="Close tab"
          >
            <X className="h-3 w-3" />
          </span>
        </button>
      </TooltipTrigger>
      <TooltipContent side="bottom">
        <p>
          {tab.path || tab.name}
          <br />
          <span className="text-xs opacity-80">Middle-click to close</span>
        </p>
      </TooltipContent>
    </Tooltip>
  )
}