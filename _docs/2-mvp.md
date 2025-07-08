# ShuScribe MVP Complete System Overview

**Context-Aware Fiction Writing Platform - Full MVP Specification**

_How Frontend + Backend Work Together to Deliver the Core @-Reference System_

---

## MVP Vision & Core Value Proposition

### What ShuScribe MVP Delivers

**"Cursor for fiction writing - context-aware assistance through smart references and tagging"**

**Core Innovation:** Like how Cursor understands your codebase, ShuScribe understands your story world through @-references and tags, providing intelligent context within a flexible workspace.

**Target User:** Fiction writers who struggle to keep track of story elements across multiple documents and chapters.

---

## Complete System Architecture

### Technology Stack Overview

```
Frontend (Next.js)              Backend (FastAPI)              Database (Supabase)
├── React + TypeScript          ├── Python + FastAPI           ├── PostgreSQL
├── shadcn/ui + Tailwind        ├── SQLAlchemy + Pydantic      ├── Auth management
├── ProseMirror editor          ├── Dependency injection       ├── Real-time capabilities
├── TanStack Query              ├── Reference processing       └── File storage
└── Zustand stores              └── Mock AI services           
```

### Data Flow Architecture

```
Project Load → Frontend Fetches All Documents & Tags → Local Index Built
    ↓
User Types "@char..." 
    ↓
ProseMirror Plugin Detects @ 
    ↓
Client-Side Fuzzy Search of Local Index
    ↓
Instant Suggestion List (no API call)
    ↓
User Selects → Reference Inserted 
    ↓
Document Saved → Backend Extracts References → Updates Index
```

---

## Core Feature Set

### 1. Context-Aware Reference + Tagging System (Primary Feature)

**What It Does:**

- **@-References:** Type `@` to link documents: `@characters/protagonists/elara`
- **Tag References:** Link by theme: `@fire-magic` (finds all documents with that tag)
- **Smart Tagging:** Documents can have multiple tags for thematic organization
- **Instant Autocomplete:** Client-side fuzzy search of all project content (no API delay)
- **Visual Context:** See all story elements connected to current document

**User Experience:**

```
User writing: "Elara walked into the tavern, her @"
                                              ↑
                                    Instant dropdown with:
                                    📄 @characters/protagonists/elara 🔥💔
                                    🏷️ @fire-magic (3 documents)
                                    📄 @locations/settlements/hometown
```

**Technical Implementation:**

- **Frontend:** Project data loaded once → built into searchable index
- **Frontend:** Custom ProseMirror plugin detects `@` → instant client-side search
- **Frontend:** No API calls for autocomplete (uses local project index)
- **Backend:** Reference extraction and tag management on document save

### 2. Flexible Workspace Layout

**Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│ Header: Project Selector | User Menu | Save Status         │
├─────────────────────────────────────────────────────────────┤
│ File Explorer │        Editor Workspace        │ AI Panel │
│ [▼] [↔]       │         (flexible)             │ [↔] [▼]  │
│               │                                │          │
│ 📁 characters │ ┌─ Tabs ──────────────────────┐│ Mode:    │
│ ├─ 👥 protag  │ │ elara.md │ chapter1.md │ x ││ 📝 Write │
│ ├─ 💀 antag   │ └─────────────────────────────┘│          │
│ └─ 🤝 support │                                │ Context: │
│               │ ProseMirror Editor             │ • elara  │
│ 📁 locations  │ with @-reference system        │ • magic  │
│ 📁 timeline   │                                │          │
│ 📁 world      │ Status: Auto-saved • 847 words│ [Mock]   │
└─────────────────────────────────────────────────────────────┘
```

**Panel Features:**

- **Flexible Layout:** All panels resizable with drag handles
- **Collapsible:** File explorer and AI panel can collapse to icons
- **Responsive:** Layout adapts to screen size and user preferences
- **Persistent:** Panel sizes/states saved per user

### 3. Document Management System

**Project Structure:**

```
My Fantasy Novel/
├── characters/
│   ├── protagonists/
│   │   ├── elara.md         🔥💔 (tags: fire-magic, trauma)
│   │   └── marcus.md        🌍🎓 (tags: earth-magic, mentor)
│   ├── antagonists/
│   └── supporting/
├── locations/
│   ├── settlements/
│   └── mystical/
├── timeline/
└── worldbuilding/
```

**Document Operations:**

- Create documents with templates
- Open multiple documents in tabs
- Auto-save on content changes
- Delete with reference integrity checking
- Rename with automatic reference updates

### 4. Reference Intelligence

**Reference Types:**

- **File References:** `@characters/protagonists/elara` → Direct link to character document
- **Tag References:** `@fire-magic` → All documents tagged with fire-magic
- **Path Completion:** Smart autocomplete based on project structure

**Intelligence Features:**

- **Broken Reference Detection:** Visual indicators for invalid references
- **Reference Counting:** Show how many times elements are referenced
- **Context Extraction:** AI panel shows current document's story context
- **Hover Previews:** Quick view of referenced content

### 5. Authentication & Project Management

**User Experience:**

- Simple email/password login via Supabase
- Dashboard showing user's projects
- Create new projects with folder templates
- Project settings and sharing (basic)

**Technical Implementation:**

- Supabase handles auth complexity
- Frontend gets JWT tokens
- Backend validates tokens for API access
- User-project ownership and permissions

---

## Key User Workflows

### Workflow 1: New User Onboarding

1. **Sign up** → Email verification via Supabase
2. **Create first project** → "My Fantasy Novel"
3. **Auto-generated structure** → characters/, locations/, etc. folders
4. **Create character** → characters/protagonists/elara.md
5. **Add character details** → Tags: fire-magic, trauma
6. **Create chapter** → chapter1.md
7. **Use @-reference** → Type `@characters/elara` → See autocomplete → Insert reference
8. **See AI context** → Right panel shows "Context: elara, fire-magic"

### Workflow 2: Active Writing Session

1. **Open project** → Last session restored
2. **Open chapter document** → Tabs from previous session
3. **Write scene** → "Elara entered the @" → Autocomplete suggests locations
4. **Insert reference** → `@locations/mystical/ancient-temple`
5. **Continue writing** → References become part of natural prose
6. **Check context** → AI panel shows all story elements in current document
7. **Navigate** → Click reference → Opens referenced document in new tab

### Workflow 3: Story Organization

1. **Create new character** → Add to characters/antagonists/
2. **Tag character** → Add relevant theme tags
3. **Reference in multiple chapters** → `@characters/antagonists/villain`
4. **Check reference usage** → File explorer shows reference counts
5. **Rename character** → All references update automatically
6. **Validate integrity** → System checks for broken references

---

## Technical Integration Points

### Frontend ↔ Backend Communication

**Authentication Flow:**

```
Frontend                    Backend                     Supabase
├── User login             ├── Validate JWT            ├── Issue JWT token
├── Store JWT token        ├── Extract user ID         ├── Handle auth logic
├── Send in API headers    ├── Protect routes          └── Manage sessions
└── Handle auth state      └── Return user data        
```

**Document Operations:**

```
Frontend                    Backend                     Database
├── Open document          ├── GET /documents/{id}     ├── Fetch document
├── Edit in ProseMirror    ├── PUT /documents/{id}     ├── Save content
├── Auto-save changes     ├── Extract references      ├── Update references
└── Show save status       └── Validate integrity      └── Maintain consistency
```

**Reference System:**

```
Frontend                    Backend                     Processing
├── Load project once      ├── GET /projects/{id}/data ├── Return all docs + tags
├── Build local index      ├── Documents + metadata    ├── File tree structure
├── Detect @ character     ├── Tags and relationships  ├── Reference mappings
├── Client-side search     ├── No autocomplete API     └── Complete project context
├── Instant suggestions    ├── Validate on save        
├── Insert reference       ├── Extract new references  
└── Render as styled span  └── Update project index    
```

### Database Schema Integration

**Core Tables:**

```sql
users (id, supabase_user_id, email, created_at)
projects (id, user_id, title, created_at, updated_at)
documents (id, project_id, path, title, content_json, tags, word_count)
document_references (source_doc_id, target_path, reference_type, is_valid)
```

**Key Relationships:**

- User owns multiple Projects
- Project contains hierarchical Documents
- Documents contain References to other Documents
- References maintain integrity across operations

---

## Mock AI Integration (Foundation for Future)

### Current MVP Implementation

**Purpose:** Show users what AI features will look like without implementing them

**AI Panel Components:**

- **Mode Selector:** Dropdown with options (Chapter Writing, Character Development, etc.) - non-functional
- **Context Display:** Shows current document's references and story elements
- **Chat Interface:** Placeholder with "Coming Soon" messages
- **Sample Suggestions:** Hardcoded examples of future AI assistance

### API Structure (Ready for Real Implementation)

```
POST /projects/{id}/ai/chat
├── Request: { message: string, mode: string, context: DocumentContext }
├── Current: Returns hardcoded responses
└── Future: Real AI integration with OpenAI/Anthropic

GET /documents/{id}/ai/context  
├── Current: Extracts references and returns story context
└── Future: Enhanced with AI-generated insights

POST /documents/{id}/ai/suggestions
├── Current: Returns mock writing suggestions
└── Future: Real AI suggestions based on content and context
```

---

## Success Metrics & Validation

### User Engagement Metrics

- **@-references created per session:** Target >10 (shows core feature adoption)
- **Documents created per project:** Target >5 (comprehensive story building)
- **Reference navigation clicks:** Target >5 per session (users exploring connections)
- **Time spent in editor:** Target >20 minutes (productive writing sessions)

### Technical Performance Metrics

- **Reference autocomplete response:** <50ms (instant client-side search)
- **Project load time:** <2 seconds (all documents and tags loaded once)
- **Document save time:** <500ms (doesn't interrupt flow)
- **Panel resize/collapse:** <100ms (smooth UI interactions)
- **Reference validation accuracy:** >95% (reliable integrity checking)

### Feature Adoption Metrics

- **Users creating @-references:** >80% (core feature adoption)
- **Multi-document projects:** >65% (complex story building)
- **Tag usage for organization:** >60% (thematic organization)
- **Reference clicking/navigation:** >70% (discovering connections)

---

## MVP Scope Boundaries

### What's Included in MVP

✅ **@-reference system** with autocomplete and validation  
✅ **Three-panel workspace** with file tree and editor  
✅ **Document CRUD** operations with auto-save  
✅ **Basic project management** and file organization  
✅ **Supabase authentication** and user management  
✅ **Mock AI panel** showing future capabilities  
✅ **Reference integrity** checking and broken link detection

### What's Explicitly NOT in MVP

❌ **Real-time collaboration** (Y.js, WebSocket, presence)  
❌ **AI chat implementation** (OpenAI/Anthropic integration)  
❌ **Publishing platform** (public stories, wikis)  
❌ **Advanced search** (full-text, semantic search)  
❌ **File uploads** (images, attachments)  
❌ **Complex permissions** (sharing, team management)  
❌ **Performance optimization** (caching, virtualization)  
❌ **Mobile app** (desktop web only)

---

## Development Priorities

### Phase 1: Foundation (Most Critical)

1. **Authentication setup** - Users can sign up, login, access dashboard
2. **Flexible workspace layout** - Resizable/collapsible panels with state persistence
3. **Project data loading** - Load all documents/tags into client-side index
4. **Basic file tree** - File explorer with project structure

### Phase 2: Core Feature (MVP Differentiator)

5. **@-reference detection** - ProseMirror plugin detects @ character
6. **Client-side autocomplete** - Instant fuzzy search of local project index
7. **Reference insertion** - Custom ProseMirror nodes for references
8. **Tagging system** - Document tags for thematic organization

### Phase 3: Polish & Complete (MVP Ready)

9. **Reference validation** - Integrity checking, broken link detection
10. **File operations** - Create, delete, rename with reference updates
11. **Mock AI panel** - Context display showing current document's story elements

### Success Definition

**MVP is complete when:** A user can create a project, add character and chapter documents, use @-references to link them together, and see the story context in the AI panel - providing a compelling preview of the full platform vision.

---

This MVP delivers the core value proposition of context-aware writing through @-references while building the foundation for future AI and collaboration features. The focus is on proving the concept and validating user demand for the reference system before building more complex features.