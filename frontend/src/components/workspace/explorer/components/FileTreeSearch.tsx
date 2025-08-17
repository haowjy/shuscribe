'use client'

import { Search, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

interface FileTreeSearchProps {
  searchQuery: string
  onSearchChange: (query: string) => void
  resultsCount?: number
}

export function FileTreeSearch({ 
  searchQuery, 
  onSearchChange,
  resultsCount 
}: FileTreeSearchProps) {
  const clearSearch = () => {
    onSearchChange('')
  }

  return (
    <div className="p-2 border-b border-border">
      <div className="relative">
        <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 text-muted-foreground h-3 w-3" />
        <Input
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search files..."
          className="h-7 pl-7 pr-7 text-xs"
          data-search-input
        />
        {searchQuery && (
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-1 top-1/2 transform -translate-y-1/2 h-5 w-5 p-0 hover:bg-muted"
            onClick={clearSearch}
          >
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>
      {searchQuery && (
        <div className="text-xs text-muted-foreground mt-1">
          {resultsCount === 0 
            ? 'No files found' 
            : `${resultsCount} files found`
          }
        </div>
      )}
    </div>
  )
}