'use client'

import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react'
import type { RailMode } from '@/components/workspace/layout/types'
import type { Tab } from '@/components/editor/tabs/types'

// Project state interface
interface ProjectState {
  // Editor state
  openTabs: Tab[]
  activeTabId: string
  
  // Navigation state
  lastVisitedRoute: string
  activeRailMode: RailMode
  
  // Timestamps
  lastUpdated: number
  lastAccessed: number
}

// Project cache interface
interface ProjectCache {
  [projectId: string]: ProjectState
}

// Context interface
interface ProjectStateContextType {
  // Current project state
  currentProjectId: string | null
  currentState: ProjectState | null
  
  // State management
  updateProjectState: (projectId: string, updates: Partial<ProjectState>) => void
  switchToProject: (projectId: string, initialState?: Partial<ProjectState>) => void
  
  // Editor state helpers
  updateEditorTabs: (projectId: string, tabs: Tab[], activeTabId: string) => void
  openFileInEditor: (projectId: string, fileId: string, fileName: string, documentId?: string) => void
  
  // Navigation helpers
  updateActiveRoute: (projectId: string, route: string, railMode: RailMode) => void
  
  // Cache management
  clearProjectCache: (projectId: string) => void
  getProjectState: (projectId: string) => ProjectState | null
  getMostRecentProjectId: () => string | null
}

// Default project state
const createDefaultProjectState = (): ProjectState => ({
  openTabs: [], // Start with no tabs - will be opened by file selection
  activeTabId: '',
  lastVisitedRoute: '',
  activeRailMode: 'workspace',
  lastUpdated: Date.now(),
  lastAccessed: Date.now()
})

const ProjectStateContext = createContext<ProjectStateContextType | null>(null)

// Storage keys
const STORAGE_KEY = 'shuscribe_project_cache'
const MAX_CACHED_PROJECTS = 5

interface ProjectStateProviderProps {
  children: ReactNode
}

export function ProjectStateProvider({ children }: ProjectStateProviderProps) {
  const [projectCache, setProjectCache] = useState<ProjectCache>({})
  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null)

  // Load cache from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved)
        setProjectCache(parsed)
      }
    } catch (error) {
      console.error('Failed to load project cache:', error)
    }
  }, [])

  // Save cache to localStorage when it changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(projectCache))
    } catch (error) {
      console.error('Failed to save project cache:', error)
    }
  }, [projectCache])

  // Evict oldest projects if cache exceeds limit
  const evictOldestProjects = useCallback((cache: ProjectCache): ProjectCache => {
    const projects = Object.entries(cache)
    if (projects.length <= MAX_CACHED_PROJECTS) return cache

    // Sort by last accessed time and keep only the most recent
    const sorted = projects.sort(([, a], [, b]) => b.lastAccessed - a.lastAccessed)
    const kept = sorted.slice(0, MAX_CACHED_PROJECTS)
    
    return Object.fromEntries(kept)
  }, [])

  const updateProjectState = useCallback((projectId: string, updates: Partial<ProjectState>) => {
    setProjectCache(prev => {
      const existing = prev[projectId] || createDefaultProjectState()
      const updated = {
        ...existing,
        ...updates,
        lastUpdated: Date.now(),
        lastAccessed: Date.now()
      }
      
      const newCache = {
        ...prev,
        [projectId]: updated
      }
      
      return evictOldestProjects(newCache)
    })
  }, [evictOldestProjects])

  const switchToProject = useCallback((projectId: string, initialState?: Partial<ProjectState>) => {
    setCurrentProjectId(projectId)
    
    // Update last accessed time
    setProjectCache(prev => {
      const existing = prev[projectId] || createDefaultProjectState()
      const updated = {
        ...existing,
        ...initialState,
        lastAccessed: Date.now()
      }
      
      return {
        ...prev,
        [projectId]: updated
      }
    })
  }, [])

  const updateEditorTabs = useCallback((projectId: string, tabs: Tab[], activeTabId: string) => {
    updateProjectState(projectId, { openTabs: tabs, activeTabId })
  }, [updateProjectState])

  const getProjectState = useCallback((projectId: string): ProjectState | null => {
    return projectCache[projectId] || null
  }, [projectCache])

  const openFileInEditor = useCallback((projectId: string, fileId: string, fileName: string, documentId?: string) => {
    const currentState = getProjectState(projectId) || createDefaultProjectState()
    const existingTabs = currentState.openTabs

    // Check if tab already exists
    const existingTab = existingTabs.find(tab => tab.id === fileId)
    if (existingTab) {
      // Just activate the existing tab
      updateProjectState(projectId, { activeTabId: fileId })
      return
    }

    // Create new tab for the file
    const newTab: Tab = {
      id: fileId,
      name: fileName,
      hasUnsavedChanges: false,
      documentId: documentId // Store document ID for content loading
    }

    // Add new tab and make it active
    const updatedTabs = [...existingTabs, newTab]
    updateProjectState(projectId, {
      openTabs: updatedTabs,
      activeTabId: fileId
    })
  }, [getProjectState, updateProjectState])

  const updateActiveRoute = useCallback((projectId: string, route: string, railMode: RailMode) => {
    updateProjectState(projectId, {
      lastVisitedRoute: route,
      activeRailMode: railMode
    })
  }, [updateProjectState])

  const clearProjectCache = useCallback((projectId: string) => {
    setProjectCache(prev => {
      const newCache = { ...prev }
      delete newCache[projectId]
      return newCache
    })
  }, [])

  const getMostRecentProjectId = useCallback((): string | null => {
    const projects = Object.entries(projectCache)
    if (projects.length === 0) return null
    
    // Sort by lastAccessed time, most recent first
    const sorted = projects.sort(([, a], [, b]) => b.lastAccessed - a.lastAccessed)
    return sorted[0][0] // Return the project ID of the most recent
  }, [projectCache])

  const currentState = currentProjectId ? projectCache[currentProjectId] || null : null

  const value: ProjectStateContextType = {
    currentProjectId,
    currentState,
    updateProjectState,
    switchToProject,
    updateEditorTabs,
    openFileInEditor,
    updateActiveRoute,
    clearProjectCache,
    getProjectState,
    getMostRecentProjectId
  }

  return (
    <ProjectStateContext.Provider value={value}>
      {children}
    </ProjectStateContext.Provider>
  )
}

export function useProjectState() {
  const context = useContext(ProjectStateContext)
  if (!context) {
    throw new Error('useProjectState must be used within a ProjectStateProvider')
  }
  return context
}