'use client'

import { DocumentEditor } from '@/components/editor/DocumentEditor'
import { TabBar } from '@/components/workspace/shared/TabBar'
import { EmptyEditor } from './components/EmptyEditor'
import { ContentAreaContainer } from '@/components/workspace/shared/ContentAreaContainer'
import { useEditorTabsWithState } from './hooks/useEditorTabsWithState'
import { useDocumentContent } from './hooks/useDocumentContent'
import { useUpdateDocument } from '@/hooks/data'
import { htmlToTipTap, calculateWordCount } from '@/lib/utils/markdownToTipTap'
import { useCallback, useState, useEffect } from 'react'
import type { RailMode } from './types/editor.types'

// Canonical useDebounce hook - debounces values, not callbacks
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

interface EditorPanelProps {
  projectId: string
  railMode?: RailMode
  
  // Sidebar controls
  leftSidebar?: {
    isOpen: boolean
    onToggle: () => void
  }
  rightSidebar?: {
    isOpen: boolean
    onToggle: () => void
  }
}

// No initial tabs - tabs will be opened by file selection from Explorer

export function EditorPanel({ 
  projectId,
  railMode = 'workspace',
  leftSidebar,
  rightSidebar
}: EditorPanelProps) {
  const {
    openTabs,
    activeTabId,
    activeTab,
    handleTabClose,
    handleNewTab,
    handleTabSelect,
    // markTabUnsaved, // TODO: Implement unsaved state tracking when needed
    reorderTabs
  } = useEditorTabsWithState({ 
    projectId,
    initialTabs: [], // Start with no tabs
    initialActiveTabId: undefined 
  })

  // Load document content for active tab
  const { 
    content: documentContent, 
    isLoading: loadingContent,
    title: documentTitle,
    document: currentDocument 
  } = useDocumentContent({
    fileId: activeTabId || null,
    documentId: activeTab?.documentId || null,
    projectId
  })

  // Document update mutation for saving changes
  const updateDocumentMutation = useUpdateDocument(activeTab?.documentId || '')

  // Content state for debounced auto-save (always called at top level)
  const [currentHtmlContent, setCurrentHtmlContent] = useState<string>('')
  const debouncedHtmlContent = useDebounce(currentHtmlContent, 500)

  // Auto-save effect - responds to debounced content changes
  useEffect(() => {
    // Only save real documents (not mock files) when debounced content changes
    const documentId = activeTab?.documentId
    const isRealDocument = !!documentId && !!currentDocument
    
    // Skip saving for various invalid states
    if (!isRealDocument || !debouncedHtmlContent) {
      // Skip saving for mock files or empty content
      return
    }
    
    // Skip saving if content is effectively empty (just HTML structure with no meaningful content)
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = debouncedHtmlContent
    const textContent = tempDiv.textContent || tempDiv.innerText || ''
    const trimmedText = textContent.trim()
    
    if (!trimmedText || trimmedText.length < 3) {
      // Skip saving if there's no meaningful text content (less than 3 characters)
      return
    }

    try {
      // Convert HTML back to ProseMirror JSON for Dexie storage
      const prosemirrorContent = htmlToTipTap(debouncedHtmlContent)
      
      // Silent auto-save to LocalStorage (no UI indicators)
      updateDocumentMutation.mutate({
        content: prosemirrorContent,
        wordCount: calculateWordCount(prosemirrorContent),
        updatedAt: new Date().toISOString()
      })
      
      // TODO: BACKGROUND CLOUD SYNC INTEGRATION
      // When backend APIs are implemented, this is where background sync will be added:
      // 
      // 1. BACKGROUND SERVER SYNC:
      //    - Queue document for server sync after local save succeeds
      //    - Use background queue: POST /api/documents/{id} with conflict detection
      //    - Compare server document.version with local version
      //    - Handle version conflicts with three-way merge or user prompt
      // 
      // 2. OPERATIONAL TRANSFORMS FOR COLLABORATION:
      //    - Implement real-time collaborative editing
      //    - Use WebSocket connection for live document updates
      //    - Apply operational transforms to resolve concurrent edits
      //    - Show live cursors and user presence indicators
      // 
      // 3. SYNC STATUS UI (FUTURE):
      //    - Add sync status indicator only for cloud sync, not local saves
      //    - Show sync conflicts that require user resolution
      //    - Display "Syncing...", "Sync failed", "Conflict detected" states
      //    - Local saves remain completely invisible (offline-first philosophy)
      // 
      // 4. ADVANCED CONFLICT RESOLUTION:
      //    - Detect concurrent edits using document versions
      //    - Implement conflict-free replicated data types (CRDTs)
      //    - Provide merge UI for complex conflicts
      //    - Auto-resolve simple conflicts (non-overlapping changes)
      // 
      // 5. PERFORMANCE OPTIMIZATIONS:
      //    - Delta compression for large documents
      //    - Batch multiple rapid changes into single sync operation
      //    - Implement exponential backoff for sync retries
      //    - Cache frequently accessed documents for offline editing
      
    } catch (error) {
      // Log silently - LocalStorage failures are rare and shouldn't interrupt editing
      console.error('Failed to save document to LocalStorage:', error)
      // TODO: FUTURE CLOUD SYNC ERROR HANDLING
      // - Show UI notification only for cloud sync failures
      // - Provide retry mechanism for failed server syncs
      // - Queue failed saves for retry when connection restored
    }
  }, [debouncedHtmlContent, activeTab?.documentId, currentDocument, updateDocumentMutation])

  // Simple callback to update content state (no debouncing here)
  const handleContentUpdate = useCallback((htmlContent: string) => {
    setCurrentHtmlContent(htmlContent)
  }, [])


  // Header content - editor tabs
  const headerContent = (
    <TabBar
      mode="advanced"
      advancedTabs={openTabs}
      activeTabId={activeTabId}
      onTabSelect={handleTabSelect}
      onTabClose={handleTabClose}
      onNewTab={handleNewTab}
      onReorderTabs={reorderTabs}
    />
  )

  // Main editor content
  const editorContent = activeTab ? (
    <DocumentEditor
      content={loadingContent ? 'Loading...' : (documentContent || '')}
      placeholder={`Start writing in ${documentTitle || activeTab.name}...`}
      container="flex flex-col h-full"
      border={false}
      rounded={false}
      railMode={railMode}
      onUpdate={handleContentUpdate}
    />
  ) : (
    <EmptyEditor />
  )

  return (
    <ContentAreaContainer
      headerContent={headerContent}
      centerHeader={false}
      leftSidebar={leftSidebar ? {
        ...leftSidebar,
        label: 'Open Sidebar',
        shortcut: '⌘B'
      } : undefined}
      rightSidebar={rightSidebar ? {
        ...rightSidebar,
        label: 'AI Chat',
        shortcut: '⌘\\'
      } : undefined}
    >
      {editorContent}
    </ContentAreaContainer>
  )
}