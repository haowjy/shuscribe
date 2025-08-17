'use client'

import { Eye, Code } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { getComponentById, getVariantById } from './galleryConfig'

interface ComponentGalleryHeaderProps {
  componentId: string
  variantId: string
  viewMode: 'preview' | 'code'
  onVariantChange?: (variantId: string) => void
  onViewModeChange?: (mode: 'preview' | 'code') => void
}

export function ComponentGalleryHeader({ 
  componentId, 
  variantId, 
  viewMode,
  onVariantChange,
  onViewModeChange
}: ComponentGalleryHeaderProps) {
  const component = getComponentById(componentId)
  const variant = component ? getVariantById(componentId, variantId) : undefined

  if (!component || !variant) {
    return (
      <div className="flex items-center gap-3">
        <div className="text-sm text-muted-foreground">
          No Component Selected
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-between w-full min-w-0 h-8">
      {/* Left side - Component info */}
      <div className="flex items-center gap-2 min-w-0">
        <div className="min-w-0">
          <h2 className="text-sm font-medium truncate leading-none">{component.name}</h2>
          <p className="text-xs text-muted-foreground truncate leading-none mt-0.5">
            {variant.name} - {variant.description}
          </p>
        </div>
        <Badge variant="outline" className="text-xs shrink-0 h-5">
          {component.category}
        </Badge>
      </div>
      
      {/* Right side - Controls */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Variant Selector */}
        {component.variants.length > 1 && onVariantChange && (
          <div className="flex items-center gap-2 min-w-0">
            <span className="text-xs text-muted-foreground shrink-0">Variant:</span>
            <div className="relative min-w-0">
              <div className="flex gap-1 overflow-x-auto scroll-smooth scrollbar-none pb-1">
                {component.variants.map((v) => (
                  <Button
                    key={v.id}
                    variant={variantId === v.id ? 'default' : 'outline'}
                    size="sm"
                    className="h-6 text-xs px-2 shrink-0"
                    onClick={() => onVariantChange(v.id)}
                  >
                    {v.name}
                  </Button>
                ))}
              </div>
              {/* Subtle scroll fade indicators */}
              <div className="pointer-events-none absolute top-0 left-0 w-3 h-full bg-gradient-to-r from-background to-transparent" />
              <div className="pointer-events-none absolute top-0 right-0 w-3 h-full bg-gradient-to-l from-background to-transparent" />
            </div>
          </div>
        )}
        
        {/* View Mode Toggle */}
        {onViewModeChange && (
          <div className="flex gap-1">
            <Button
              variant={viewMode === 'preview' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => onViewModeChange('preview')}
              className="gap-1 h-6 px-2"
            >
              <Eye className="h-3 w-3" />
              Preview
            </Button>
            <Button
              variant={viewMode === 'code' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => onViewModeChange('code')}
              className="gap-1 h-6 px-2"
            >
              <Code className="h-3 w-3" />
              Code
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}