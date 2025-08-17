'use client'

import { useState } from 'react'
import { ChevronDown, ChevronRight, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { componentCategories, ComponentCategory } from './galleryConfig'
import { cn } from '@/lib/utils'

interface ComponentGallerySidebarProps {
  selectedComponentId?: string
  onComponentSelect: (componentId: string) => void
  onHide?: () => void
}

interface CategorySectionProps {
  category: ComponentCategory
  selectedComponentId?: string
  onComponentSelect: (componentId: string) => void
  isExpanded: boolean
  onToggleExpanded: () => void
}

function CategorySection({ 
  category, 
  selectedComponentId, 
  onComponentSelect, 
  isExpanded, 
  onToggleExpanded 
}: CategorySectionProps) {
  return (
    <div className="space-y-1">
      {/* Category Header */}
      <Button
        variant="ghost"
        size="sm"
        className="w-full justify-start gap-2 h-8 px-2 text-xs font-medium text-muted-foreground hover:text-foreground"
        onClick={onToggleExpanded}
      >
        {isExpanded ? (
          <ChevronDown className="h-3 w-3" />
        ) : (
          <ChevronRight className="h-3 w-3" />
        )}
        <span className="truncate">{category.name}</span>
        <span className="ml-auto text-xs opacity-60">
          {category.components.length}
        </span>
      </Button>

      {/* Category Components */}
      {isExpanded && (
        <div className="ml-2 space-y-0.5">
          {category.components.map((component) => (
            <Button
              key={component.id}
              variant={selectedComponentId === component.id ? 'secondary' : 'ghost'}
              size="sm"
              className={cn(
                "w-full justify-start h-8 px-3 text-xs font-normal",
                selectedComponentId === component.id && "bg-muted/50 shadow-none"
              )}
              onClick={() => onComponentSelect(component.id)}
            >
              <span className="truncate">{component.name}</span>
            </Button>
          ))}
        </div>
      )}
    </div>
  )
}

export function ComponentGallerySidebar({ 
  selectedComponentId, 
  onComponentSelect, 
  onHide 
}: ComponentGallerySidebarProps) {
  // Track which categories are expanded
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(['ui']) // UI category expanded by default
  )

  const toggleCategoryExpanded = (categoryId: string) => {
    const newExpanded = new Set(expandedCategories)
    if (newExpanded.has(categoryId)) {
      newExpanded.delete(categoryId)
    } else {
      newExpanded.add(categoryId)
    }
    setExpandedCategories(newExpanded)
  }

  return (
    <div className="h-full w-full flex flex-col bg-background">
      {/* Minimal header */}
      <div className="flex items-center justify-between p-2 border-b border-border">
        <div className="text-sm font-medium text-foreground">Component Gallery</div>
        {onHide && (
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 rounded-md"
            onClick={onHide}
            aria-label="Hide sidebar"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Full-height scrollable content */}
      <div className="flex-1 relative">
        <div className="h-full overflow-y-auto scroll-smooth">
          <div className="p-3 space-y-4">
            {/* Gallery Description */}
            <div className="text-xs text-muted-foreground px-1">
              Browse and interact with all available UI components and their variants.
            </div>

            {/* Component Categories */}
            <div className="space-y-3">
              {componentCategories.map((category) => (
                <CategorySection
                  key={category.id}
                  category={category}
                  selectedComponentId={selectedComponentId}
                  onComponentSelect={onComponentSelect}
                  isExpanded={expandedCategories.has(category.id)}
                  onToggleExpanded={() => toggleCategoryExpanded(category.id)}
                />
              ))}
            </div>

            {/* Development Notice */}
            <div className="mt-6 p-3 bg-muted/30 rounded-lg">
              <div className="text-xs font-medium mb-1">Development Mode</div>
              <div className="text-xs text-muted-foreground">
                This gallery is available in development mode to help with component testing and documentation.
              </div>
            </div>
          </div>
        </div>
        
        {/* Scroll fade indicator at bottom */}
        <div className="pointer-events-none absolute bottom-0 left-0 right-0 h-6 bg-gradient-to-t from-background to-transparent" />
      </div>
    </div>
  )
}