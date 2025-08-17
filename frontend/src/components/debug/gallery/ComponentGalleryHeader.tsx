'use client'

import { Eye, Code, ChevronDown } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
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
      <div className="p-4">
        <div className="text-sm text-muted-foreground">
          No Component Selected
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Top section - Component name and variant selector */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-semibold">{component.name}</h1>
          <Badge variant="outline" className="text-xs">
            {component.category}
          </Badge>
        </div>
        
        {/* Variant Dropdown */}
        {component.variants.length > 1 && onVariantChange && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">variants:</span>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="gap-2">
                  {variant.name}
                  <ChevronDown className="h-3 w-3" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                {component.variants.map((v) => (
                  <DropdownMenuItem
                    key={v.id}
                    onClick={() => onVariantChange(v.id)}
                    className={variantId === v.id ? "bg-muted" : ""}
                  >
                    <div className="flex flex-col">
                      <span className="font-medium">{v.name}</span>
                      <span className="text-xs text-muted-foreground">{v.description}</span>
                    </div>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}
      </div>

      {/* Middle section - Two-column descriptions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 py-2 border-y border-border">
        <div>
          <h3 className="text-sm font-medium mb-1">Component</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {component.description}
          </p>
        </div>
        <div>
          <h3 className="text-sm font-medium mb-1">Variant</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {variant.description}
          </p>
        </div>
      </div>

      {/* Bottom section - View mode toggle */}
      {onViewModeChange && (
        <div className="flex gap-1">
          <Button
            variant={viewMode === 'preview' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => onViewModeChange('preview')}
            className="gap-2"
          >
            <Eye className="h-4 w-4" />
            Preview
          </Button>
          <Button
            variant={viewMode === 'code' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => onViewModeChange('code')}
            className="gap-2"
          >
            <Code className="h-4 w-4" />
            Code
          </Button>
        </div>
      )}
    </div>
  )
}