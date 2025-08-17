'use client'

import { useState, useRef } from 'react'
import { Palette } from 'lucide-react'
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from '@/components/ui/resizable'
import { ComponentGallerySidebar } from './gallery/ComponentGallerySidebar'
import { ComponentGalleryHeader } from './gallery/ComponentGalleryHeader'
import { ComponentPreview } from './gallery/ComponentPreview'
import { Button } from '@/components/ui/button'
import { PanelLeftOpen } from 'lucide-react'
import { getAllComponents } from './gallery/galleryConfig'

interface ComponentGalleryProps {
  onSuccess?: (message: string) => void
  onError?: (message: string) => void
}

export function ComponentGallery({ }: ComponentGalleryProps) {
  const [isEnabled] = useState(() => {
    return process.env.NODE_ENV === 'development' || 
           process.env.NEXT_PUBLIC_ENABLE_COMPONENT_GALLERY === 'true'
  })

  // Gallery state
  const [selectedComponentId, setSelectedComponentId] = useState<string>(() => {
    const allComponents = getAllComponents()
    return allComponents.length > 0 ? allComponents[0].id : ''
  })
  
  const [selectedVariantId, setSelectedVariantId] = useState<string>(() => {
    const allComponents = getAllComponents()
    const firstComponent = allComponents.length > 0 ? allComponents[0] : null
    return firstComponent ? firstComponent.defaultVariantId : ''
  })

  const [viewMode, setViewMode] = useState<'preview' | 'code'>('preview')
  
  // Panel state management (workspace style)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const sidebarPanelRef = useRef<any>(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  if (!isEnabled) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Palette className="h-8 w-8 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">Component Gallery</h3>
          <p className="text-sm text-muted-foreground">
            Component gallery is only available in development mode or when explicitly enabled.
          </p>
        </div>
      </div>
    )
  }

  const handleComponentSelect = (componentId: string) => {
    setSelectedComponentId(componentId)
    // Reset to default variant when selecting a new component
    const allComponents = getAllComponents()
    const component = allComponents.find(c => c.id === componentId)
    if (component) {
      setSelectedVariantId(component.defaultVariantId)
    }
  }

  const handleVariantChange = (variantId: string) => {
    setSelectedVariantId(variantId)
  }

  const handleViewModeChange = (mode: 'preview' | 'code') => {
    setViewMode(mode)
  }

  // Workspace-style panel handlers
  const handleSidebarCollapse = () => {
    setSidebarCollapsed(true)
  }

  const handleSidebarExpand = () => {
    setSidebarCollapsed(false)
  }

  const handleSidebarToggle = () => {
    if (sidebarPanelRef.current) {
      if (sidebarCollapsed) {
        sidebarPanelRef.current.expand()
      } else {
        sidebarPanelRef.current.collapse()
      }
    }
  }

  return (
    <div className="h-full bg-background flex overflow-hidden min-w-0">
      <ResizablePanelGroup direction="horizontal" className="h-full min-w-0">
        {/* Sidebar Panel */}
        <ResizablePanel
          ref={sidebarPanelRef}
          defaultSize={25}
          minSize={20}
          maxSize={40}
          collapsible={true}
          collapsedSize={0}
          onCollapse={handleSidebarCollapse}
          onExpand={handleSidebarExpand}
          className="min-w-0"
        >
          <ComponentGallerySidebar
            selectedComponentId={selectedComponentId}
            onComponentSelect={handleComponentSelect}
            onHide={handleSidebarToggle}
          />
        </ResizablePanel>

        <ResizableHandle />

        {/* Main Content Panel */}
        <ResizablePanel defaultSize={75} className="min-w-0">
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="border-b border-border bg-background">
              <div className="p-4">
                {/* Sidebar toggle - only show if sidebar is collapsed */}
                {sidebarCollapsed && (
                  <div className="mb-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="gap-2"
                      onClick={handleSidebarToggle}
                      aria-label="Show component browser"
                    >
                      <PanelLeftOpen className="h-4 w-4" />
                      Show Component Browser
                    </Button>
                  </div>
                )}
                
                {/* Component header content */}
                <ComponentGalleryHeader
                  componentId={selectedComponentId}
                  variantId={selectedVariantId}
                  viewMode={viewMode}
                  onVariantChange={handleVariantChange}
                  onViewModeChange={handleViewModeChange}
                />
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 min-h-0">
              <ComponentPreview
                componentId={selectedComponentId}
                variantId={selectedVariantId}
                viewMode={viewMode}
              />
            </div>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  )
}