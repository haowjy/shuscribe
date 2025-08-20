import { useState, useEffect, useRef, useMemo, useLayoutEffect } from 'react'
import { useProjectState } from '@/components/providers/ProjectStateProvider'
import type { Tab } from '../tabs/types'

interface UseEditorTabsWithStateOptions {
  projectId: string
  initialTabs?: Tab[]
  initialActiveTabId?: string
}

export function useEditorTabsWithState({ 
  projectId,
  initialTabs = [],
  initialActiveTabId 
}: UseEditorTabsWithStateOptions) {
  const { getProjectState, updateEditorTabs } = useProjectState()
  
  // Get project state to initialize tabs
  const projectState = getProjectState(projectId)
  const savedTabs = projectState?.openTabs || initialTabs
  const savedActiveTabId = projectState?.activeTabId || initialActiveTabId || savedTabs[0]?.id || ''
  
  const [openTabs, setOpenTabs] = useState<Tab[]>(savedTabs)
  const [activeTabId, setActiveTabId] = useState(savedActiveTabId)
  
  // Track if we're updating from project state to prevent infinite loops
  const isUpdatingFromProjectState = useRef(false)
  const lastProjectState = useRef(projectState)

  // Memoize current project state to track changes
  const currentProjectState = useMemo(() => getProjectState(projectId), [getProjectState, projectId])

  // Listen for project state changes and sync to local state
  useEffect(() => {
    if (!currentProjectState) return
    
    // Only sync if project state actually changed (not on every render)
    const stateChanged = lastProjectState.current !== currentProjectState
    if (!stateChanged) return
    
    lastProjectState.current = currentProjectState
    
    const { openTabs: projectTabs, activeTabId: projectActiveTabId } = currentProjectState
    
    // Compare project state with local state
    const tabsChanged = JSON.stringify(projectTabs) !== JSON.stringify(openTabs)
    const activeTabChanged = projectActiveTabId !== activeTabId
    
    if (tabsChanged || activeTabChanged) {
      // Set flag to prevent write-back loop
      isUpdatingFromProjectState.current = true
      
      if (tabsChanged) {
        setOpenTabs(projectTabs)
      }
      if (activeTabChanged) {
        setActiveTabId(projectActiveTabId)
      }
    }
  }, [currentProjectState, openTabs, activeTabId])

  // Reset sync flag immediately after state updates
  useLayoutEffect(() => {
    if (isUpdatingFromProjectState.current) {
      isUpdatingFromProjectState.current = false
    }
  })

  // Update project state whenever tabs change (but not when updating from project state)
  useEffect(() => {
    if (!isUpdatingFromProjectState.current) {
      console.log('📝 useEditorTabsWithState: Writing to project state', { openTabs: openTabs.length, activeTabId })
      updateEditorTabs(projectId, openTabs, activeTabId)
    }
  }, [projectId, openTabs, activeTabId, updateEditorTabs])

  const handleTabClose = (tabId: string) => {
    const updatedTabs = openTabs.filter(tab => tab.id !== tabId)
    setOpenTabs(updatedTabs)
    
    // If closing active tab, switch to another tab
    if (tabId === activeTabId && updatedTabs.length > 0) {
      setActiveTabId(updatedTabs[0].id)
    }
  }

  const handleNewTab = () => {
    const newTab: Tab = {
      id: `doc${Date.now()}`,
      name: 'untitled.md',
      hasUnsavedChanges: true
    }
    setOpenTabs(prev => [...prev, newTab])
    setActiveTabId(newTab.id)
  }

  const handleTabSelect = (tabId: string) => {
    setActiveTabId(tabId)
  }

  const updateTabName = (tabId: string, name: string) => {
    setOpenTabs(prev => prev.map(tab => 
      tab.id === tabId ? { ...tab, name } : tab
    ))
  }

  // Autosave is default; unsaved tracking removed
  const markTabUnsaved = (_tabId: string) => {}
  const markTabSaved = (_tabId: string) => {}

  const reorderTabs = (fromIndex: number, toIndex: number) => {
    setOpenTabs(prev => {
      const newTabs = [...prev]
      const [movedTab] = newTabs.splice(fromIndex, 1)
      newTabs.splice(toIndex, 0, movedTab)
      return newTabs
    })
  }

  const activeTab = openTabs.find(tab => tab.id === activeTabId)

  return {
    openTabs,
    activeTabId,
    activeTab,
    handleTabClose,
    handleNewTab,
    handleTabSelect,
    updateTabName,
    markTabUnsaved,
    markTabSaved,
    reorderTabs
  }
}