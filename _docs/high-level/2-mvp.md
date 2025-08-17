# ShuScribe MVP Complete System Overview

**Context-Aware Fiction Writing Platform - Full MVP Specification**

*How Frontend + Backend Work Together to Deliver the Core @-Reference System*

---

## MVP Vision & Core Value Proposition

### What ShuScribe MVP Delivers
**"Cursor for fiction writing - context-aware assistance through smart references and tagging"**

**Core Innovation:** Like how Cursor understands your codebase, ShuScribe understands your story world through @-references and tags, providing intelligent context within a flexible workspace.

**Target User:** Fiction writers who struggle to keep track of story elements across multiple documents and chapters.

---

## Complete System Architecture

### Technology Stack Overview

**Frontend Architecture**: Next.js 15 with React 19, TypeScript, shadcn/ui components, Tailwind CSS, ProseMirror editor, and TanStack Query for state management.

**Backend Architecture**: FastAPI with Python, SQLAlchemy ORM, Pydantic validation, dependency injection patterns, and integrated reference processing.

**Database & Services**: Supabase PostgreSQL with built-in authentication, real-time capabilities, and file storage.

**Technology Details**: See technical specifications in [`3-frontend.md`](3-frontend.md) and [`4-backend.md`](4-backend.md).

### Data Flow Architecture

**Reference System Flow**: Project data loads once into frontend index → @-character detection triggers client-side search → instant suggestions without API calls → reference insertion and backend extraction on save.

**Performance Strategy**: Local indexing enables <50ms autocomplete responses while backend maintains reference integrity and cross-document relationships.

**Implementation Details**: See data flow patterns in [`3-frontend.md`](3-frontend.md) and API contracts in [`../api/contracts.md`](../api/contracts.md).

---

## Core Feature Set

### 1. Context-Aware Reference + Tagging System (Primary Feature)

**What It Does:**
- **@-References:** Type `@` to link documents: `@characters/protagonists/elara`
- **Tag References:** Link by theme: `@fire-magic` (finds all documents with that tag)
- **Smart Tagging:** Documents can have multiple tags for thematic organization
- **Instant Autocomplete:** Client-side fuzzy search of all project content (no API delay)
- **Visual Context:** See all story elements connected to current document

**User Experience**: Writing `@` triggers instant autocomplete showing character references, tag-based suggestions, and location links with visual icons and tag indicators.

**Reference Types**: File references link directly to character/location documents, while tag references show all documents with thematic connections.

**Technical Implementation**: Frontend builds searchable index from project data, custom ProseMirror plugin provides instant autocomplete, backend handles reference extraction and integrity checking.

**Implementation Files**: See ProseMirror integration in `frontend/src/components/editor/` and reference processing in `backend/src/agents/reference/`.

### 2. Flexible Workspace Layout

**Workspace Layout**: Three-panel VS Code-style interface with file explorer, tabbed editor workspace, and AI assistance panel. All panels are resizable and collapsible with persistent state.

**Layout Components**: File explorer shows hierarchical project structure, editor supports multiple document tabs with @-reference system, AI panel provides context-aware assistance.

**Implementation**: See workspace components in `frontend/src/components/workspace/layout/` and layout patterns in [`../frontend/designs/universal-container-pattern.md`](../frontend/designs/universal-container-pattern.md).

**Panel Features:**
- **Flexible Layout:** All panels resizable with drag handles
- **Collapsible:** File explorer and AI panel can collapse to icons
- **Responsive:** Layout adapts to screen size and user preferences
- **Persistent:** Panel sizes/states saved per user

### 3. Document Management System

**Project Structure**: Hierarchical organization with characters, locations, timeline, and worldbuilding folders. Documents support multiple tags for thematic organization and cross-cutting concerns.

**Organization Philosophy**: Path-based document creation automatically generates folder structure, eliminating manual folder management while maintaining intuitive hierarchy.

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

**Authentication Flow**: Frontend handles Supabase Auth operations, backend validates JWT tokens from Authorization headers, maintaining stateless authentication pattern.

**Document Operations**: Frontend editor auto-saves to backend, backend processes reference extraction and maintains document integrity, database stores rich ProseMirror content.

**Reference System**: Frontend loads complete project data once to build local search index, enabling instant @-reference autocomplete without API calls, while backend validates references on save.

**Integration Details**: See API contracts in [`../api/contracts.md`](../api/contracts.md) and authentication patterns in [`../core/system-architecture.md`](../core/system-architecture.md).

### Database Schema Integration

**Database Schema**: Users own projects containing hierarchical documents with reference relationships. Documents store ProseMirror JSON content with extracted metadata including word counts, tags, and reference mappings.

**Schema Details**: See complete database models in [`../backend/overview.md`](../backend/overview.md) and data relationships in [`../core/system-architecture.md`](../core/system-architecture.md).

---

## Mock AI Integration (Foundation for Future)

### Current MVP Implementation
**Purpose:** Show users what AI features will look like without implementing them

**AI Panel Components:**
- **Mode Selector:** Dropdown with options (Chapter Writing, Character Development, etc.) - non-functional
- **Context Display:** Shows current document's references and story elements
- **Chat Interface:** Placeholder with "Coming Soon" messages
- **Sample Suggestions:** Hardcoded examples of future AI assistance

### Mock AI Integration (Foundation for Future)

**Current Implementation**: AI panel shows interface design with context display and placeholder chat functionality, demonstrating future AI integration patterns.

**API Foundation**: Backend provides context extraction and mock response endpoints, ready for real AI integration with OpenAI/Anthropic services.

**Future Integration**: See AI system architecture in [`../backend/capabilities.md`](../backend/capabilities.md) and context processing in [`../core/system-architecture.md`](../core/system-architecture.md).

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
✅ **AI wiki generation** - One-click wiki from @-references  
✅ **Export capabilities** - Markdown, PDF, EPUB export  
✅ **Basic publishing** - Simple public story pages with wikis  

### What's Explicitly NOT in MVP
❌ **Real-time collaboration** (Y.js, WebSocket, presence)  
❌ **AI chat implementation** (OpenAI/Anthropic integration)  
❌ **Interactive reading** (hover context, AI companion)  
❌ **Advanced search** (full-text, semantic search)  
❌ **File uploads** (images, attachments)  
❌ **Complex permissions** (sharing, team management)  
❌ **Performance optimization** (caching, virtualization)  
❌ **Mobile app** (desktop web only)  
❌ **Multi-content types** (blogs, announcements, etc.)  
❌ **Advanced publishing** (monetization, analytics, community)  

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

### Phase 3: Basic Publishing (Market Validation)
9. **AI wiki generation** - Extract @-references and generate comprehensive wikis
10. **Export system** - Generate Markdown, PDF, EPUB from ProseMirror content
11. **Simple publishing** - Public story pages with integrated wiki access
12. **Reference validation** - Integrity checking, broken link detection

### Phase 4: Polish & Complete (MVP Ready)
13. **File operations** - Create, delete, rename with reference updates
14. **Mock AI panel** - Context display showing current document's story elements
15. **Publishing workflows** - Simple publishing wizard and management

### Success Definition
**MVP is complete when:** A user can create a project, add character and chapter documents, use @-references to link them together, generate an AI wiki from those references, and publish their story with the wiki - proving the core value proposition of automatic universe creation from natural writing.

---

This MVP delivers the complete core value proposition: context-aware writing through @-references combined with automatic wiki generation and basic publishing capabilities. By including basic publishing, the MVP proves the full concept that sets ShuScribe apart - the ability to create comprehensive story universes automatically from natural writing workflow. The focus remains on validating the @-reference system while demonstrating the platform's unique wiki generation capabilities that will drive the larger universe management vision.