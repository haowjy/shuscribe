# ShuScribe Frontend MVP Technical Specification

**"Cursor for Fiction Writing" - Frontend Implementation**

*Practical technical planning for Next.js + shadcn/ui + ProseMirror with client-side search*

---

## Core MVP Features

### Current Implementation Snapshot

**✅ Implemented Architecture**:
- **Universal Rail Navigation**: Complete route-based navigation system serving fiction writers with consistent workspace experience
- **Three-Panel Workspace**: Fully functional resizable layout with file explorer, editor, and AI panel areas
- **Project State Management**: Multi-project caching with localStorage persistence and automatic state restoration
- **Route Structure**: All project functionality organized under `/projects/[id]/[tool]` for predictable navigation
- **DocumentEditor**: Rich text editor with configurable toolbar, tables, images, formatting, and state persistence

**✅ Implemented Routes**:
- `/projects/[id]` → Explorer workspace with three-panel layout
- `/projects/[id]/series` → Series management interface
- `/projects/[id]/articles` → Article publishing interface
- `/projects/[id]/settings` → Project configuration
- `/projects/[id]/devtools` → Development tools (dev only)
- `/projects/[id]/component-gallery` → UI component testing (dev only)

**❌ Not yet implemented**: Real file explorer data, @-reference ProseMirror extensions, Supabase auth/middleware, TanStack Query, real API integration, AI panel functionality, wiki generation UI.

### MVP Feature Status

**✅ Implemented**:
1. **Flexible workspace** — Complete three-panel resizable layout with ActivityContainer and ContentAreaContainer patterns
2. **Route-based navigation** — Universal left-rail navigation consistent across all project tools
3. **Project state management** — Multi-project caching with complete workspace state persistence
4. **Editor integration** — DocumentEditor with toolbar, tabs, and state persistence across navigation
5. **Panel management** — Resizable/collapsible panels with configurations per activity type
6. **Component architecture** — Reusable layout patterns supporting future @-reference and AI integration

**🚧 In Progress**:
7. **@-reference system + tagging** — Foundation ready, ProseMirror extensions needed
8. **File explorer data** — UI structure complete, needs real file management integration
9. **AI panel functionality** — UI area allocated, needs actual AI integration

**🗺️ Planned Next**:
10. **Client-side autocomplete** — @-reference autocomplete from local project index
11. **Supabase auth** — Login/signup/logout with middleware
12. **Document management** — Create, edit, save, delete documents with real persistence
13. **AI wiki generation UI** — One-click wiki creation from @-references
14. **Export functionality** — Generate Markdown, PDF, EPUB files
15. **Publishing interface** — Publication wizard and public page management

### What We're NOT Building Yet
- Real-time collaboration
- AI chat functionality (just mock UI)
- Interactive reading experience (hover context, AI companion)
- Complex performance optimizations
- Advanced search/filtering beyond local fuzzy search
- Multi-content types (blogs, announcements, etc.)
- Advanced publishing features (monetization, analytics, community)

---

## Technology Stack

- **Next.js 14+** with App Router
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui** components
- **ProseMirror** for rich text editing
- **Supabase** (auth + database via FastAPI)
- **TanStack Query** for API state
- **Zustand** for simple client state

---

## Key Technical Components

### 1. Universal Rail Navigation (Implemented)

**Architecture**: ActivityContainer serves as universal route wrapper with left-rail navigation, providing consistent interface across all project functionality.

**Route Structure**: Dynamic content switching based on URLs (`/projects/[id]`, `/projects/[id]/settings`, etc.) while maintaining consistent navigation patterns.

**Panel Integration**: ContentAreaContainer provides three-panel workspace for complex tools, single content area for simple settings/configuration pages.

**User Experience Benefits**: Predictable URL structure for bookmarking, consistent left-rail navigation, state preservation across route switches, and familiar browser navigation patterns.

**Technical Implementation**: See `ActivityContainer` in `frontend/src/components/workspace/layout/ActivityContainer.tsx`, panel integration via `react-resizable-panels`, and state management in `ProjectStateProvider`.

### 2. Client-Side @-Reference + Tagging System (Core Feature)

**Local Index Strategy**: Frontend loads complete project data once, builds searchable index in memory for instant autocomplete without API delays.

**ProseMirror Integration**: Custom node types for @-references, plugin-based detection system, styled reference rendering with hover effects and client-side validation.

**Reference Types**: File references link to specific documents, tag references connect thematically related content across the project.

**Implementation Details**: See ProseMirror extensions in `frontend/src/components/editor/extensions/` and reference processing in `backend/src/agents/reference/`.

### 3. Document Management

**Document Operations**: Standard CRUD operations with template support, tabbed editing interface, auto-save functionality, and file tree integration.

**File Management**: Hierarchical tree display with context menus, file type icons, and seamless tab integration for multi-document editing.

**Implementation**: See file operations in `frontend/src/components/workspace/` and document management in `backend/src/agents/document/`.

### 4. Mock AI Panel

**Purpose**: Demonstrate future AI integration capabilities through UI mockups while establishing component architecture for real implementation.

**Components**: Mode selection interface, context extraction display, placeholder chat interface with sample suggestions.

**Implementation**: See AI panel components in `frontend/src/components/ai/` and mock backend services in `backend/src/agents/llm/`.

### 5. Publishing & Export System

Planned feature set. Details will be documented when implementation begins.

---

## Technical Implementation

### Project Structure (Implemented)

**Project Structure**: Next.js App Router with dynamic project routes, workspace components, editor integration, and state management providers.

**Architecture Benefits**: Clear separation between route handling and content rendering, reusable patterns across functionality, isolated state management, and type-safe Next.js integration.

**Directory Structure**: See complete organization in `frontend/src/` with routes in `app/projects/[id]/`, workspace components in `components/workspace/`, and UI primitives in `components/ui/`.

### State Management Strategy (Implemented)

**ProjectStateProvider** (Complete Implementation):
- **Multi-Project Caching**: Keeps up to 5 most recently accessed projects in memory
- **localStorage Integration**: Automatic session persistence with smart eviction
- **Complete State Persistence**: Editor tabs, panel arrangements, navigation state, last visited routes
- **Performance Optimized**: Debounced state updates and smart cache management

**State Structure**: Multi-project caching with editor tabs, panel arrangements, navigation state, and automatic cache management.

**State Interface**: See `ProjectState` interface in `frontend/src/components/providers/ProjectStateProvider.tsx`.

**Integration Points**: ActivityContainer manages state during navigation, panel components sync with provider, persistent editor tabs, and smart cache eviction.

**Future Integration**: TanStack Query integration planned for server state synchronization.

### ProseMirror Integration (Foundation Ready)

**Current Implementation**:
- **DocumentEditor**: Complete rich text editor with toolbar sections, tables, images, formatting
- **State Persistence**: Editor content and tabs persist across navigation via ProjectStateProvider
- **ContentAreaContainer Integration**: Consistent layout with header tabs and sidebar controls
- **Configurable Toolbar**: Full customization of toolbar sections for different use cases

**Architecture Ready for @-References**:
- Component structure supports ProseMirror plugin integration
- State management can handle reference index and autocomplete
- Editor integration patterns established for future @-reference features
- UI patterns ready for reference badges and disambiguation dialogs

**Planned Next**: Custom @-reference ProseMirror node type and autocomplete plugin for instant character/location linking.

### API Integration (Ready for Implementation)

**Frontend Architecture Prepared**:
- Route structure ready for API endpoint integration
- State management patterns established for server data
- Error handling and loading states defined in component patterns
- Type-safe interfaces ready in frontend architecture

**Current Status**: 
- UI and navigation fully functional with mock data
- State persistence working locally via ProjectStateProvider
- Component patterns ready for TanStack Query integration
- Route handlers ready for real API calls

**Next Steps**: 
- Add TanStack Query for server state management
- Integrate with FastAPI backend for real data persistence
- Connect authentication flow with Supabase
- Replace localStorage with server synchronization

---

## Key Implementation Challenges

### Implementation Priorities

**1. @-Reference System**: Foundation ready in editor components, needs ProseMirror schema definition, autocomplete plugin development, and cross-document navigation.

**2. Data Integration**: Infrastructure complete for API integration, authentication patterns ready for Supabase, file management UI ready for backend connection.

**3. Performance Optimization**: Core systems complete including resizable panels, route-based navigation, editor tabs with state persistence, and optimized caching.

**Implementation Status**: See current progress in component files and detailed roadmap in [`MVP-PLAN.md`](../frontend/MVP-PLAN.md).

### 5. Publishing & Export Implementation
- AI wiki generation progress tracking and error handling
- Large file export with proper download management
- Public page generation with SEO optimization
- Basic analytics tracking without complex infrastructure
- Export format handling (PDF generation, EPUB creation)

---

## Things to Keep in Mind (But Don't Build Yet)

### Future Enhancements:
- **Real AI integration** replacing mock panel
- **Advanced reference types** (filters, complex queries)
- **Collaborative editing** with Y.js and real-time sync
- **Performance optimizations** (virtualization for large projects)
- **Offline support** with local storage fallback
- **Keyboard shortcuts** and advanced accessibility
- **Advanced search** beyond local fuzzy search
- **Panel layout persistence** across devices

### Architectural Decisions:
- Local project index supports instant search now, can add server-side search later
- ProseMirror schema should be extensible for future node types
- Panel system ready for real-time collaborative cursors
- Component structure supports AI integration when ready
- State management simple now, but designed for complexity later

---

## Success Criteria

### Success Criteria

**Achieved Milestones**: Flexible workspace layout, panel management with persistence, consistent navigation system, complete state management, rich text editor integration, and bookmarkable route structure.

**Next Milestones**: @-reference system implementation, real document management, file explorer functionality, authentication integration, and API data persistence.

**User Experience Progress**: Core workspace navigation complete, editor functionality established, state persistence working, pending @-reference autocomplete and cross-document navigation.

---

### Current Status

**Foundation Complete**: Essential workspace architecture and navigation patterns established, providing solid foundation for fiction writers with consistent interface patterns.

**Next Phase**: Focus on @-reference system implementation and real data integration while maintaining established user experience patterns.

**Architecture Philosophy**: Universal container system serves fiction writers with predictable navigation, making feature additions seamless without disrupting core user experience.