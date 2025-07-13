# ShuScribe Frontend MVP Technical Specification

**"Cursor for Fiction Writing" - Frontend Implementation**

*Practical technical planning for Next.js + shadcn/ui + ProseMirror with client-side search*

---

## Core MVP Features

### What We're Actually Building
1. **Flexible workspace** - Resizable/collapsible file explorer, editor, mock AI panel
2. **@-reference system + tagging** - Context-aware linking like "Cursor for fiction writing"
3. **Client-side autocomplete** - Instant suggestions from local project index
4. **Basic document management** - Create, edit, save, delete documents
5. **Project data loading** - Load all documents/tags once for fast local search
6. **Supabase auth** - Login/signup/logout
7. **AI wiki generation UI** - One-click wiki creation from @-references
8. **Export functionality** - Generate Markdown, PDF, EPUB files
9. **Basic publishing interface** - Simple publication wizard and public page management

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

**Purpose:** Validate the core platform concept by enabling wiki generation and basic publishing

#### AI Wiki Generation Interface
```typescript
interface WikiGenerationUI {
  // Wiki generation trigger
  generateButton: "Generate Wiki from @-references";
  progressIndicator: WikiGenerationProgress;
  
  // Configuration options
  spoilerManagement: {
    arcBreakpoints: ArcDefinition[];
    spoilerLevels: SpoilerLevel[];
  };
  
  // Preview and editing
  wikiPreview: WikiPreviewComponent;
  editMode: WikiEditingInterface;
}
```

**Components:**
- **Wiki Generation Wizard**: Step-by-step process for creating wikis from @-references
- **Arc Management**: Define story arcs for spoiler-safe wiki organization
- **Wiki Preview**: Show generated wiki content with editing capabilities
- **Spoiler Controls**: Manage what content is revealed at different story points

#### Export Functionality
```typescript
interface ExportUI {
  // Format selection
  exportFormats: ('markdown' | 'pdf' | 'epub')[];
  
  // Content selection
  contentSelector: {
    includeStory: boolean;
    includeWiki: boolean;
    specificChapters: number[];
  };
  
  // Export options
  exportOptions: ExportConfiguration;
  downloadHandler: ExportDownload;
}
```

**Components:**
- **Export Wizard**: Multi-step export process with format and content selection
- **Format Options**: PDF styling, EPUB metadata, Markdown formatting options
- **Preview Generator**: Show export preview before final generation
- **Download Manager**: Handle large file downloads with progress indicators

#### Basic Publishing Interface
```typescript
interface PublishingUI {
  // Publication settings
  publicationMode: 'story-only' | 'wiki-only' | 'story-and-wiki';
  visibility: 'private' | 'unlisted' | 'public';
  
  // Simple public page
  publicPageBuilder: PublicPageBuilder;
  urlManager: CustomDomainHandler;
  
  // Basic analytics
  analyticsView: BasicAnalytics;
}
```

**Components:**
- **Publishing Wizard**: Simple process to make stories/wikis public
- **Public Page Editor**: Basic customization of public story pages
- **URL Management**: Handle public URLs and custom domains
- **Basic Analytics**: View counts and basic engagement metrics

---

## Technical Implementation

### Project Structure

```
frontend/src/
├── app/                     # Next.js app router
│   ├── (auth)/             # Auth pages
│   ├── (dashboard)/        # Main app
│   ├── project/[id]/       # Project workspace
│   └── public/             # Public story/wiki pages
├── components/
│   ├── editor/             # ProseMirror components
│   ├── project/            # File tree, navigation
│   ├── ai/                 # Mock AI panel
│   ├── publishing/         # Publishing UI components
│   ├── wiki/               # Wiki generation and display
│   └── ui/                 # shadcn/ui components
├── lib/
│   ├── supabase/           # Auth client
│   ├── api/                # FastAPI client
│   ├── prosemirror/        # Editor schema/plugins
│   ├── publishing/         # Export and publishing utilities
│   └── stores/             # Zustand stores
└── types/                  # TypeScript types
```

### State Management Strategy

**Project Data Loading:**
- Load complete project on open: all documents, metadata, tags
- Build local searchable index for instant autocomplete
- Cache in memory for session, refresh on document changes

**Zustand Stores (Keep Simple):**
- `useAuthStore` - User session, login/logout
- `useProjectStore` - Project data, local index, file tree state
- `useWorkspaceStore` - Panel sizes, collapse states, UI preferences
- `useEditorStore` - Open tabs, active document
- `usePublishingStore` - Wiki generation state, export progress, publishing status

**TanStack Query:**
- Load project data once per session
- Document save mutations with optimistic updates
- Reference validation on save (not for autocomplete)
- Wiki generation mutations with progress tracking
- Export operations with file download handling
- Publishing mutations for making content public

### ProseMirror Integration

**Custom Schema:**
- Standard nodes (paragraph, heading, text)
- Custom `reference` node for @-references
- Basic marks (bold, italic)

**Key Plugins:**
- Reference input detection (@ character)
- Reference autocomplete
- Basic editing commands

**Reference Node:**
```typescript
// Conceptual structure - we'll implement this
referenceNode = {
  attrs: {
    type: 'file' | 'tag',
    path: string,
    displayText: string,
    isValid: boolean
  },
  // rendering, parsing logic
}
```

### FastAPI Integration

**Core Endpoints:**
- `GET /projects/{id}/data` - Load complete project data once
- `GET /documents/{id}` - Get single document content
- `POST /documents` - Create document
- `PUT /documents/{id}` - Save document
- `POST /projects/{id}/references/validate` - Validate references on demand

**Publishing Endpoints:**
- `POST /projects/{id}/wiki/generate` - Generate AI wiki from @-references
- `GET /projects/{id}/wiki` - Get generated wiki content
- `POST /documents/{id}/export` - Export document to various formats
- `POST /projects/{id}/publish` - Publish story/wiki publicly
- `GET /public/stories/{slug}` - Public story page
- `GET /public/wikis/{slug}` - Public wiki page

**Client Setup:**
- Simple fetch wrapper with auth headers
- TanStack Query for project data loading and document mutations
- Local project index for instant search (no API calls for autocomplete)
- Publishing operations with progress tracking and error handling
- Export file downloads with proper MIME types

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