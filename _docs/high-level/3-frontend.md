# ShuScribe Frontend MVP Technical Specification

**"Cursor for Fiction Writing" - Frontend Implementation**

*Practical technical planning for Next.js + shadcn/ui + ProseMirror with client-side search*

---

## Core MVP Features

### Current Implementation Snapshot

- Implemented now: Landing page (`/`) and Editor Test page (`/editor-test`) showcasing a rich Tiptap editor with toolbar, tables, images (via DataURL), lists, headings, formatting, highlight, sub/superscript, and alignment.
- Not yet implemented: workspace layout, @-reference system, dashboard/auth, API integration, TanStack Query, publishing/export, wiki generation UI.

### Planned MVP Features
1. Flexible workspace — Resizable/collapsible file explorer, editor, mock AI panel
2. @-reference system + tagging — Context-aware linking
3. Client-side autocomplete — Instant suggestions from local project index
4. Basic document management — Create, edit, save, delete documents
5. Project data loading — Load all documents/tags once for fast local search
6. Supabase auth — Login/signup/logout
7. AI wiki generation UI — One-click wiki creation from @-references
8. Export functionality — Generate Markdown, PDF, EPUB files
9. Basic publishing interface — Simple publication wizard and public page management

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

### 1. Flexible Workspace Layout

```
┌─────────────────────────────────────────────┐
│ Header (project selector, user menu)       │
├─────────────────────────────────────────────┤
│ File Explorer│  Editor Workspace │ AI Panel│
│ [▼] [↔]     │  (flexible center) │ [↔] [▼] │
│             │                    │         │
│ - resizable │ - ProseMirror      │- mock   │
│ - collapsible│ - @-references    │- context│
│ - file tree │ - local search     │- modes  │
│ - tags view │ - tabs             │         │
└─────────────────────────────────────────────┘
```

**Implementation Notes:**
- Use CSS Grid with `fr` units for flexible center panel
- Drag handles between panels for resizing
- Collapse buttons that hide panels and show icon bars
- Save panel states in localStorage or user preferences

### 2. Client-Side @-Reference + Tagging System (Core Feature)

**Local Project Index Approach:**
- Load all project documents and tags on project open
- Build searchable index in client memory
- No API calls for autocomplete → instant <50ms responses
- Fuzzy search through documents, paths, and tags

**ProseMirror Integration:**
- Custom node type for references: `@characters/elara`
- Plugin to detect `@` character and trigger instant autocomplete
- Render references as styled spans with hover effects
- Client-side validation against local project index

**Autocomplete Flow:**
1. User types `@` in editor
2. Plugin detects and shows dropdown instantly
3. Client-side fuzzy search of local project index
4. User selects → insert reference node in editor
5. Reference becomes clickable/hoverable

**Reference + Tag Types:**
- **File references**: `@characters/protagonists/elara`
- **Tag references**: `@fire-magic` (all docs with that tag)
- **Smart tagging**: Documents have multiple tags for thematic organization

### 3. Document Management

**Basic CRUD:**
- Create new document (with simple templates)
- Open document → new tab
- Edit in ProseMirror editor
- Save document (manual save button + auto-save on change)
- Delete document

**File Tree:**
- Show project structure as collapsible tree
- Click file → open in new tab
- Right-click → context menu (create, delete, rename)
- Simple icons for different file types

**Tab System:**
- Open documents appear as tabs above editor
- Click tab → switch document
- Close tab button
- *Keep it simple - no persistence or complex state*

### 4. Mock AI Panel

**Purpose:** Show what AI features will look like without implementing them

**Components:**
- Mode selector dropdown (Chapter Writing, Character Development, etc.) - non-functional
- Context display showing current document's references
- Placeholder chat interface with "Coming Soon" message
- Maybe some sample suggestions to show concept

### 5. Publishing & Export System

Planned feature set. Details will be documented when implementation begins.

---

## Technical Implementation

### Project Structure

Current minimal structure focuses on the editor demo (`components/editor/`, `app/page.tsx`, `app/editor-test/page.tsx`). Expanded structure is planned and tracked in design docs.

### State Management Strategy

Planned: TanStack Query for server state and small Zustand stores for UI. Not implemented yet.

### ProseMirror Integration

Current: Tiptap-based editor with core extensions (headings, lists, tables, images, formatting). Planned: custom @-reference node and autocomplete plugin.

### FastAPI Integration

Planned. See backend docs and API specification. Not implemented in frontend yet.

---

## Key Implementation Challenges

### 1. Client-Side Project Index
- Building efficient searchable index from all project documents
- Fuzzy search algorithm for instant autocomplete
- Keeping index in sync when documents change
- Memory management for large projects

### 2. Flexible Panel System
- CSS Grid layout with resizable panels
- Drag handles for panel resizing
- Panel collapse/expand with smooth animations
- Persistent panel state across sessions

### 3. @-Reference ProseMirror Integration
- Custom schema definition with reference nodes
- Plugin development for @ detection and autocomplete
- Styling references with Tailwind classes
- Handling reference clicks and navigation

### 4. Local Search Performance
- Fast fuzzy search through documents and tags
- Debounced search to avoid blocking UI
- Ranking algorithms for relevance
- Efficient re-indexing on content changes

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

**MVP is successful when:**
- User can create a project and add documents
- @-reference + tagging system works with instant autocomplete
- Flexible workspace layout feels intuitive and customizable
- Documents save and load reliably
- Local project search is fast and helpful
- Panel resizing/collapsing works smoothly

**Core User Flow:**
1. Login → Dashboard → Create/Open Project
2. Project loads → Complete data loaded once → Local index built
3. Create character document in `characters/` folder with tags
4. Create chapter document
5. Type `@characters/elara` in chapter → instant autocomplete works
6. Reference becomes clickable/hoverable
7. Navigate between documents via file tree and tabs
8. Resize panels to preferred layout → state persists

---

This specification focuses on building the essential features that make ShuScribe unique (the @-reference system) without getting bogged down in premature optimizations or complex features we don't need yet.