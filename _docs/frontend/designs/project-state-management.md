# Project State Management Architecture

## Overview

The ProjectStateProvider implements comprehensive workspace state persistence, ensuring that editor tabs, panel configurations, and navigation state are preserved across route changes and project switching. This enables instant project switching without losing context.

## Core Architecture

### ProjectStateProvider

A React Context provider that manages workspace state for multiple projects with smart caching and localStorage persistence.

```tsx
interface ProjectState {
  // Editor state
  openTabs: Tab[]
  activeTabId: string
  
  // Panel states  
  leftPanelCollapsed: boolean
  rightPanelCollapsed: boolean
  bottomPanelCollapsed: boolean
  
  // Navigation state
  lastVisitedRoute: string
  activeRailMode: RailMode
  
  // Timestamps
  lastUpdated: number
  lastAccessed: number
}
```

### Multi-Project Caching

The system caches up to 5 projects in memory with smart eviction based on last accessed time:

```tsx
const evictOldestProjects = useCallback((cache: ProjectCache): ProjectCache => {
  const projects = Object.entries(cache)
  if (projects.length <= MAX_CACHED_PROJECTS) return cache

  // Sort by last accessed time and keep only the most recent
  const sorted = projects.sort(([, a], [, b]) => b.lastAccessed - a.lastAccessed)
  const kept = sorted.slice(0, MAX_CACHED_PROJECTS)
  
  return Object.fromEntries(kept)
}, [])
```

## State Persistence Layers

### Session Storage (React Context)

Real-time state management during active session:

```tsx
const [projectCache, setProjectCache] = useState<ProjectCache>({})
const [currentProjectId, setCurrentProjectId] = useState<string | null>(null)
```

### localStorage Integration

Automatic persistence across browser sessions:

```tsx
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
```

## State Management Operations

### Project Switching

Seamless project switching with state restoration:

```tsx
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
```

### Editor State Integration

Editor tabs are automatically synchronized with project state:

```tsx
const updateEditorTabs = useCallback((projectId: string, tabs: Tab[], activeTabId: string) => {
  updateProjectState(projectId, { openTabs: tabs, activeTabId })
}, [updateProjectState])
```

### Panel State Synchronization

Panel collapse/expand states are preserved per project:

```tsx
const updatePanelStates = useCallback((projectId: string, panels: {
  leftCollapsed?: boolean
  rightCollapsed?: boolean  
  bottomCollapsed?: boolean
}) => {
  updateProjectState(projectId, {
    leftPanelCollapsed: panels.leftCollapsed,
    rightPanelCollapsed: panels.rightCollapsed,
    bottomPanelCollapsed: panels.bottomCollapsed
  })
}, [updateProjectState])
```

## Integration with Components

### ActivityContainer Integration

The ActivityContainer automatically manages project state during navigation:

```tsx
// Initialize project state when component mounts or project changes
useEffect(() => {
  switchToProject(projectId, { activeRailMode: railMode })
}, [projectId, switchToProject, railMode])

// Update active route when pathname changes
useEffect(() => {
  updateActiveRoute(projectId, pathname, railMode)
}, [projectId, pathname, railMode, updateActiveRoute])

// Update panel states in project state when they change
useEffect(() => {
  updatePanelStates(projectId, {
    leftCollapsed: leftPanel.isCollapsed,
    rightCollapsed: rightPanel.isCollapsed,
    bottomCollapsed: bottomPanel.isCollapsed
  })
}, [
  projectId,
  leftPanel.isCollapsed,
  rightPanel.isCollapsed,
  bottomPanel.isCollapsed,
  updatePanelStates
])
```

### Editor Tabs with State

Custom hook that integrates editor tabs with project state:

```tsx
export function useEditorTabsWithState({ 
  projectId,
  initialTabs = [],
  initialActiveTabId 
}: UseEditorTabsWithStateOptions) {
  const { getProjectState, updateEditorTabs } = useProjectState()
  
  // Get project state to initialize tabs
  const projectState = getProjectState(projectId)
  const savedTabs = projectState?.openTabs || initialTabs
  const savedActiveTabId = projectState?.activeTabId || initialActiveTabId
  
  const [openTabs, setOpenTabs] = useState<Tab[]>(savedTabs)
  const [activeTabId, setActiveTabId] = useState(savedActiveTabId)

  // Update project state whenever tabs change
  useEffect(() => {
    updateEditorTabs(projectId, openTabs, activeTabId)
  }, [projectId, openTabs, activeTabId, updateEditorTabs])
}
```

## State Initialization

### Default Project State

New projects start with sensible defaults:

```tsx
const createDefaultProjectState = (): ProjectState => ({
  openTabs: [
    { id: 'doc1', name: 'chapter-01.md', hasUnsavedChanges: true },
    { id: 'doc2', name: 'characters.md', hasUnsavedChanges: false }
  ],
  activeTabId: 'doc1',
  leftPanelCollapsed: false,
  rightPanelCollapsed: true,
  bottomPanelCollapsed: true,
  lastVisitedRoute: '',
  activeRailMode: 'explorer',
  lastUpdated: Date.now(),
  lastAccessed: Date.now()
})
```

### State Restoration

Panel states are restored from project state:

```tsx
// Panel state management - initialize from project state or defaults
const leftPanel = usePanelState(
  projectState?.leftPanelCollapsed ?? !activityConfig.leftPanel.defaultOpen
)
const rightPanel = usePanelState(
  projectState?.rightPanelCollapsed ?? !activityConfig.rightPanel.defaultOpen
)
const bottomPanel = usePanelState(
  projectState?.bottomPanelCollapsed ?? !activityConfig.bottomPanel.defaultOpen
)
```

## Performance Optimizations

### Smart Cache Eviction

Only keep the 5 most recently accessed projects in memory:

```tsx
const MAX_CACHED_PROJECTS = 5

const evictOldestProjects = useCallback((cache: ProjectCache): ProjectCache => {
  // Implementation that sorts by lastAccessed and keeps top 5
}, [])
```

### Debounced State Updates

State updates are batched to prevent excessive localStorage writes:

```tsx
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
```

## Benefits

**Instant Project Switching**:
- No reload delays when switching between projects
- Complete workspace context preserved
- Recently used projects cached in memory

**Work Continuity**:
- Open editor tabs persist across navigation
- Panel arrangements remember user preferences
- Navigation state preserved per project

**Performance**:
- Smart caching prevents memory bloat
- localStorage integration for session persistence
- Optimized state updates to reduce re-renders

**User Experience**:
- Never lose your place when switching tools
- Consistent workspace across sessions
- Seamless multi-project workflow