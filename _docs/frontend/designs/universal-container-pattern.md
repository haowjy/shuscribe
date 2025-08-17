# Universal Container Pattern

## Overview

The ActivityContainer implements a universal wrapper pattern that handles all project routes with dynamic content rendering. This pattern eliminates duplicate navigation systems and provides consistent rail navigation across all project functionality.

## Core Pattern

### Single Container, Multiple Contents

Instead of separate layouts for different tools, one container dynamically renders content based on the current route:

```tsx
export function ActivityContainer({ projectId }: ActivityContainerProps) {
  const pathname = usePathname()
  
  // Determine content type from route
  const railMode: RailMode = (() => {
    if (pathname.includes('/devtools')) return 'devtools'
    if (pathname.includes('/settings')) return 'settings'
    if (pathname.includes('/component-gallery')) return 'component-gallery'
    if (pathname.includes('/series')) return 'series'
    if (pathname.includes('/articles')) return 'articles'
    return 'explorer'
  })()
  
  // Dynamic content rendering
  const renderMainContent = () => {
    switch (railMode) {
      case 'devtools': return <DevToolsPage />
      case 'settings': return <SettingsPage />
      // ... other cases
      case 'explorer':
      default: return <WorkspaceLayout />
    }
  }
  
  return (
    <div className="h-screen bg-background flex overflow-hidden">
      <LeftRail activeMode={railMode} onModeChange={handleRailNavigation} />
      <div className="flex-1 min-h-0">
        {renderMainContent()}
      </div>
    </div>
  )
}
```

## Activity Configuration System

### Route-Based Panel Configuration

Different routes have different panel requirements:

```tsx
// Explorer needs full workspace with panels
const EXPLORER_CONFIGURATION: ActivityConfiguration = {
  leftPanel: { enabled: true, defaultOpen: true },
  rightPanel: { enabled: true, defaultOpen: false },
  bottomPanel: { enabled: true, defaultOpen: false }
}

// Tools use full content area without panels
const TOOL_CONFIGURATION: ActivityConfiguration = {
  leftPanel: { enabled: false, defaultOpen: false },
  rightPanel: { enabled: false, defaultOpen: false },
  bottomPanel: { enabled: false, defaultOpen: false }
}

// Configuration selection based on route
const activityConfig = railMode === 'explorer' ? EXPLORER_CONFIGURATION : TOOL_CONFIGURATION
```

### Panel State Management

Panel states are managed per activity configuration:

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

## Content Rendering Strategy

### Route-Specific Content

Each route renders its appropriate content while maintaining consistent chrome:

```tsx
const renderMainContent = () => {
  switch (railMode) {
    case 'devtools':
      return (
        <div className="h-full bg-background">
          <ToastProvider>
            <DevToolsPage onBackToProjects={() => {}} />
          </ToastProvider>
        </div>
      )
      
    case 'settings':
      return (
        <div className="h-full bg-background">
          <SettingsPage />
        </div>
      )
      
    case 'component-gallery':
      return (
        <div className="h-full bg-background p-6">
          <div className="container mx-auto max-w-6xl">
            <div className="mb-6">
              <h1 className="text-2xl font-semibold mb-2">Component Gallery</h1>
              <p className="text-muted-foreground">
                Browse and test UI components
              </p>
            </div>
            <ComponentGallery />
          </div>
        </div>
      )
      
    case 'explorer':
    default:
      return (
        <WorkspaceLayout
          activityConfig={activityConfig}
          panelStates={{
            leftPanel,
            rightPanel,
            bottomPanel
          }}
          railMode={railMode}
          projectId={projectId}
        />
      )
  }
}
```

## Integration with State Management

### Project State Integration

The container automatically manages project state during route navigation:

```tsx
const { 
  switchToProject, 
  updateActiveRoute, 
  updatePanelStates, 
  getProjectState 
} = useProjectState()

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

### Navigation Handler

Rail navigation triggers Next.js routing:

```tsx
const handleRailNavigation = useCallback((mode: RailMode) => {
  if (mode === 'explorer') {
    router.push(`/projects/${projectId}`)
  } else {
    router.push(`/projects/${projectId}/${mode}`)
  }
}, [router, projectId])
```

## Route Page Implementation

### Standardized Route Pages

All project route pages follow the same simple pattern:

```tsx
// /projects/[id]/settings/page.tsx
'use client'

import { useParams } from 'next/navigation'
import { ActivityContainer } from '@/components/workspace/layout/ActivityContainer'

export default function ProjectSettingsPage() {
  const params = useParams()
  const projectId = params.id as string

  return <ActivityContainer projectId={projectId} />
}
```

### Project Layout Provider

A layout provides necessary context for all project routes:

```tsx
// /projects/[id]/layout.tsx
'use client'

import { ProjectStateProvider } from '@/components/providers/ProjectStateProvider'

interface ProjectLayoutProps {
  children: React.ReactNode
}

export default function ProjectLayout({ children }: ProjectLayoutProps) {
  return (
    <ProjectStateProvider>
      {children}
    </ProjectStateProvider>
  )
}
```

## TypeScript Integration

### Type-Safe Rail Modes

All rail modes are type-safe across the system:

```tsx
export type RailMode = 'explorer' | 'component-gallery' | 'devtools' | 'settings' | 'series' | 'articles'

export interface ActivityConfiguration {
  leftPanel: PanelConfig
  rightPanel: PanelConfig
  bottomPanel: PanelConfig
}

export interface ActivityContainerProps {
  projectId: string
}
```

### Component Integration

The container integrates with existing component interfaces:

```tsx
export interface WorkspaceLayoutProps {
  activityConfig: ActivityConfiguration
  panelStates: PanelStates
  railMode: RailMode
  projectId: string
}
```

## Benefits

**Code Consolidation**:
- Single navigation system across all routes
- Eliminates duplicate layout implementations
- Consistent chrome and behavior

**Maintainability**:
- Central location for navigation logic
- Easy to add new routes and tools
- Type-safe route handling

**User Experience**:
- Consistent interface across all functionality
- Predictable navigation patterns
- State preservation across route changes

**Performance**:
- Single container reduces component mounting overhead
- Smart content rendering based on route
- Efficient state management integration

## Extension Pattern

### Adding New Routes

To add a new project tool:

1. Add the mode to `RailMode` type
2. Add rail item to `LeftRail` configuration
3. Add case to `renderMainContent()` switch
4. Create route page using `ActivityContainer`
5. Configure panel requirements if needed

```tsx
// 1. Type definition
export type RailMode = 'explorer' | 'new-tool' | '...'

// 2. Rail configuration
const mainRailItems: RailItem[] = [
  { id: 'new-tool', label: 'New Tool', icon: NewIcon },
  // ...
]

// 3. Content rendering
const renderMainContent = () => {
  switch (railMode) {
    case 'new-tool':
      return <NewToolComponent />
    // ...
  }
}

// 4. Route page
export default function NewToolPage() {
  const params = useParams()
  return <ActivityContainer projectId={params.id as string} />
}
```