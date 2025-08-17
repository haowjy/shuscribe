## ShuScribe Frontend MVP - Current Implementation

**Status**: Core workspace architecture implemented with route-based navigation and complete state persistence.

**Architecture**: Universal ActivityContainer with left-rail navigation, serving fiction writers with consistent workspace experience across all project tools.

### Current Architecture (Implemented)

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Universal ActivityContainer (Route-Based Navigation)                         │
├──────────────────────────────────────────────────────────────────────────────┤
│ Rail │                    Dynamic Content Area                              │
│ ──── │ ──────────────────────────────────────────────────────────────────── │
│ 📁   │ Route: /projects/[id] (Explorer)                                    │
│ 📚   │ ┌─ Editor Tabs ─────────────────────────────────────────────┐        │
│ 📄   │ │ chapter-01.md │ characters.md │           [+]          │        │
│ ──── │ └───────────────────────────────────────────────────────────┘        │
│ 🎨   │ [Toolbar: History | Text | Lists | Align | Insert | Table]         │
│ 🧰   │                                                                      │
│ ──── │ Writing content with @-references...                                │
│ ⚙️   │ @characters/elara appears in the moonlight...                       │
│      │                                                                      │
│      │ [Footer: 847 words • Auto-saved • v1.1]                            │
│      │                                                                      │
│      │ Route: /projects/[id]/series (Series Management)                    │
│      │ ┌─ Series: "The Fire Chronicles" ─────────────────────────┐        │
│      │ │ Status: Draft    Visibility: Public                    │        │
│      │ │ Chapters:                                              │        │
│      │ │  1. chapter-01.md  ✓ published    2,143 words          │        │
│      │ │  2. chapter-02.md  draft          1,876 words          │        │
│      │ │ [Preview] [Publish] [Unpublish]                        │        │
│      │ └────────────────────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Rail Navigation**:
- 📁 Explorer: File browsing and editing workspace
- 📚 Series: Book/series organization and publishing
- 📄 Articles: Individual story publishing and sharing
- 🎨 Component Gallery: UI component testing (dev)
- 🧰 DevTools: Development and debugging tools (dev)
- ⚙️ Settings: Project and account configuration

### Key Features Implemented

**✅ Universal Navigation System**:
- Left-rail navigation consistent across all project tools
- Route-based content switching (`/projects/[id]/[tool]`)
- Active state management based on current route
- Familiar navigation patterns for fiction writers

**✅ Complete State Persistence**:
- Editor tabs persist across route navigation
- Panel arrangements saved per project
- Multi-project caching for instant switching
- localStorage integration for session persistence

**✅ Dynamic Content Rendering**:
- Single ActivityContainer handles all project routes
- Route-specific content with consistent chrome
- Panel configuration per activity type
- Integrated sidebar controls throughout

**✅ Editor Integration**:
- DocumentEditor with full toolbar and formatting
- Tab system with state persistence
- ContentAreaContainer layout pattern
- @-reference system foundation

### Technical Architecture

**Core Components**:
- `ActivityContainer` - Universal route wrapper with dynamic content
- `ProjectStateProvider` - Complete workspace state management 
- `ContentAreaContainer` - Reusable layout with sidebar integration
- `LeftRail` - Consistent navigation across all routes

**State Management**:
- React Context for project state persistence
- Smart caching with automatic eviction
- localStorage synchronization
- Route-based state restoration

**Navigation Pattern**:
- Next.js App Router with dynamic routes
- Route-based content switching vs complex mode management
- Type-safe rail mode definitions
- Consistent URL structure for bookmarking
```

### Components to Build (UI-only)

- Workspace layout
  - `WorkspaceLayout`: 3 resizable panels (react-resizable-panels), collapse/expand, responsive.
  - `WorkspaceHeader`: project selector placeholder, save status, word count (UI-only).
- File explorer (no real data)
  - `FileExplorer`: static in-memory tree, icons, expand/collapse, tag badges (UI-only).
  - Context menu (rename/delete/new folder/file) as non-functional UI.
- Tabs and editor container
  - `EditorTabs`: open/close/reorder tabs, unsaved indicator (UI-only).
  - `EditorSurface`: hosts `DocumentEditor` and footer.
- Editor
  - `DocumentEditor` (existing): toolbar sections (history, textStyle, formatting, lists, alignment, blocks, table); footer stats.
  - Selection context menu: quick actions (Ask AI, Rewrite, Fix grammar) as UI triggers.
- @-reference UI (mock)
  - `ReferenceAutocomplete`: trigger on `@`, dropdown suggestions from static list; keyboard nav; click to insert.
  - `ReferenceBadge`: styled inline node rendering; hover preview popover (mock content).
  - `ReferenceDisambiguationDialog`: shown when multiple matches (UI-only).
- AI panel (mock)
  - `AiPanel`: modes (Write/Edit/Plan/Wiki), context chips, spoiler slider, prompt textarea, Ask AI button.
  - `AiResponse`: mocked streaming skeleton with variants (Tone/Expand/Shorten) and apply actions (Insert/Replace/Append/Open as Note) that manipulate editor content locally.
- Utilities and primitives
  - `SaveStatus`: shows Auto-saved / Saving… (UI-only state).
  - `useLocalStorageState` hook: persist panel sizes, collapse states, and last-open tabs (frontend-only).

### Routes and Pages

- Workspace page
  - `src/app/page.tsx`: render `WorkspaceLayout` when `?project=<id>` present; otherwise fallback still can show workspace with mock project. No navigation or data required for MVP UI.
- Component gallery link (dev-only): keep `/component-gallery/editor/full` for reference while implementing.

### Editor Enhancements (UI-only)

- Toolbar configuration: ensure commands mapping for history, text, lists, alignment, blocks, tables.
- Footer: word/char counts, autosave indicator (simulated), version label (static).
- @-reference shell:
  - Minimal Tiptap plugin wrapper to detect `@` and open `ReferenceAutocomplete`.
  - Use hardcoded suggestions for now; no indexing/search.
  - Insert renders `ReferenceBadge` inline.

### AI Panel UX (UI-only)

- Mode selector: Write, Edit, Plan, Wiki (no behavior changes yet; just labels).
- Context chips: show selected refs/tags (mock values); removable chips.
- Spoiler slider: visual only; no filtering.
- Prompt box + Ask AI: on submit, show mocked streaming text (typewriter effect) in `AiResponse`.
- Apply actions: locally mutate editor content (replace selection, insert at cursor, append to end) with no server.

### UX Interactions

- Keyboard shortcuts (bind to UI handlers):
  - Cmd/Ctrl+Enter → Ask AI
  - Shift+Cmd/Ctrl+I → Rewrite selection
  - Esc → Cancel AI response (stops mock stream)
- Context menu on selection: Ask AI → submenu (Rewrite, Fix grammar, Shorten, Expand) – trigger same mock pipeline.

### Data Strategy (Local-First)

- **Storage Layer**: Use IndexedDB (Dexie) for all project data (`projects`, `documents`, `fileTree`, `tags`, `referenceIndex`). Use localStorage only for UI state (panel sizes, tabs).
- **Bootstrap Logic**: On app load, if stores are empty, show prompt: "Start blank" or "Load sample project." Auto-seed in dev mode.
- **Reference Index**: Build local in-memory index for @-references; persist snapshot for fast cold starts.
- **No Network**: Pure local-first for MVP; add sync layer later with provider abstraction.

### Dev Tools (Development Only)

- **Test Storage Route**: `src/app/test-storage/page.tsx` protected by dev flag.
- **Actions**: Clear all data, seed sample project, seed large demo, export/import JSON.
- **Access**: Only render when `process.env.NODE_ENV === 'development'` or `NEXT_PUBLIC_ENABLE_DEV_TOOLS=true`.

### Persistence Strategy

- **Data**: Projects, documents, file tree, tags → IndexedDB via Dexie.
- **UI State**: Panel sizes/collapsed state, open tabs → localStorage via `useLocalStorageState`.
- **Index**: @-reference index snapshot → IndexedDB for fast cold start.

### Accessibility & Performance

- A11y: focus trap for dialogs, ARIA for menus, keyboard navigation in autocomplete and tabs.
- Performance budgets (frontend-only):
  - Autocomplete open within <50ms (from static list).
  - Panel resize/collapse <100ms.

### Acceptance Criteria (UI-only)

- Layout
  - Resizable/collapsible three-panel workspace renders without data.
  - Header shows save status and word count placeholders.
- File Explorer
  - Static tree renders; expand/collapse; icons and tag badges visible.
- Tabs & Editor
  - Multiple tabs open/close/reorder; unsaved indicator toggles on edit.
  - Editor toolbar buttons execute formatting; footer shows counts.
- @-Reference
  - Typing `@` opens dropdown with keyboard navigation; selecting inserts styled badge.
  - Disambiguation dialog can be invoked from mock dataset.
- AI Panel
  - Modes switch UI state; context chips add/remove; spoiler slider moves.
  - Ask AI displays mocked streaming suggestion; Insert/Replace/Append apply to editor content.
- Persistence
  - Panel sizes and collapsed state persist; tabs restore on reload.

### Out of Scope (for this doc)

- Auth, Supabase integration, API clients, backend calls.
- Real AI providers, streaming, or wiki generation calls.
- Real @-reference indexing/search; use only static mock lists.

### Phase 2 (Follow-ups, not part of this task)

- Real @-reference: local project index, fuzzy search, integrity checks.
- Diff preview for AI Replace with segment-level accept/reject.
- SSE streaming UI and cancellation tied to real requests.
- Wiki mode: entry preview list and creation flows (UI already loosely represented).

---

### Task Breakdown (Frontend only)

1) **Data Layer** (Current Task)
- IndexedDB schema with Dexie
- Local data provider and bootstrap logic
- Dev tools for clearing/seeding data
- Reference index builder

2) **Layout & Header**
- WorkspaceLayout, WorkspaceHeader, SaveStatus

3) **File Explorer**
- FileExplorer (tree, icons, context menu UI)

4) **Tabs & Editor Surface**
- EditorTabs, EditorSurface integration with DocumentEditor

5) **@-Reference UI (mock)**
- ReferenceAutocomplete, ReferenceBadge, ReferenceDisambiguationDialog, minimal Tiptap plugin glue

6) **AI Panel (mock)**
- AiPanel, AiResponse, apply-to-editor actions

7) **Persistence Utilities**
- useLocalStorageState for panel and tabs state

8) **Polish & A11y**
- Keyboard shortcuts, focus management, ARIA labeling

### Future Phases

- **Phase 2**: Real backend integration with provider abstraction; keep local-first UX with background sync.
- **Phase 3**: Real AI integration, SSE streaming, wiki generation.
- **Phase 4**: Real-time collaboration with Yjs/Hocuspocus.
