'use client'

import { useState } from 'react'
import { ChevronDown, X, Search } from 'lucide-react'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable'
import { restrictToVerticalAxis } from '@dnd-kit/modifiers'
import { CSS } from '@dnd-kit/utilities'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import { formatTabLabel } from '../utils/labels'
import type { Tab } from '../types'

interface AllTabsMenuProps {
  tabs: Tab[]
  activeTabId: string
  onTabSelect: (tabId: string) => void
  onTabClose: (tabId: string) => void
  onReorderTabs?: (fromIndex: number, toIndex: number) => void
}

export function AllTabsMenu({
  tabs,
  activeTabId,
  onTabSelect,
  onTabClose,
  onReorderTabs
}: AllTabsMenuProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  // Filter tabs based on search query
  const filteredTabs = tabs.filter(tab => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    const name = formatTabLabel(tab.name).toLowerCase()
    const path = (tab.path || tab.name).toLowerCase()
    return name.includes(query) || path.includes(query)
  })

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event

    if (active.id !== over?.id && onReorderTabs) {
      const oldIndex = tabs.findIndex(tab => tab.id === active.id)
      const newIndex = tabs.findIndex(tab => tab.id === over?.id)
      
      onReorderTabs(oldIndex, newIndex)
    }
  }

  const handleTabSelect = (tabId: string) => {
    onTabSelect(tabId)
    setIsOpen(false)
    setSearchQuery('')
  }

  const handleTabClose = (tabId: string, event: React.MouseEvent) => {
    event.stopPropagation()
    onTabClose(tabId)
  }

  // No-op: outside clicks should pass through and trigger underlying actions

  // Sortable tab item component for the dropdown
  const SortableTabItem = ({ tab }: { tab: Tab }) => {
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

    return (
      <div
        ref={setNodeRef}
        style={style}
        className={cn(
          "flex items-center gap-2 px-2 py-1.5 text-xs rounded cursor-pointer group",
          "hover:bg-accent/50 transition-colors",
          tab.id === activeTabId && "bg-accent text-accent-foreground",
          isDragging && "opacity-50"
        )}
        onClick={() => handleTabSelect(tab.id)}
        {...attributes}
        {...listeners}
      >
        {/* Tab label */}
        <div className="flex items-center gap-1.5 flex-1 min-w-0">
          <span className="truncate">{formatTabLabel(tab.name)}</span>
        </div>

        {/* Close button */}
        <button
          className="h-4 w-4 p-0 hover:bg-destructive/20 hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 rounded-sm flex items-center justify-center"
          onClick={(e) => handleTabClose(tab.id, e)}
        >
          <X className="h-3 w-3" />
        </button>
      </div>
    )
  }

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <Tooltip>
        <TooltipTrigger asChild>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-t-md border border-transparent border-b-0 data-[state=open]:bg-accent data-[state=open]:text-accent-foreground transition-colors flex items-center justify-center"
            >
              <ChevronDown className="h-3 w-3" />
            </Button>
          </DropdownMenuTrigger>
        </TooltipTrigger>
        <TooltipContent side="bottom">
          <p>All Tabs</p>
        </TooltipContent>
      </Tooltip>

      <DropdownMenuContent
        align="end"
        className="w-64 max-h-80 overflow-hidden p-0 flex flex-col"
        side="bottom"
      >
        {/* Search input */}
        <div className="p-2 border-b border-border">
          <div className="relative">
            <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-3 w-3 text-muted-foreground" />
            <Input
              placeholder="Search tabs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-7 h-7 text-xs"
              autoFocus
            />
          </div>
        </div>

        {/* Tabs list */}
        <div className="flex-1 min-h-0 overflow-y-auto">
          {filteredTabs.length === 0 ? (
            <div className="p-3 text-center text-sm text-muted-foreground">
              {searchQuery ? 'No tabs match your search' : 'No tabs open'}
            </div>
          ) : (
            <DndContext
              id="all-tabs-menu-dnd"
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={handleDragEnd}
              modifiers={[restrictToVerticalAxis]}
            >
              <div className="p-1">
                <SortableContext
                  items={filteredTabs.map(tab => tab.id)}
                  strategy={verticalListSortingStrategy}
                >
                  {filteredTabs.map((tab) => (
                    <SortableTabItem key={tab.id} tab={tab} />
                  ))}
                </SortableContext>
              </div>
            </DndContext>
          )}
        </div>

        {/* Tab count footer */}
        {tabs.length > 0 && (
          <div className="p-2 border-t border-border text-xs text-muted-foreground text-center">
            {filteredTabs.length} of {tabs.length} tabs
            {searchQuery && ` matching "${searchQuery}"`}
          </div>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}