# ShuScribe Frontend Development TODO

**MVP Priority Tasks - Context-Aware Fiction Writing Platform**

*Based on comprehensive implementation status analysis - Updated January 2025*

---

## 🚨 CRITICAL MVP BLOCKERS (Must Complete for Launch)

### @-Reference System Implementation (HIGHEST PRIORITY)
- [ ] **ProseMirror Plugin Development** - Create plugin to detect `@` character input
- [ ] **Local Project Index** - Build searchable index from all project documents and tags
- [ ] **Fuzzy Search Algorithm** - Client-side instant search (<50ms response time)
- [ ] **Reference Node Type** - Custom ProseMirror nodes for `@characters/elara` syntax
- [ ] **Tag System Integration** - Support `@fire-magic` tag references
- [ ] **Reference Autocomplete UI** - Dropdown with instant suggestions
- [ ] **Reference Navigation** - Click references to open linked documents
- [ ] **Reference Validation** - Detect and highlight broken references
- [ ] **Reference Integrity** - Update references when files are renamed/moved

#### Tag Reference System Architecture (CRITICAL DESIGN DECISIONS)
- [ ] **Reference Type System** - Design discriminated union for file/folder/tag references
- [ ] **Multi-Target Resolution** - Handle tags that match multiple files/folders
- [ ] **Reference Handler Separation** - Separate handlers for file/folder/tag clicks
- [ ] **Disambiguation UI** - Interface for when tag matches multiple items
- [ ] **Tag View Implementation** - Virtual view showing all items with specific tag

**⚠️ Tag Reference Complications Identified:**
- Current `@elara` (file) vs `@characters` (folder) vs `@fire-magic` (tag) all use same syntax
- Tag references can match multiple items (many files with "fire-magic" tag)
- Editor `handleOpenFile(id)` assumes 1:1 ID-to-item mapping, breaks with tags
- Need architectural changes: `ReferenceType = file | folder | tag`
- Current `findItemById` decision supports file/folder, sets foundation for tags

### Backend API Integration (CRITICAL)
- [ ] **FastAPI Client Setup** - Create API client with authentication headers
- [ ] **Project Data Loading** - `GET /projects/{id}/data` endpoint integration
- [ ] **Document CRUD Operations** - Create, read, update, delete documents
- [ ] **Reference Extraction API** - Backend processing of @-references
- [ ] **Authentication Flow** - Complete Supabase auth integration
- [ ] **Error Handling** - Comprehensive API error states and retry logic

### File Operations (BLOCKING BASIC USAGE)
- [ ] **Document Creation** - Create new documents with templates
- [ ] **Folder Management** - Create, rename, delete folders
- [ ] **Document Deletion** - Delete with reference dependency checking
- [ ] **File Renaming** - Rename with automatic reference updates
- [ ] **Import Documents** - Upload and import existing documents

---

## 🟡 HIGH PRIORITY (MVP Polish)

### User Experience Improvements
- [ ] **Loading States** - Comprehensive loading indicators throughout app
- [ ] **Error Boundaries** - Graceful error handling for component failures
- [ ] **Keyboard Shortcuts** - Essential shortcuts for power users
- [ ] **Search Functionality** - Global project search across documents
- [ ] **Recent Files** - Quick access to recently opened documents

### Authentication & User Management
- [ ] **OAuth Callback Handling** - Complete Google OAuth flow
- [ ] **Email Verification** - User registration with email confirmation
- [ ] **Password Reset** - Forgot password functionality
- [ ] **User Profile Management** - Basic profile settings
- [ ] **Session Management** - Proper token refresh and logout

### Project Management
- [ ] **Project Creation Wizard** - Guided project setup with templates
- [ ] **Project Settings** - Basic project configuration options
- [ ] **Project Deletion** - Safe project removal with confirmations
- [ ] **Project Sharing** - Basic collaboration setup (future-ready)

---

## 📝 COMPLETED FEATURES ✅

### Core Infrastructure
- [x] **Three-panel workspace layout** with resizable panels
- [x] **Tiptap editor integration** with rich text formatting
- [x] **Tab management system** with drag-and-drop reordering
- [x] **Component library** using shadcn/ui
- [x] **Design system** with Tailwind CSS v4
- [x] **State management** with TanStack Query setup
- [x] **Auto-save system** with localStorage persistence

### UI Components
- [x] **File explorer structure** with hierarchical tree view
- [x] **Context menus** for file operations (UI only)
- [x] **Mock AI panel** with mode selection and context display
- [x] **Responsive design** for different screen sizes
- [x] **Dark/light theme support** with CSS custom properties

### Editor Features
- [x] **Rich text formatting** (bold, italic, headings, lists, etc.)
- [x] **Code blocks** with syntax highlighting
- [x] **Character/word counting** in status bar
- [x] **Draft management** with auto-save
- [x] **Multiple editor variants** (rich, basic, minimal)

---

## 🔮 FUTURE ENHANCEMENTS (Post-MVP)

### Advanced @-Reference Features
- [ ] **Reference Analytics** - Show reference usage statistics
- [ ] **Smart Reference Suggestions** - AI-powered reference recommendations
- [ ] **Reference Visualization** - Graph view of story element connections
- [ ] **Bulk Reference Operations** - Mass update/rename references

### Real AI Integration
- [ ] **OpenAI/Anthropic Integration** - Replace mock AI with real functionality
- [ ] **Context-Aware Writing Assistance** - AI suggestions based on story context
- [ ] **Character Development AI** - AI help with character consistency
- [ ] **Plot Analysis** - AI-powered story structure analysis

### Collaboration Features
- [ ] **Real-time Collaborative Editing** - Multiple users editing simultaneously
- [ ] **Comment System** - Inline comments and suggestions
- [ ] **Version History** - Track document changes over time
- [ ] **Team Management** - User roles and permissions

### Advanced File Management
- [ ] **Advanced Search** - Full-text search with filters
- [ ] **File Templates** - Rich document templates for characters, locations, etc.
- [ ] **Import/Export** - Various file format support
- [ ] **File Versioning** - Track document revision history

### Performance & Quality
- [ ] **Virtual Scrolling** - Handle large file trees efficiently
- [ ] **Code Splitting** - Optimize bundle size for editor extensions
- [ ] **Comprehensive Testing** - Unit, integration, and E2E tests
- [ ] **Accessibility** - Full ARIA support and keyboard navigation

### Writer-Specific Features
- [ ] **Writing Statistics** - Daily writing goals and progress tracking
- [ ] **Focus Mode** - Distraction-free writing environment
- [ ] **Outline View** - Document structure navigation
- [ ] **Writing Analytics** - Patterns and productivity insights
- [ ] **Export to Publishing Formats** - EPUB, PDF, etc.

---

## 🎯 CURRENT SPRINT FOCUS

**Week 1-2: @-Reference System Foundation**
1. Implement ProseMirror plugin for @ detection
2. Build local project index and fuzzy search
3. Create reference autocomplete UI
4. Test reference insertion and navigation

**Week 3-4: Backend Integration**
1. Connect to FastAPI endpoints
2. Implement project data loading
3. Complete authentication flows
4. Add basic file operations

**Week 5-6: MVP Polish**
1. Add comprehensive error handling
2. Implement search functionality
3. Polish user experience
4. Prepare for beta testing

---

## 📊 SUCCESS METRICS

### MVP Launch Criteria
- [ ] Users can create projects with @-references
- [ ] @-reference autocomplete works with <50ms response time
- [ ] Documents save and load reliably
- [ ] File operations work without data loss
- [ ] Authentication flows are secure and functional

### User Engagement Targets
- **@-references per session:** >10 (core feature adoption)
- **Documents per project:** >5 (comprehensive story building)
- **Reference navigation clicks:** >5 per session (exploring connections)
- **Session duration:** >20 minutes (productive writing time)

---

*This TODO list prioritizes the core @-reference system that makes ShuScribe unique, while maintaining the excellent UI foundation already built. Focus on MVP completion before adding advanced features.*