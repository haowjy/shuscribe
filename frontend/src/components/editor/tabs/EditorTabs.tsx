'use client'

import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import type { WheelEvent } from 'react'
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
  horizontalListSortingStrategy,
} from '@dnd-kit/sortable'
import { restrictToHorizontalAxis } from '@dnd-kit/modifiers'
import { TabItem } from './components/TabItem'
import { NewTabButton } from './components/NewTabButton'
import { cn } from '@/lib/utils'
import { AllTabsMenu } from './components/AllTabsMenu'
// import { SidebarToggleButton } from './components/SidebarToggleButton'
import { useTabScroll } from './hooks/useTabScroll'
import type { EditorTabsProps } from './types'

export function EditorTabs({ 
  tabs, 
  activeTabId, 
  onTabSelect, 
  onTabClose, 
  onNewTab, 
  onReorderTabs
}: EditorTabsProps) {
  const { scrollContainerRef, canScrollLeft, canScrollRight, hasOverflow } = useTabScroll([tabs])
  
  // Prevent vertical scroll when hovering tabs; translate vertical wheel to horizontal scroll
  const handleWheel = (event: WheelEvent<HTMLDivElement>) => {
    const container = scrollContainerRef.current
    if (!container) return
    if (Math.abs(event.deltaY) > Math.abs(event.deltaX)) {
      event.preventDefault()
      container.scrollLeft += event.deltaY
    }
  }
  
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

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event

    if (active.id !== over?.id && onReorderTabs) {
      const oldIndex = tabs.findIndex(tab => tab.id === active.id)
      const newIndex = tabs.findIndex(tab => tab.id === over?.id)
      
      onReorderTabs(oldIndex, newIndex)
    }
  }

  if (tabs.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <Button
          variant="ghost"
          size="sm"
          onClick={onNewTab}
          className="h-7 text-xs text-muted-foreground"
        >
          <Plus className="h-3 w-3 mr-1" />
          New Document
        </Button>
      </div>
    )
  }

  return (
    <div className="flex items-center h-8 relative w-full min-w-0 max-w-full overflow-hidden select-none border-b border-border bg-background/95">
      {/* Fade gradient for left overflow */}
      {canScrollLeft && (
        <div className="absolute left-0 top-0 bottom-0 w-4 bg-gradient-to-r from-background to-transparent z-10 pointer-events-none" />
      )}
      
      {/* Scrollable tabs container */}
      <DndContext
        id="editor-tabs-dnd"
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
        modifiers={[restrictToHorizontalAxis]}
      >
        <div
          ref={scrollContainerRef}
          className="flex items-center gap-0 overflow-x-auto overflow-y-hidden overscroll-y-none touch-pan-x scrollbar-none scroll-smooth flex-1 min-w-0 h-full pl-1 pr-0"
          onWheel={handleWheel}
          style={{ 
            scrollbarWidth: 'none', 
            msOverflowStyle: 'none'
          }}
        >
          <SortableContext
            items={tabs.map(tab => tab.id)}
            strategy={horizontalListSortingStrategy}
          >
            {(() => {
              const activeIndex = tabs.findIndex(t => t.id === activeTabId)
              return tabs.map((tab, index) => (
                <TabItem
                  key={tab.id}
                  tab={tab}
                  isActive={tab.id === activeTabId}
                  onSelect={onTabSelect}
                  onClose={onTabClose}
                  showLeftDivider={index !== 0 && index !== activeIndex && index !== activeIndex + 1}
                  showLeftEdge={index === 0}
                  showRightEdge={index === tabs.length - 1}
                />
              ))
            })()}
          </SortableContext>
        </div>
      </DndContext>

      {/* Fade gradient for right overflow */}
      {canScrollRight && (
        <div className="absolute top-0 bottom-0 w-4 bg-gradient-to-l from-background to-transparent z-0 pointer-events-none right-0" />
      )}

      {/* All Tabs menu - only show when there are tabs */}
      {tabs.length > 0 && (
        <AllTabsMenu
          tabs={tabs}
          activeTabId={activeTabId}
          onTabSelect={onTabSelect}
          onTabClose={onTabClose}
          onReorderTabs={onReorderTabs}
        />
      )}

      {/* New tab button */}
      <NewTabButton onNewTab={onNewTab} />

      {/* Right sidebar toggle removed; handled within sidebar headers */}
    </div>
  )
}

// Re-export types for convenience
export type { Tab, EditorTabsProps } from './types'