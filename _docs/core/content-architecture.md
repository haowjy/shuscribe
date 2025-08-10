# ShuScribe Content Architecture

**Current Implementation - Fantasy Writing Platform**

*Database models, relationships, and data flow for universe content management*

---

## Architecture Overview

### **Current Implementation Philosophy**

ShuScribe's content architecture is designed around **hierarchical project organization** with **rich document management**, **flexible tagging**, and **AI-powered features**. The system supports fantasy writers with complex worldbuilding needs while maintaining clean data relationships and extensibility.

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTENT ARCHITECTURE LAYERS                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🎯 PROJECT LAYER                                               │
│  ─────────────────                                              │
│  Project Container → Hierarchical File Tree → Document Storage  │
│                                                                 │
│  📝 CONTENT LAYER                                               │
│  ─────────────────                                              │
│  ProseMirror Documents → Word Count Tracking → Version Control  │
│                                                                 │
│  🏷️ ORGANIZATION LAYER                                          │
│  ──────────────────────                                         │
│  Many-to-Many Tags → Categories → Usage Tracking → Search       │
│                                                                 │
│  🤖 AI LAYER                                                    │
│  ────────────                                                   │
│  LLM Integration → WikiGen Agents → Spoiler Prevention          │
│                                                                 │
│  💾 DATA LAYER                                                  │
│  ─────────────                                                  │
│  PostgreSQL → SQLAlchemy ORM → Repository Pattern → Multi-Backend│
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Data Models

### **Project Model**

**The universe container for all content and organization**

```python
class Project(Base):
    # Identity
    id: str (UUID)
    title: str
    description: str
    
    # Ownership & Collaboration
    owner_id: str (user)
    created_by: str (user)
    updated_by: str (user)
    collaborators: List[Dict] (JSON)
    
    # Metrics (auto-calculated)
    word_count: int
    document_count: int
    
    # Configuration
    settings: Dict (JSON)
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    documents: List[Document]            # One-to-many
    file_tree_items: List[FileTreeItem]  # One-to-many
    tags: List[Tag]                      # Many-to-many
```

**Project Features:**
- **Universe Container**: Single project contains all documents, characters, locations, etc.
- **Collaboration Support**: JSON-based collaborator system with roles
- **Auto-calculated Metrics**: Word count and document count maintained automatically
- **Flexible Settings**: JSON settings for project-specific configuration

### **Document Model**

**Rich content storage with ProseMirror JSON support**

```python
class Document(Base):
    # Identity
    id: str (UUID)
    project_id: str (FK to Project)
    title: str
    path: str (hierarchical path)
    
    # Content (ProseMirror JSON)
    content: Dict (JSON)
    word_count: int (auto-calculated)
    version: str
    
    # Edit Control
    is_locked: bool
    locked_by: str (user)
    
    # File Tree Integration
    file_tree_id: str (optional FK to FileTreeItem)
    
    # User Tracking
    created_by: str (user)
    updated_by: str (user)
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    project: Project                     # Many-to-one
    file_tree_item: FileTreeItem         # One-to-one (optional)
    tags: List[Tag]                      # Many-to-many
```

**Document Features:**
- **ProseMirror Support**: Full rich text JSON content preservation
- **Word Count Automation**: Extracted from ProseMirror content on save
- **Version Tracking**: Version strings for draft management
- **Locking Mechanism**: Basic edit conflict prevention
- **File Tree Integration**: Optional linking to hierarchical organization

### **FileTreeItem Model**

**Hierarchical organization system supporting folders and files**

```python
class FileTreeItem(Base):
    # Identity
    id: str (UUID)
    project_id: str (FK to Project)
    name: str
    type: str ("file" | "folder")
    path: str (full hierarchical path)
    
    # Hierarchy
    parent_id: str (self-referential FK)
    
    # File Properties (for type="file")
    document_id: str (FK to Document)
    word_count: int
    
    # Display
    icon: str
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    project: Project                     # Many-to-one
    parent: FileTreeItem                 # Self-referential
    children: List[FileTreeItem]         # Self-referential
    document: Document                   # One-to-one (for files)
    tags: List[Tag]                      # Many-to-many
```

**FileTreeItem Features:**
- **Hierarchical Structure**: Self-referential parent/child relationships
- **File/Folder Support**: Type constraints ensure proper document linking
- **Path Management**: Full hierarchical paths for navigation
- **Tag Integration**: Files and folders can be tagged for organization

### **Tag Model**

**Flexible tagging system with categories, colors, and usage tracking**

```python
class Tag(Base):
    # Identity
    id: str (UUID)
    name: str
    
    # Visual & Categorization
    icon: str
    color: str (hex color code)
    description: str
    category: str ("character", "location", "magic-system", etc.)
    
    # Scope
    project_id: str (FK to Project)
    
    # Metadata
    is_system: bool (system-generated)
    is_archived: bool (soft delete)
    usage_count: int (auto-maintained)
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Many-to-Many Relationships
    projects: List[Project]
    documents: List[Document]
    file_tree_items: List[FileTreeItem]
```

**Tag Features:**
- **Project-Scoped**: Tags belong to specific projects
- **Visual Organization**: Icons and colors for visual categorization
- **Category Support**: Flexible categorization (character, location, etc.)
- **Usage Tracking**: Automatic usage count maintenance
- **Many-to-Many**: Tags can be applied to projects, documents, and file tree items

---

## Entity Relationships & Architecture Concepts

### **Understanding Files, Folders, and Documents**

ShuScribe uses a **three-entity architecture** that separates content organization from content storage. This design provides flexibility and clear separation of concerns.

#### **The Three Core Entities**

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   FOLDER        │    │      FILE        │    │    DOCUMENT      │
│ (FileTreeItem)  │    │  (FileTreeItem)  │    │                  │
├─────────────────┤    ├──────────────────┤    ├──────────────────┤
│ • Organization  │    │ • Organization   │◄──┤ • Actual Content │
│ • No content    │    │ • Links to doc   │    │ • ProseMirror    │
│ • Contains:     │    │ • Has:           │    │ • Word count     │
│   - Subfolders  │    │   - document_id  │    │ • Rich text      │
│   - Files       │    │   - Path/name    │    │ • @-references   │
│ • document_id   │    │   - Tags/icon    │    │ • Version info   │
│   = null        │    │   - Metadata     │    │                  │
└─────────────────┘    └──────────────────┘    └──────────────────┘
```

#### **Key Relationships**

1. **Folder → Files**: Contains zero or more files and subfolders
2. **File → Document**: Has exactly one linked document (`document_id`)
3. **Document ← File**: Can be linked from exactly one file (optional `file_tree_id`)

#### **Database Constraints**

```sql
-- Ensures data integrity
CHECK ((type = 'file' AND document_id IS NOT NULL) OR 
       (type = 'folder' AND document_id IS NULL))
```

### **Real-World Example**

Let's trace through creating a character document:

#### **User Action**: Create document at `/characters/protagonists/aria`

```json
POST /projects/proj_123/documents
{
  "title": "Aria - Fire Mage",
  "path": "/characters/protagonists/aria"
}
```

#### **What Happens Behind the Scenes**:

**Step 1: Auto-create folder hierarchy**
```json
// Create folder: /characters (if doesn't exist)
{
  "id": "ft_001",
  "name": "characters", 
  "type": "folder",
  "path": "/characters",
  "parent_id": null,
  "document_id": null  // ← No linked document
}

// Create folder: /characters/protagonists (if doesn't exist)  
{
  "id": "ft_002",
  "name": "protagonists",
  "type": "folder", 
  "path": "/characters/protagonists",
  "parent_id": "ft_001",
  "document_id": null  // ← No linked document
}
```

**Step 2: Create the actual document**
```json
{
  "id": "doc_456",
  "title": "Aria - Fire Mage",
  "path": "/characters/protagonists/aria",
  "content": {
    "type": "doc",
    "content": []  // Empty initially
  },
  "word_count": 0,
  "file_tree_id": "ft_003"  // ← Links to file tree item
}
```

**Step 3: Create file tree item linking to document**
```json
{
  "id": "ft_003", 
  "name": "aria",
  "type": "file",  // ← This is a FILE
  "path": "/characters/protagonists/aria",
  "parent_id": "ft_002",
  "document_id": "doc_456"  // ← Links to document content
}
```

#### **Final File Tree Structure**:

```
📁 characters/               (folder, no content)
  📁 protagonists/           (folder, no content)  
    📄 aria                  (file, links to doc_456)
```

#### **What User Sees**:

- **File Explorer**: Hierarchical folder structure with the "aria" file
- **Document Editor**: Rich text content when clicking on "aria" file
- **Clean Separation**: Organization (file tree) vs content (document)

### **Benefits of This Architecture**

1. **Flexible Organization**: Move files without affecting content
2. **Performance**: File tree loads quickly without heavy document content  
3. **Clean APIs**: Separate endpoints for organization vs content management
4. **Path-Based Creation**: Automatic folder hierarchy from document paths
5. **Independent Operations**: 
   - Rename files without changing document titles
   - Move files without copying large content
   - Tag files and folders independently

### **Quick Reference Table**

| Aspect | **Folder** (FileTreeItem) | **File** (FileTreeItem) | **Document** |
|--------|---------------------------|-------------------------|--------------|
| **Purpose** | Organization container | Organization + link | Actual content |
| **Contains** | Child folders/files | Link to document | Rich text content |
| **User sees** | 📁 In file tree | 📄 In file tree | 📝 In editor |
| **Can edit** | Name, move, tags | Name, move, tags | Title, content |
| **Has content** | ❌ No | ❌ No | ✅ Yes (ProseMirror) |
| **document_id** | `null` | Points to document | N/A |
| **file_tree_id** | N/A | N/A | Points to file (optional) |
| **Database type** | `type: "folder"` | `type: "file"` | Documents table |
| **Word count** | 0 | Mirrors document | Calculated from content |
| **API endpoints** | `/file-tree` | `/file-tree` | `/documents` |
| **When created** | Manual or auto-path | Auto with document | User creates |
| **Performance** | Fast (no content) | Fast (no content) | Heavy (rich content) |

### **Entity Type Quick Check**

```javascript
// Quick identification logic
if (item.type === "folder") {
  // It's a folder - no content, just organization
  console.log("📁 Folder:", item.name);
  console.log("Contains:", item.children?.length || 0, "items");
}

if (item.type === "file" && item.document_id) {
  // It's a file - links to actual content
  console.log("📄 File:", item.name);
  console.log("Content in document:", item.document_id);
}

if (document.id && document.content) {
  // It's a document - contains the actual content
  console.log("📝 Document:", document.title);
  console.log("Word count:", document.word_count);
}
```

### **Common Workflows**

#### **Creating Content**:
1. User creates document with path → Auto-creates folders + file + document
2. User can then edit document content independently
3. User can move file in tree without affecting document content

#### **Organizing Content**:
1. User can create folders manually for organization
2. User can move files between folders
3. User can apply tags to both files and folders
4. File tree operations are fast (no large content to move)

#### **Editing Content**:
1. User clicks file in tree → Opens linked document for editing
2. Document operations (save, edit) are independent of file tree
3. Word count updates flow from document → file tree item

---

## Database Schema & Relationships

### **Core Tables**

```sql
-- Projects table
CREATE TABLE projects (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    owner_id VARCHAR(36),
    created_by VARCHAR(36),
    updated_by VARCHAR(36),
    word_count INTEGER NOT NULL DEFAULT 0,
    document_count INTEGER NOT NULL DEFAULT 0,
    collaborators JSON NOT NULL DEFAULT ('[]'),
    settings JSON NOT NULL DEFAULT ('{}'),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- Documents table
CREATE TABLE documents (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    path VARCHAR(500) NOT NULL,
    created_by VARCHAR(36),
    updated_by VARCHAR(36),
    content JSON NOT NULL DEFAULT ('{}'),
    word_count INTEGER NOT NULL DEFAULT 0,
    version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    is_locked BOOLEAN NOT NULL DEFAULT FALSE,
    locked_by VARCHAR(255),
    file_tree_id VARCHAR(36),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (file_tree_id) REFERENCES file_tree_items(id)
);

-- File tree items table
CREATE TABLE file_tree_items (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('file', 'folder')),
    path VARCHAR(500) NOT NULL,
    parent_id VARCHAR(36),
    document_id VARCHAR(36),
    icon VARCHAR(50),
    word_count INTEGER,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES file_tree_items(id),
    CHECK ((type = 'file' AND document_id IS NOT NULL) OR 
           (type = 'folder' AND document_id IS NULL))
);

-- Tags table
CREATE TABLE tags (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    icon VARCHAR(50),
    color VARCHAR(7),
    description TEXT,
    category VARCHAR(100),
    project_id VARCHAR(36) NOT NULL,
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    usage_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

### **Junction Tables for Many-to-Many Relationships**

```sql
-- Project-Tag relationships
CREATE TABLE project_tags (
    project_id VARCHAR(36) NOT NULL,
    tag_id VARCHAR(36) NOT NULL,
    PRIMARY KEY (project_id, tag_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Document-Tag relationships
CREATE TABLE document_tags (
    document_id VARCHAR(36) NOT NULL,
    tag_id VARCHAR(36) NOT NULL,
    PRIMARY KEY (document_id, tag_id),
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- FileTreeItem-Tag relationships
CREATE TABLE file_tree_item_tags (
    file_tree_item_id VARCHAR(36) NOT NULL,
    tag_id VARCHAR(36) NOT NULL,
    PRIMARY KEY (file_tree_item_id, tag_id),
    FOREIGN KEY (file_tree_item_id) REFERENCES file_tree_items(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
```

### **Key Relationships**

**One-to-Many Relationships:**
- Project → Documents
- Project → FileTreeItems  
- Project → Tags
- FileTreeItem → FileTreeItem (parent/children)

**One-to-One Relationships:**
- Document ↔ FileTreeItem (optional)

**Many-to-Many Relationships:**
- Projects ↔ Tags
- Documents ↔ Tags
- FileTreeItems ↔ Tags

**Referential Integrity:**
- Cascade deletes maintain data consistency
- Check constraints ensure proper file/folder behavior
- Foreign key constraints prevent orphaned records

---

## Content Processing & Features

### **ProseMirror Content Handling**

**Content Structure:**
```python
interface ProseMirrorContent {
    type: "doc"
    content: ProseMirrorNode[]
}

interface ProseMirrorNode {
    type: string
    text?: string
    content?: ProseMirrorNode[]
    attrs?: Record<string, any>
    marks?: ProseMirrorMark[]
}
```

**Word Count Calculation:**
```python
def calculate_word_count(content: DocumentContent) -> int:
    """Extract text from ProseMirror JSON and count words"""
    def extract_text(node: Dict[str, Any]) -> str:
        text = ""
        if "text" in node:
            text += node["text"]
        if "content" in node and isinstance(node["content"], list):
            for child in node["content"]:
                child_text = extract_text(child)
                if child_text:
                    text += " " + child_text if text else child_text
        return text
    
    # Extract all text and count words
    full_text = ""
    for node in content.content:
        extracted = extract_text(node)
        if extracted:
            full_text += " " + extracted if full_text else extracted
    
    words = [word.strip() for word in full_text.split() if word.strip()]
    return len(words)
```

**Content Features:**
- **Rich Text Preservation**: Full ProseMirror JSON structure maintained
- **Automatic Word Counting**: Real-time calculation from content
- **Extensible Format**: ProseMirror supports custom node types for @-references
- **Version Tracking**: Content versioning for draft management

### **Tag System Features**

**Tag Categories for Fantasy Writing:**
```python
# Common tag categories for fantasy projects
TAG_CATEGORIES = {
    "character": {"icon": "user", "color": "#3b82f6"},
    "location": {"icon": "map-pin", "color": "#10b981"},  
    "magic-system": {"icon": "sparkles", "color": "#8b5cf6"},
    "timeline": {"icon": "clock", "color": "#f59e0b"},
    "organization": {"icon": "shield", "color": "#ef4444"},
    "artifact": {"icon": "gem", "color": "#6366f1"},
    "concept": {"icon": "lightbulb", "color": "#84cc16"},
    "chapter": {"icon": "book-open", "color": "#06b6d4"}
}
```

**Tag Operations:**
- **Assignment/Unassignment**: Proper relationship management
- **Usage Tracking**: Automatic increment/decrement of usage counts
- **Search & Filter**: Category-based filtering and search
- **Color Coding**: Visual organization with hex colors
- **Icon Support**: Visual identification with icon names

---

## API Architecture

### **Current API Endpoints**

**Projects API:**
```http
GET    /api/v1/projects                    # List projects with pagination
GET    /api/v1/projects/{id}               # Get project details
POST   /api/v1/projects                    # Create project
PUT    /api/v1/projects/{id}               # Update project
DELETE /api/v1/projects/{id}               # Delete project
GET    /api/v1/projects/{id}/file-tree     # Get hierarchical file tree
```

**Documents API:**
```http
GET    /api/v1/documents/{id}              # Get document with content
POST   /api/v1/documents                   # Create document
PUT    /api/v1/documents/{id}              # Update document content
DELETE /api/v1/documents/{id}              # Delete document
```

**Tags API:**
```http
GET    /api/v1/projects/{id}/tags          # List project tags
POST   /api/v1/projects/{id}/tags          # Create tag
PUT    /api/v1/projects/{id}/tags/{id}     # Update tag
DELETE /api/v1/projects/{id}/tags/{id}     # Delete tag
POST   /api/v1/projects/{id}/tags/{id}/assign    # Assign tag to file
DELETE /api/v1/projects/{id}/tags/{id}/assign    # Unassign tag from file
GET    /api/v1/projects/{id}/tags/search   # Search tags
GET    /api/v1/projects/{id}/tags/stats    # Tag statistics
```

**LLM Integration API:**
```http
POST   /api/v1/llm/chat                    # LLM chat completion
POST   /api/v1/llm/validate-key            # Validate API key
POST   /api/v1/llm/store-key               # Store encrypted API key
DELETE /api/v1/llm/keys/{provider}         # Delete API key
GET    /api/v1/llm/keys                    # List stored keys
GET    /api/v1/llm/providers               # List LLM providers
GET    /api/v1/llm/models                  # List available models
```

### **Response Format**

**All responses use consistent ApiResponse wrapper:**
```typescript
interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  message: string | null;
  status: number;
}
```

---

## Fantasy Writing Support

### **Current Backend Capabilities for Fantasy Writing**

**✅ Hierarchical Organization:**
- File tree structure supports Characters/, Locations/, Chapters/, Magic/ organization
- Parent/child relationships for nested categorization
- Document-to-file-tree linking for integrated navigation

**✅ Rich Content Management:**
- ProseMirror JSON content preserves formatting and structure
- Automatic word count tracking for writing goals
- Version control and edit locking for draft management

**✅ Flexible Tagging System:**
- Category-based tag organization (character, location, magic-system)
- Color-coded and icon-based visual organization
- Many-to-many relationships allow complex cross-references
- Usage tracking shows most important elements

**✅ AI Integration Foundation:**
- LLM API integration with multiple providers
- WikiGen agent system for automated worldbuilding
- Encrypted API key storage for security

**❌ Missing Frontend Features:**
- **@-Reference System**: Parsing `@character/Aragorn` syntax in editor
- **Cross-Reference Navigation**: Click-to-navigate between documents
- **Reference Validation**: Checking if `@location/Rivendell` exists
- **Timeline Management**: Chronological event organization
- **Relationship Mapping**: Visual connections between entities

### **Foundation for @-Reference System**

**Backend provides excellent foundation:**

**Data Structure Support:**
- File tree paths can serve as reference targets (`/characters/aragorn`)
- ProseMirror JSON can store custom node types for references
- Tag system can categorize reference types
- Document relationships can track dependencies

**API Capabilities:**
- Complete project data loading for building reference indexes
- Document CRUD operations for reference updates
- Search capabilities for reference autocomplete
- Tag assignment for categorizing referenced entities

**Implementation Strategy for Frontend:**
1. **Parse References**: Extract `@character/aragorn` from ProseMirror content
2. **Build Index**: Use project data API to create reference lookup table  
3. **Validate References**: Check if target paths exist in file tree
4. **Link Navigation**: Implement click-to-navigate using document IDs
5. **Autocomplete**: Use tag and file tree data for suggestion system

---

## Scalability & Performance

### **Current Architecture Benefits**

**Repository Pattern:**
- Clean separation allows easy backend swapping
- Memory backend provides complete test isolation
- Interface-based design supports future optimizations

**Database Design:**
- Proper foreign keys with cascade deletes
- Indexes on commonly queried fields
- JSON fields for flexible configuration without schema changes

**API Design:**
- Pagination support for large datasets
- Efficient relationship loading with SQLAlchemy
- Consistent error handling and response formats

### **Future Scalability Considerations**

**Database Optimizations:**
- Read replicas for content queries
- Partitioning by project for large installations
- Full-text search indexes for content search
- Caching layer for frequently accessed data

**Content Delivery:**
- CDN support for published content
- Export service for multiple formats
- Background processing for heavy operations
- Real-time collaboration with WebSocket support

**AI Integration:**
- Batch processing for wiki generation
- Streaming responses for chat interfaces
- Rate limiting and quota management
- Model switching based on task requirements

---

## Security & Data Protection

### **Current Security Features**

**Authentication:**
- Supabase JWT validation
- Environment-based user filtering
- Role-based access through collaborators

**Data Protection:**
- Encrypted API key storage (Fernet encryption)
- Input validation through Pydantic models
- SQL injection prevention through SQLAlchemy ORM
- Path sanitization for file operations

### **Enterprise Security Readiness**

**Access Control:**
- Project-level ownership and collaboration
- Tag-level permissions for sensitive content
- Document locking for edit conflicts

**Data Compliance:**
- User ownership tracking on all content
- Soft delete capability (tag archiving)
- Export capabilities for data portability
- Audit trail through created_by/updated_by fields

---

This content architecture provides a solid foundation for fantasy writing with comprehensive worldbuilding support. The current backend implementation covers all essential data management needs, with clear pathways for implementing the @-reference system and other advanced features in the frontend.