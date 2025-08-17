'use client'

import { FileTreeItem } from './FileTreeItem'
import type { FileNode } from '../types'

interface FileTreeViewProps {
  nodes: FileNode[]
  searchQuery: string
  onFileSelect: (fileId: string, fileName: string) => void
}

export function FileTreeView({ nodes, searchQuery, onFileSelect }: FileTreeViewProps) {
  if (nodes.length === 0 && searchQuery) {
    return (
      <div className="text-center text-muted-foreground text-xs py-8">
        No files match "{searchQuery}"
      </div>
    )
  }

  return (
    <div className="space-y-1">
      {nodes.map((node) => (
        <FileTreeItem
          key={node.id}
          node={node}
          level={0}
          onFileSelect={onFileSelect}
          searchQuery={searchQuery}
        />
      ))}
    </div>
  )
}