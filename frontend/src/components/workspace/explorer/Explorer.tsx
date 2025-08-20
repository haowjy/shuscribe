'use client'

import { useState, useMemo } from 'react'
import { ExplorerHeader } from './components/ExplorerHeader'
import { FileTreeView } from './components/FileTreeView'
import { useFileTree } from './hooks/useFileTree'
import { filterFileTree, countFilesInTree } from './utils/fileTreeFilter'
import { useProjectState } from '@/components/providers/ProjectStateProvider'

interface ExplorerProps {
  projectId: string
}

export function Explorer({ projectId }: ExplorerProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const { data: fileTree } = useFileTree(projectId)
  const { openFileInEditor } = useProjectState()

  const handleFileSelect = (fileId: string, fileName: string, documentId?: string) => {
    openFileInEditor(projectId, fileId, fileName, documentId)
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

  // const resultsCount = useMemo(() => {
  //   return countFilesInTree(filteredFileTree)
  // }, [filteredFileTree])

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