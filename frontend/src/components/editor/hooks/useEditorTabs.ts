import { useState } from 'react'
import type { Tab } from '../tabs/types'

interface UseEditorTabsOptions {
  initialTabs?: Tab[]
  initialActiveTabId?: string
}

export function useEditorTabs({ 
  initialTabs = [],
  initialActiveTabId 
}: UseEditorTabsOptions = {}) {
  const [openTabs, setOpenTabs] = useState<Tab[]>(initialTabs)
  const [activeTabId, setActiveTabId] = useState(
    initialActiveTabId || initialTabs[0]?.id || ''
  )

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