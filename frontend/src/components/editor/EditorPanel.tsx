'use client'

import { DocumentEditor } from '@/components/editor/DocumentEditor'
import { TabBar } from '@/components/workspace/shared/TabBar'
import { EmptyEditor } from './components/EmptyEditor'
import { ContentAreaContainer } from '@/components/workspace/shared/ContentAreaContainer'
import { useEditorTabsWithState } from './hooks/useEditorTabsWithState'
import { getContentForTab } from './utils/mockContent'
import type { RailMode } from './types/editor.types'

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

// Initial tabs for testing overflow behavior
const initialTabs = [
  { id: 'doc1', name: 'chapter-01.md', hasUnsavedChanges: true },
  { id: 'doc2', name: 'characters.md', hasUnsavedChanges: false },
  { id: 'doc3', name: 'world-building-notes.md', hasUnsavedChanges: false },
  { id: 'doc4', name: 'plot-outline.md', hasUnsavedChanges: true },
  { id: 'doc5', name: 'research-references.md', hasUnsavedChanges: false },
  { id: 'doc6', name: 'dialogue-snippets.md', hasUnsavedChanges: true },
  { id: 'doc7', name: 'character-development.md', hasUnsavedChanges: false },
  { id: 'doc8', name: 'scene-descriptions.md', hasUnsavedChanges: false }
]

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
    markTabUnsaved,
    reorderTabs
  } = useEditorTabsWithState({ 
    projectId,
    initialTabs, 
    initialActiveTabId: 'doc1' 
  })

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
      content={getContentForTab(activeTab.name)}
      placeholder={`Start writing in ${activeTab.name}...`}
      container="flex flex-col h-full"
      border={false}
      rounded={false}
      railMode={railMode}
      onUpdate={() => {
        // Autosave hook would go here; unsaved tracking removed
      }}
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