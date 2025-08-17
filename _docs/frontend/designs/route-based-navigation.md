# Route-Based Navigation Architecture

## Overview

The frontend implements a universal left-rail navigation system using Next.js routing instead of complex state-based mode switching. All project functionality is accessed through dedicated routes under `/projects/[id]/`, providing predictable URLs and consistent navigation patterns.

## Core Architecture

### ActivityContainer Pattern

The `ActivityContainer` component serves as the universal wrapper for all project routes, dynamically rendering content based on the current pathname while maintaining consistent rail navigation.

```tsx
// Route-based content detection
const railMode: RailMode = (() => {
  if (pathname.includes('/devtools')) return 'devtools'
  if (pathname.includes('/settings')) return 'settings' 
  if (pathname.includes('/component-gallery')) return 'component-gallery'
  if (pathname.includes('/series')) return 'series'
  if (pathname.includes('/articles')) return 'articles'
  return 'explorer' // default
})()

// Dynamic content rendering
const renderMainContent = () => {
  switch (railMode) {
    case 'devtools': return <DevToolsPage />
    case 'settings': return <SettingsPage />
    case 'component-gallery': return <ComponentGallery />
    case 'series': return <SeriesManagementContent />
    case 'articles': return <ArticlesContent />
    case 'explorer':
    default: return <WorkspaceLayout />
  }
}
```

### Left Rail Navigation

The left rail (`LeftRail`) provides consistent navigation across all project routes:

```tsx
// Main project activities
const mainRailItems: RailItem[] = [
  { id: 'explorer', label: 'Explorer', icon: FolderOpen, shortcut: '⌘B' },
  { id: 'series', label: 'Series', icon: BookOpen },
  { id: 'articles', label: 'Articles', icon: FileText }
]

// Development and utility tools  
const toolsRailItems: RailItem[] = [
  { id: 'component-gallery', label: 'Component Gallery', icon: Palette },
  { id: 'devtools', label: 'Developer Tools', icon: Database } // dev only
]

// Settings and configuration
const settingsRailItems: RailItem[] = [
  { id: 'settings', label: 'Settings', icon: Settings, shortcut: '⌘,' }
]
```

### Route Structure

```
/projects/[id]                    → Explorer workspace (default)
/projects/[id]/series             → Series management
/projects/[id]/articles           → Article publishing  
/projects/[id]/component-gallery  → Component gallery (dev)
/projects/[id]/devtools          → Developer tools (dev)
/projects/[id]/settings          → Project settings
```

## Navigation Implementation

### Route-Based Mode Detection

Instead of managing complex state, the system determines the current mode by parsing the URL pathname:

```tsx
const railMode: RailMode = (() => {
  if (pathname.includes('/devtools')) return 'devtools'
  if (pathname.includes('/settings')) return 'settings'
  if (pathname.includes('/component-gallery')) return 'component-gallery'
  if (pathname.includes('/series')) return 'series'
  if (pathname.includes('/articles')) return 'articles'
  return 'explorer'
})()
```

### Navigation Handler

Rail clicks trigger Next.js routing instead of state changes:

```tsx
const handleRailNavigation = useCallback((mode: RailMode) => {
  if (mode === 'explorer') {
    router.push(`/projects/${projectId}`)
  } else {
    router.push(`/projects/${projectId}/${mode}`)
  }
}, [router, projectId])
```

### Active State Management

The rail automatically highlights the current route:

```tsx
<Button
  variant={activeMode === item.id ? 'secondary' : 'ghost'}
  onClick={() => handleModeClick(item.id)}
>
  <item.icon className="h-4 w-4" />
</Button>
```

## Activity Configuration

Different routes have different panel requirements:

```tsx
// Explorer mode needs all panels
const EXPLORER_CONFIGURATION: ActivityConfiguration = {
  leftPanel: { enabled: true, defaultOpen: true },
  rightPanel: { enabled: true, defaultOpen: false },
  bottomPanel: { enabled: true, defaultOpen: false }
}

// Tool modes use full content area
const TOOL_CONFIGURATION: ActivityConfiguration = {
  leftPanel: { enabled: false, defaultOpen: false },
  rightPanel: { enabled: false, defaultOpen: false }, 
  bottomPanel: { enabled: false, defaultOpen: false }
}
```

## Route Page Implementation

All project route pages use the same pattern:

```tsx
// /projects/[id]/settings/page.tsx
export default function ProjectSettingsPage() {
  const params = useParams()
  const projectId = params.id as string

  return <ActivityContainer projectId={projectId} />
}
```

The ActivityContainer handles:
- Route detection and mode switching
- Content rendering based on current route
- Rail navigation state management
- Panel configuration per route type

## Benefits

**Predictable Navigation**:
- Each tool has a dedicated URL
- Bookmarkable routes for specific project tools
- Clear mental model: URL = current context

**State Isolation**:
- Routes can manage their own specific state
- No complex mode switching logic
- Easier debugging and testing

**Scalability**:
- Easy to add new project tools
- Consistent patterns across all routes
- No growing complexity in central state management

**User Experience**:
- Familiar browser navigation (back/forward)
- Direct links to specific project tools
- Consistent interface across all functionality

## Integration Points

- **Next.js App Router**: Dynamic routes with `[id]` parameter
- **React Context**: Project state persistence via ProjectStateProvider
- **TypeScript**: Type-safe RailMode definitions across components
- **UI Components**: Consistent rail and content layout patterns