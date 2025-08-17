'use client'

import { useState } from 'react'
import { Search, Palette } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import { EditorVariantConfig } from './editorVariantConfigs'

interface ComponentVariantSidebarProps {
  variants: EditorVariantConfig[]
  selectedVariantId: string
  onVariantSelect: (variantId: string) => void
}

export function ComponentVariantSidebar({ 
  variants, 
  selectedVariantId, 
  onVariantSelect 
}: ComponentVariantSidebarProps) {
  const [searchQuery, setSearchQuery] = useState('')

  // Filter variants based on search query
  const filteredVariants = variants.filter(variant =>
    variant.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    variant.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="h-full flex flex-col">
      {/* Header with search - matching ExplorerHeader pattern */}
      <div className="flex items-center gap-2 p-3 border-b border-border">
        <div className="relative flex-1">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 text-muted-foreground h-3 w-3" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search variants..."
            className="h-7 pl-7 text-xs"
          />
        </div>
        <div className="flex items-center gap-1">
          <Palette className="h-4 w-4 text-muted-foreground" />
        </div>
      </div>
      
      {/* Variant List - matching FileTreeView pattern */}
      <div className="flex-1 min-h-0 overflow-auto p-2">
        {filteredVariants.length === 0 && searchQuery ? (
          <div className="text-center text-muted-foreground text-xs py-8">
            No variants match &ldquo;{searchQuery}&rdquo;
          </div>
        ) : (
          <div className="space-y-1">
            {filteredVariants.map((variant) => {
              const IconComponent = variant.icon
              const isSelected = selectedVariantId === variant.id
              
              return (
                <div
                  key={variant.id}
                  className={cn(
                    "flex items-center gap-2 py-1 px-2 text-sm rounded-sm hover:bg-accent cursor-pointer group transition-colors",
                    isSelected && "bg-accent"
                  )}
                  onClick={() => onVariantSelect(variant.id)}
                >
                  <IconComponent className="h-4 w-4 text-primary flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">{variant.title}</div>
                    <div className="text-xs text-muted-foreground truncate">
                      {variant.description}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}