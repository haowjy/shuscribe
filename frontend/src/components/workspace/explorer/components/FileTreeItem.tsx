'use client'

import { useState } from 'react'
import { 
  FolderOpen, 
  Folder, 
  FileText, 
  ChevronRight, 
  ChevronDown
} from 'lucide-react'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { highlightMatch } from '../utils/highlightMatch'
import type { FileTreeItemProps } from '../types'

export function FileTreeItem({ node, level, onFileSelect, searchQuery = '' }: FileTreeItemProps) {
  const [isOpen, setIsOpen] = useState(level === 0) // Root folders open by default

  const handleFileClick = () => {
    if (node.type === 'file') {
      onFileSelect(node.id, node.name)
    }
  }

  if (node.type === 'file') {
    return (
      <div
        className={cn(
          "flex items-center gap-2 py-1 px-2 text-sm rounded-sm hover:bg-accent cursor-pointer group",
          "transition-colors"
        )}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={handleFileClick}
      >
        <FileText className="h-4 w-4 text-primary flex-shrink-0" />
        <span className="flex-1 truncate">
          {highlightMatch(node.name, searchQuery)}
        </span>
        {node.hasUnsavedChanges && (
          <div className="w-1.5 h-1.5 bg-warning rounded-full flex-shrink-0" />
        )}
        {node.tags && node.tags.length > 0 && (
          <div className="flex gap-1">
            {node.tags.slice(0, 2).map(tag => (
              <Badge key={tag} variant="secondary" className="text-xs px-1 py-0 h-4">
                {tag}
              </Badge>
            ))}
            {node.tags.length > 2 && (
              <Badge variant="secondary" className="text-xs px-1 py-0 h-4">
                +{node.tags.length - 2}
              </Badge>
            )}
          </div>
        )}
      </div>
    )
  }

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <CollapsibleTrigger asChild>
        <div
          className={cn(
            "flex items-center gap-2 py-1 px-2 text-sm rounded-sm hover:bg-accent cursor-pointer group",
            "transition-colors"
          )}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
        >
          <div className="flex items-center gap-1">
            {isOpen ? (
              <ChevronDown className="h-3 w-3 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-3 w-3 text-muted-foreground" />
            )}
            {isOpen ? (
              <FolderOpen className="h-4 w-4 text-primary flex-shrink-0" />
            ) : (
              <Folder className="h-4 w-4 text-primary flex-shrink-0" />
            )}
          </div>
          <span className="flex-1 truncate font-medium">
            {highlightMatch(node.name, searchQuery)}
          </span>
        </div>
      </CollapsibleTrigger>
      <CollapsibleContent>
        {node.children?.map((child) => (
          <FileTreeItem
            key={child.id}
            node={child}
            level={level + 1}
            onFileSelect={onFileSelect}
            searchQuery={searchQuery}
          />
        ))}
      </CollapsibleContent>
    </Collapsible>
  )
}