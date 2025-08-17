# Frontend UI Patterns

## Sidebar Development Patterns

### Collapse Behavior
Sidebars use `SidebarContainer.tsx` which includes collapse buttons that disappear when the sidebar is hidden.

### Re-expand Implementation
When implementing sidebar collapse, developers must add re-expand buttons elsewhere in the UI:

**Common Locations**:
- Header bar
- Main content area
- Dedicated toolbar

**Icon Pattern**:
- Use `PanelLeftClose`/`PanelRightClose` icons for collapse
- Use `PanelLeft`/`PanelRight` icons for expand

**State Management**: Track sidebar visibility state and provide toggle handlers.

**Implementation Example**: See `LeftSidebar.tsx:14` and `RightSidebar.tsx:34` for `onToggle` prop usage, and `SidebarContainer.tsx:107-124` for collapse button implementation.

## Navigation Strategy

### Design Philosophy
Respects creative workflow patterns - writers focus deeply on single projects rather than rapidly switching between universes.

### UI Patterns
Navigation uses VS Code-like layout with persistent project focus and minimal context switching between different universes.

### Three-Panel Layout
1. **File Explorer** (left) - Hierarchical project organization with path-based auto-folder creation
2. **Document Editor** (center) - Tabbed document editor with @-reference system and ProseMirror rich content
3. **AI Assistant** (right) - Context-aware AI assistance (future implementation)

## Path-Based Organization

### Automatic Folder Creation
Documents use intuitive file paths (e.g., `/world/regions/kingdoms/stormlands/cities`) with automatic folder creation, eliminating manual folder management.

### Implementation Pattern
- **Path-Based Document Creation**: Documents automatically create folder hierarchies from paths
- Example: `/characters/locations/taverns/document` creates all missing folders automatically

## @-Reference System

### Cross-Reference Syntax
- Documents support `@character/name`, `@location/place` syntax for cross-references
- References are highlighted and clickable in editor

### Performance Implementation
- **Frontend-Only**: Search uses local file tree data for instant results
- **No Backend Integration**: Reference search stays in frontend for performance optimization
- Uses local cache for immediate autocomplete and navigation

## Component Architecture Patterns

### shadcn/ui Integration
- Use utility-first Tailwind approach with direct classes in JSX
- Never create CSS_CLASSES constants (anti-pattern that defeats Tailwind's purpose)
- Leverage shadcn/ui components for consistent design system

### State Management Patterns
- TanStack Query for server state
- Local storage for offline-first experience
- Optimistic updates for instant UI feedback

### Authentication Integration
- Supabase Auth handled entirely in frontend
- Context providers for auth state management
- Bearer token flow to backend APIs