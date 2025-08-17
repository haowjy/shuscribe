'use client'

import { useState, useMemo } from 'react'
import { ExplorerHeader } from './components/ExplorerHeader'
import { FileTreeView } from './components/FileTreeView'
import { useFileTree } from './hooks/useFileTree'
import { filterFileTree, countFilesInTree } from './utils/fileTreeFilter'

export function Explorer() {
  const [searchQuery, setSearchQuery] = useState('')
  const fileTree = useFileTree()
  
  const handleFileSelect = (fileId: string, fileName: string) => {
    // TODO: Open file in editor tab
    console.log('Opening file:', fileId, fileName)
  }

  const handleNewFile = () => {
    // TODO: Implement new file creation
    console.log('New file')
  }

  const handleMoreOptions = () => {
    // TODO: Implement more options menu
    console.log('More options')
  }
  
  // Filter file tree based on search query
  const filteredFileTree = useMemo(() => {
    return filterFileTree(fileTree, searchQuery)
  }, [fileTree, searchQuery])

  const resultsCount = useMemo(() => {
    return countFilesInTree(filteredFileTree)
  }, [filteredFileTree])

  return (
    <div className="h-full flex flex-col">
      <ExplorerHeader 
        onNewFile={handleNewFile}
        onMoreOptions={handleMoreOptions}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      {/* File Tree */}
      <div className="flex-1 min-h-0 overflow-auto p-2">
        <FileTreeView
          nodes={filteredFileTree}
          searchQuery={searchQuery}
          onFileSelect={handleFileSelect}
        />
      </div>
    </div>
  )
}

// Re-export types for convenience
export type { FileNode, FileTreeItemProps } from './types'