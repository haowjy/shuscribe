'use client'

import { Plus, MoreHorizontal, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Tooltip, 
  TooltipContent, 
  TooltipTrigger 
} from '@/components/ui/tooltip'

interface ExplorerHeaderProps {
  onNewFile?: () => void
  onMoreOptions?: () => void
  searchQuery?: string
  onSearchChange?: (query: string) => void
}

export function ExplorerHeader({ onNewFile, onMoreOptions, searchQuery = '', onSearchChange }: ExplorerHeaderProps) {
  return (
    <div className="flex items-center gap-2 p-3 border-b border-border">
      {/* Search Input */}
      <div className="relative flex-1">
        <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 text-muted-foreground h-3 w-3" />
        <Input
          value={searchQuery}
          onChange={(e) => onSearchChange?.(e.target.value)}
          placeholder="Search files..."
          className="h-7 pl-7 text-xs"
          data-search-input
        />
      </div>
      
      {/* Action Buttons */}
      <div className="flex items-center gap-1">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={onNewFile}
            >
              <Plus className="h-3 w-3" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="bottom">
            <p>New File</p>
          </TooltipContent>
        </Tooltip>
        
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={onMoreOptions}
            >
              <MoreHorizontal className="h-3 w-3" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="bottom">
            <p>More Options</p>
          </TooltipContent>
        </Tooltip>
      </div>
    </div>
  )
}