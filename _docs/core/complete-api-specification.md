# ShuScribe Complete API Specification

**Universe Content Management Platform - Complete Endpoint Reference**

*Last Updated: August 2025 - Added Always-Fork Tag System & Path-Based Document Creation*

---

## Table of Contents

1. [API Overview](#api-overview)
2. [Breaking Changes](#️-breaking-changes)
3. [Path Validation & Security](#path-validation--security)
4. [Authentication](#authentication)
5. [Currently Implemented Endpoints](#currently-implemented-endpoints)
6. [Missing Endpoints (Roadmap)](#missing-endpoints-roadmap)
7. [Integration Patterns](#integration-patterns)
8. [Testing Guidelines](#testing-guidelines)

---

## API Override

### Base Configuration
- **Base URL**: `https://api.shuscribe.com/api/v1` (production) or `http://localhost:8000/api/v1` (development)
- **Content Type**: `application/json`
- **Authentication**: Bearer tokens (Supabase JWT)
- **Response Format**: Consistent `ApiResponse<T>` wrapper

### Core Principles
- **Frontend-First Design**: API matches frontend TypeScript interfaces
- **Domain-Driven**: Clean separation between domain models and persistence
- **Rich Content Support**: ProseMirror JSON for documents with text, images, formatting
- **Offline-First**: LocalStorage + TanStack Query for offline functionality
- **Path-Based Organization**: Automatic folder creation from document paths eliminates manual folder management

---

## ⚠️ Breaking Changes

### August 2025: Always-Fork Tag System & Path-Based Document Creation

**BREAKING CHANGES**:
1. **Tag Forking**: All global tags are now automatically forked when added to projects
2. **Document Creation**: Removed `file_tree_parent_id` field from document creation API

**What Changed:**

**Tag System Changes:**
- **Always Fork**: Global tags are automatically forked when added to projects (no conditional logic)
- **Project Ownership**: All project tags are project-specific copies, never references to global tags
- **Customization Freedom**: Users can modify any project tag without affecting other projects
- **Simplified Logic**: Eliminates complex conditional forking decisions

**Document System Changes:**
- **Field Removed**: `file_tree_parent_id` no longer accepted in `POST /documents` requests
- **Auto-Folder Creation**: Parent folders are now automatically created from the document path
- **Simplified API**: Eliminates redundant field and manual folder management
- **Enhanced UX**: Users can create complex folder hierarchies in a single API call

**Migration Guide:**

**Tag System:**
```json
// OLD: Conditional forking behavior (no longer used)
// Global tags were only forked when customizations detected

// NEW: Always-fork behavior
{
  "title": "My Story",
  "tags": [
    {"id": "temp", "name": "fantasy", "icon": "⚔️", "color": "#red"},  // Always forks global "fantasy"
    {"id": "temp", "name": "adventure"}                                    // Creates new if no global exists
  ]
}
// Result: All tags become project-specific, customizable without conflicts
```

**Document System:**
```json
// OLD (no longer supported)
{
  "path": "/characters/protagonist",
  "file_tree_parent_id": "folder_123"  // ❌ REMOVED
}

// NEW (automatic folder creation)
{
  "path": "/characters/protagonists/protagonist"  // ✅ Auto-creates folders
}
```

**Benefits:**

**Tag System:**
- **Clean Ownership**: All project tags are project-specific (no shared references)
- **Customization Freedom**: Modify any tag without affecting other projects
- **Predictable Behavior**: Always-fork eliminates conditional complexity
- **Simplified Logic**: Easier to understand and implement

**Document System:**
- **Intuitive**: Path-based organization matches file system expectations
- **Robust**: Comprehensive path validation and normalization
- **Efficient**: Single API call creates entire folder hierarchy
- **Consistent**: Eliminates potential conflicts between path and parent_id

---

## Path Validation & Security

### Path Normalization Rules
- **Leading slash**: All paths normalized to start with `/`
- **Double slashes**: `//` sequences replaced with single `/`  
- **Trailing slashes**: Removed for consistency
- **Case preservation**: Original casing maintained
- **Length limits**: Individual path segments limited to 100 characters

### Path Validation
- **Security**: Prevents directory traversal attacks (`../` sequences rejected)
- **Characters**: Alphanumeric, hyphens, underscores, and forward slashes allowed
- **Structure**: Must be valid hierarchical path format
- **Empty paths**: Rejected with validation error

### Examples
```json
// Valid paths
"/characters/protagonists/aria"          // ✅
"/world/locations/cities/windmere"       // ✅
"/chapters/act-1/chapter-01"             // ✅

// Invalid paths (rejected)
"/characters/../secrets"                  // ❌ Directory traversal
""                                       // ❌ Empty path
"/characters//double-slash"               // ❌ Normalized to single slash
```

---

## Authentication

### Authentication Strategy
- **Frontend**: Handles all auth via Supabase Auth (OAuth, email/password)
- **Backend**: Validates Supabase JWT tokens from `Authorization: Bearer <token>`
- **User Context**: Endpoints receive validated user ID from token

### Headers Required
```http
Authorization: Bearer <supabase_jwt_token>
Content-Type: application/json
```

---

## Currently Implemented Endpoints

### 1. Health & System Status

#### GET `/health/ping`
Simple health check endpoint.

**Response:**
```json
{
  "message": "pong"
}
```

#### GET `/health/status`
Detailed system status with database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "service": "shuscribe-api",
  "version": "0.1.0",
  "database": "healthy (memory mode)",
  "database_type": "memory",
  "configured_backend": "memory",
  "timestamp": "2025-08-03T20:30:00Z"
}
```

---

### 2. Project Management

#### GET `/projects`
List all projects with pagination and filtering.

**Query Parameters:**
- `limit` (int, 1-100): Number of projects to return (default: 20)
- `offset` (int, ≥0): Number of projects to skip (default: 0)
- `sort` (string): Field to sort by - `title|created_at|updated_at` (default: `updated_at`)
- `order` (string): Sort order - `asc|desc` (default: `desc`)

**Response:**
```json
{
  "data": [
    {
      "id": "proj_123",
      "title": "My Fantasy Novel", 
      "description": "Epic fantasy story",
      "word_count": 15420,
      "document_count": 8,
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-08-03T15:30:00Z",
      "tags": [
        {"id": "fantasy", "name": "Fantasy", "icon": "🏰", "color": "#8B5CF6"}
      ],
      "collaborators": [
        {"user_id": "user_456", "role": "owner", "name": "John Doe", "avatar": "https://..."}
      ]
    }
  ],
  "pagination": {
    "total": 3,
    "limit": 20,
    "offset": 0,
    "has_more": false,
    "next_offset": null
  }
}
```

#### GET `/projects/{project_id}`
Get detailed project information.

**Response:**
```json
{
  "id": "proj_123",
  "title": "My Fantasy Novel",
  "description": "Epic fantasy story with magic and dragons",
  "word_count": 15420,
  "document_count": 8,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-08-03T15:30:00Z",
  "tags": [
    {"id": "fantasy", "name": "Fantasy", "icon": "🏰", "color": "#8B5CF6"}
  ],
  "collaborators": [
    {"user_id": "user_456", "role": "owner", "name": "John Doe", "avatar": "https://..."}
  ],
  "settings": {
    "auto_save_interval": 30000,
    "word_count_target": 80000,
    "backup_enabled": true
  }
}
```

#### POST `/projects`
Create a new project.

**Request:**
```json
{
  "title": "My New Novel",
  "description": "A thrilling adventure story",
  "tags": [
    {"id": "temp-1", "name": "fantasy", "icon": "🧙", "color": "#8B5CF6"},     // Forks global "fantasy" with custom icon
    {"id": "temp-2", "name": "adventure", "icon": "⚔️", "color": "#F59E0B"},  // Creates new "adventure" tag
    {"id": "temp-3", "name": "epic"}                                            // Creates new "epic" tag (no customizations)
  ],
  "settings": {
    "auto_save_interval": 30000,
    "word_count_target": 100000,
    "backup_enabled": true
  }
}
```

**Tag Resolution Logic:**
1. **Project-specific exists** → Use existing project tag
2. **Global exists** → **Always fork** with customizations (or inherit defaults)
3. **Neither exists** → Create new project-specific tag

**Result:** All resolved tags are project-specific, customizable, and independent
```

**Response:** Same as GET `/projects/{project_id}`

#### PUT `/projects/{project_id}`
Update an existing project with full tag support.

**Request:** Same as POST (all fields optional)
```json
{
  "title": "Updated Novel Title",
  "description": "Updated description",
  "tags": [
    {"id": "temp-1", "name": "dark-fantasy", "icon": "🌙", "color": "#6B46C1"},  // Forks global or creates new
    {"id": "temp-2", "name": "mystery", "icon": "🔍", "color": "#059669"}       // Always-fork behavior
  ]
}
```

**Tag Update Behavior:**
- **Complete Replacement**: Project tags are replaced with newly resolved tags
- **Always Fork**: Global tags are forked even during updates
- **Independent**: Changes don't affect other projects or global tags

**Response:** Same as GET `/projects/{project_id}`

#### DELETE `/projects/{project_id}`
Delete a project (hard delete).

**Response:**
```json
{
  "message": "Project proj_123 deleted successfully"
}
```

#### GET `/projects/{project_id}/file-tree`
Get the complete file tree structure for a project.

**Response:**
```json
{
  "file_tree": [
    {
      "id": "ft_001",
      "name": "Characters",
      "type": "folder", 
      "path": "/characters",
      "parent_id": null,
      "children": [
        {
          "id": "ft_002", 
          "name": "Elara",
          "type": "file",
          "path": "/characters/elara",
          "parent_id": "ft_001",
          "document_id": "doc_456",
          "icon": "👸",
          "tags": [
            {"id": "protagonist", "name": "Protagonist", "icon": "⭐", "color": "#10B981"}
          ],
          "word_count": 1250,
          "created_at": "2025-01-20T14:00:00Z",
          "updated_at": "2025-08-01T09:15:00Z",
          "children": null
        }
      ],
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-08-01T09:15:00Z"
    }
  ],
  "metadata": {
    "total_files": 12,
    "total_folders": 4,
    "last_updated": "2025-08-01T09:15:00Z"
  }
}
```

---

### 3. Document Management

#### GET `/documents/{document_id}`
Get a document by ID.

**Response:**
```json
{
  "id": "doc_456",
  "project_id": "proj_123",
  "title": "Elara - Main Character",
  "path": "/characters/elara",
  "content": {
    "type": "doc",
    "content": [
      {
        "type": "heading",
        "attrs": {"level": 1},
        "content": [{"type": "text", "text": "Elara Moonwhisper"}]
      },
      {
        "type": "paragraph", 
        "content": [
          {"type": "text", "text": "A powerful "},
          {"type": "text", "text": "fire mage", "marks": [{"type": "strong"}]},
          {"type": "text", "text": " with a mysterious past."}
        ]
      }
    ]
  },
  "tags": [
    {"id": "protagonist", "name": "Protagonist", "icon": "⭐", "color": "#10B981"}
  ],
  "word_count": 1250,
  "created_at": "2025-01-20T14:00:00Z",
  "updated_at": "2025-08-01T09:15:00Z",
  "version": "2.5.0",
  "is_locked": false,
  "locked_by": null,
  "file_tree_id": "ft_002"
}
```

#### POST `/documents`
Create a new document with automatic folder hierarchy creation.

**🆕 Path-Based Folder Creation**: The system automatically creates missing folders from the document path. For example, if `path="/characters/locations/taverns/prancing-pony"`, the folders `/characters`, `/characters/locations`, and `/characters/locations/taverns` will be created automatically if they don't exist.

**Request:**
```json
{
  "project_id": "proj_123",
  "title": "New Character Profile",
  "path": "/characters/protagonists/new-character",
  "content": {
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "content": [{"type": "text", "text": "Character description here..."}]
      }
    ]
  },
  "tags": ["character", "draft"]
}
```

**Field Distinctions:**
- **title**: Display name (NO file extensions) - e.g., "Chapter 1: The Beginning"
- **path**: Organizational structure - e.g., "/characters/protagonists/new-character"
  - **Auto-folder creation**: All missing parent folders are created automatically
  - **Path validation**: Normalized, validated, and sanitized for security
  - **Hierarchy**: Supports deeply nested structures like `/world/regions/kingdoms/stormlands/cities/windmere/locations/tavern`
- **content**: ProseMirror JSON with rich content (text, images, formatting, @-references)

**Path Examples:**
```json
// Simple path - creates document at root level
{"path": "/overview"}

// Single folder - creates 'characters' folder if needed
{"path": "/characters/protagonist"}

// Deep hierarchy - creates entire folder structure
{"path": "/world/regions/kingdoms/stormlands/cities/windmere/tavern"}
```

**Response:** Same as GET `/documents/{document_id}`

#### PUT `/documents/{document_id}`
Update an existing document.

**Request:**
```json
{
  "title": "Updated Character Profile",
  "content": {
    "type": "doc", 
    "content": [
      {
        "type": "paragraph",
        "content": [{"type": "text", "text": "Updated character description..."}]
      }
    ]
  },
  "tags": ["character", "complete"],
  "version": "2.6.0" 
}
```

**Response:** Same as GET `/documents/{document_id}`

#### DELETE `/documents/{document_id}`
Delete a document.

**Response:**
```json
{
  "success": true
}
```

---

### 4. Tag Management

#### GET `/projects/{project_id}/tags`
List all tags for a project.

**Query Parameters:**
- `include_archived` (bool): Include archived tags (default: false)
- `category` (string): Filter by category

**Response:**
```json
{
  "success": true,
  "data": {
    "tags": [
      {
        "id": "tag_001",
        "project_id": "proj_123", 
        "name": "Protagonist",
        "description": "Main characters driving the story",
        "color": "#10B981",
        "icon": "⭐",
        "category": "characters",
        "usage_count": 3,
        "is_system": false,
        "is_archived": false,
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-08-01T09:15:00Z"
      }
    ],
    "total": 15,
    "project_id": "proj_123"
  }
}
```

#### POST `/projects/{project_id}/tags`
Create a new tag.

**Request:**
```json
{
  "name": "Magic System",
  "description": "Elements related to the magic system",
  "color": "#8B5CF6",
  "icon": "✨", 
  "category": "worldbuilding"
}
```

#### GET `/projects/{project_id}/tags/{tag_id}`
Get a specific tag.

#### PUT `/projects/{project_id}/tags/{tag_id}`
Update a tag.

#### DELETE `/projects/{project_id}/tags/{tag_id}`
Delete a tag (hard delete).

#### POST `/projects/{project_id}/tags/{tag_id}/archive`
Archive a tag (soft delete).

#### POST `/projects/{project_id}/tags/{tag_id}/unarchive`
Unarchive a tag.

#### GET `/projects/{project_id}/tags/search`
Search tags within a project.

**Query Parameters:**
- `q` (string, required): Search query
- `category` (string): Filter by category
- `include_archived` (bool): Include archived tags (default: false)
- `limit` (int, 1-100): Maximum results (default: 20)

#### GET `/projects/{project_id}/tags/stats`
Get tag statistics for a project.

**Response:**
```json
{
  "success": true,
  "data": {
    "project_id": "proj_123",
    "total_tags": 18,
    "active_tags": 15,
    "archived_tags": 3,
    "system_tags": 2,
    "categories": ["characters", "locations", "magic", "plot"],
    "most_used_tags": [
      {"id": "protagonist", "name": "Protagonist", "usage_count": 5},
      {"id": "magic", "name": "Magic", "usage_count": 8}
    ]
  }
}
```

#### POST `/projects/{project_id}/tags/{tag_id}/assign`
Assign a tag to a file/document.

**Request:**
```json
{
  "file_tree_item_id": "ft_002"
}
```

#### DELETE `/projects/{project_id}/tags/{tag_id}/assign`
Remove a tag from a file/document.

**Request:**
```json
{
  "file_tree_item_id": "ft_002"
}
```

---

### 5. LLM Integration

#### POST `/llm/chat/completions`
Chat completion with LLM models.

**Request:**
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "messages": [
    {"role": "user", "content": "Help me develop this character further..."}
  ],
  "max_tokens": 1000,
  "temperature": 0.7,
  "stream": false
}
```

**Response:**
```json
{
  "id": "chatcmpl_123",
  "object": "chat.completion",
  "created": 1691234567,
  "model": "claude-3-5-sonnet-20241022",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Here are some suggestions for developing your character..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 120,
    "total_tokens": 165
  }
}
```

#### GET `/llm/providers`
List available LLM providers.

#### GET `/llm/models`
List available models.

#### POST `/llm/keys/validate`
Validate an API key for a provider.

#### POST `/llm/keys/store`
Securely store an API key.

#### DELETE `/llm/keys/{provider_id}`
Delete a stored API key.

#### GET `/llm/keys`
List user's stored API keys (encrypted).

---

### 6. File Tree Management

#### GET `/projects/{project_id}/file-tree`
Get the complete file tree structure for a project.

**Response:**
```json
{
  "file_tree": [
    {
      "id": "ft_001",
      "name": "characters",
      "type": "folder",
      "path": "/characters",
      "parent_id": null,
      "children": [
        {
          "id": "ft_002",
          "name": "protagonist.md",
          "type": "file",
          "path": "/characters/protagonist",
          "parent_id": "ft_001",
          "document_id": "doc_123",
          "icon": "👤",
          "tags": [
            {"id": "char_tag", "name": "Character", "icon": "👤", "color": "#F59E0B"}
          ],
          "word_count": 850,
          "created_at": "2025-01-15T10:00:00Z",
          "updated_at": "2025-08-03T15:30:00Z"
        }
      ],
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-08-03T15:30:00Z"
    }
  ],
  "metadata": {
    "total_files": 12,
    "total_folders": 5,
    "last_updated": "2025-08-03T15:30:00Z"
  }
}
```

#### PUT `/projects/{project_id}/file-tree/{item_id}/move`
Move a file tree item to a new location.

**Request:**
```json
{
  "new_path": "/world/locations/cities/protagonist-home",
  "new_parent_id": "ft_005"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "ft_002",
    "name": "protagonist-home",
    "type": "file",
    "path": "/world/locations/cities/protagonist-home",
    "parent_id": "ft_005",
    "document_id": "doc_123",
    "tags": [...],
    "word_count": 850,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-08-06T10:15:00Z"
  }
}
```

#### PUT `/projects/{project_id}/file-tree/{item_id}/rename`
Rename a file tree item.

**Request:**
```json
{
  "new_name": "main-character"
}
```

#### POST `/projects/{project_id}/file-tree`
Create a new folder in the file tree.

**Request:**
```json
{
  "name": "new-chapter",
  "type": "folder", 
  "path": "/chapters/act-2/new-chapter",
  "parent_id": "ft_010",
  "tags": ["plot"],
  "icon": "📖"
}
```

#### DELETE `/projects/{project_id}/file-tree/{item_id}`
Delete a file tree item (folder or file).

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "File tree item deleted successfully",
    "deleted_id": "ft_002"
  }
}
```

---

## Missing Endpoints (Roadmap)

### 1. User Management

#### GET `/users/profile`
Get current user profile.

#### PUT `/users/profile`
Update user profile.

#### GET `/users/preferences`
Get user preferences.

#### PUT `/users/preferences` 
Update user preferences.

---

### 2. @-Reference System (Missing)

#### GET `/projects/{project_id}/references`
Get all extractable references for @-reference autocomplete.

**Response:**
```json
{
  "references": [
    {
      "type": "document",
      "id": "doc_456",
      "path": "/characters/elara",
      "title": "Elara - Main Character",
      "tags": ["protagonist"],
      "preview": "A powerful fire mage with..."
    },
    {
      "type": "tag",
      "id": "fire-magic",
      "name": "Fire Magic",
      "usage_count": 5,
      "documents": ["doc_456", "doc_789"]
    }
  ]
}
```

#### POST `/projects/{project_id}/references/extract`
Extract @-references from document content.

**Request:**
```json
{
  "document_id": "doc_456",
  "content": {
    "type": "doc",
    "content": [...]
  }
}
```

#### GET `/projects/{project_id}/references/validate`
Validate @-references in content.

---

### 3. Content Conversion & Export (Missing)

#### GET `/documents/{document_id}/export/markdown`
Export document as Markdown.

#### GET `/documents/{document_id}/export/html`
Export document as HTML.

#### GET `/documents/{document_id}/export/pdf`
Export document as PDF.

#### GET `/projects/{project_id}/export/zip`
Export entire project as ZIP archive.

---

### 4. Collaboration (Missing)

#### GET `/projects/{project_id}/collaborators`
List project collaborators.

#### POST `/projects/{project_id}/collaborators`
Add a collaborator to a project.

#### PUT `/projects/{project_id}/collaborators/{user_id}`
Update collaborator permissions.

#### DELETE `/projects/{project_id}/collaborators/{user_id}`
Remove a collaborator.

#### GET `/documents/{document_id}/comments`
Get comments on a document.

#### POST `/documents/{document_id}/comments`
Add a comment to a document.

#### GET `/documents/{document_id}/versions`
Get version history for a document.

---

### 5. Search & Navigation (Missing)

#### GET `/projects/{project_id}/search`
Global search within a project.

**Query Parameters:**
- `q` (string, required): Search query
- `type` (string): Filter by content type - `documents|tags|all`
- `limit` (int): Maximum results

**Response:**
```json
{
  "query": "fire magic",
  "results": [
    {
      "type": "document",
      "id": "doc_456", 
      "title": "Elara - Main Character",
      "path": "/characters/elara",
      "relevance": 0.95,
      "snippet": "...powerful **fire magic** abilities..."
    },
    {
      "type": "tag",
      "id": "fire-magic",
      "name": "Fire Magic", 
      "usage_count": 5,
      "relevance": 0.88
    }
  ],
  "total": 8,
  "limit": 20
}
```

#### GET `/projects/{project_id}/recent`
Get recently modified documents.

#### GET `/projects/{project_id}/bookmarks`
Get bookmarked documents.

#### POST `/projects/{project_id}/bookmarks`
Bookmark a document.

---

### 6. Analytics & Progress (Missing)

#### GET `/projects/{project_id}/stats`
Get detailed project statistics.

**Response:**
```json
{
  "project_id": "proj_123",
  "writing_stats": {
    "total_words": 15420,
    "target_words": 80000,
    "progress_percentage": 19.3,
    "daily_average": 245,
    "weekly_trend": 8.5
  },
  "content_stats": {
    "total_documents": 12,
    "characters": 8,
    "locations": 5,  
    "chapters": 15
  },
  "activity_stats": {
    "last_7_days": {
      "words_written": 1750,
      "documents_modified": 6,
      "sessions": 4
    }
  }
}
```

#### GET `/users/activity`
Get user activity and writing habits.

#### GET `/projects/{project_id}/progress`
Get writing progress over time.

---

### 7. Real-time Features (WebSocket) (Missing)

#### WebSocket `/ws/projects/{project_id}`
Real-time project updates.

**Events:**
- `document_updated`: Document content changed
- `collaborator_joined`: User joined project
- `file_tree_changed`: File structure modified

---

### 8. Import & Integration (Missing)

#### POST `/projects/{project_id}/import/markdown`
Import Markdown files.

#### POST `/projects/{project_id}/import/word`
Import Word documents.

#### POST `/projects/{project_id}/import/scrivener`
Import Scrivener projects.

#### GET `/projects/{project_id}/integrations`
List available integrations.

#### POST `/projects/{project_id}/integrations/{service}`
Configure integration (Google Drive, Dropbox, etc.).

---

## Integration Patterns

### Frontend-Backend Data Flow

1. **Project Load**: Frontend fetches projects, documents, and tags
2. **Local Index**: Build searchable index for @-references 
3. **Real-time Updates**: Use TanStack Query for optimistic updates
4. **Offline Support**: LocalStorage caching for offline editing

### Pagination Strategy
```http
GET /projects?limit=20&offset=40
```

### Filtering & Search
```http  
GET /projects/{project_id}/tags/search?q=magic&category=worldbuilding&limit=10
```

### Batch Operations
```http
POST /projects/{project_id}/documents/batch
```

### Error Handling
All endpoints return consistent error format:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title cannot contain file extensions",
    "details": {
      "field": "title",
      "rejected_value": "Chapter 1.md"
    }
  }
}
```

---

## Testing Guidelines

### Insomnia/Postman Testing

#### Environment Variables
```json
{
  "base_url": "http://localhost:8000/api/v1",
  "auth_token": "{{supabase_jwt_token}}",
  "project_id": "{{test_project_id}}",
  "document_id": "{{test_document_id}}"
}
```

#### Essential Test Cases

1. **Authentication Flow**
   - Valid JWT token → 200 responses
   - Invalid/expired token → 401 Unauthorized
   - Missing token → 401 Unauthorized

2. **Project Management**
   - Create project → Verify in GET /projects
   - Update project → Check updated_at timestamp
   - Delete project → Verify 404 on subsequent GET

3. **Document Operations**
   - Create document with ProseMirror content
   - Verify word count calculation
   - Test title validation (reject .md extensions)
   - Test path normalization and validation
   - **Path-Based Creation Tests**:
     - Create document with simple path (`/overview`) → no folders created
     - Create document with nested path (`/characters/protagonists/hero`) → auto-creates folders
     - Create document with deep hierarchy → verify all folders created
     - Test with existing folders → should reuse existing structure
     - Test invalid paths → should return 400 with validation errors

4. **Tag Management & Always-Fork System**
   - **Project Creation with Tags**:
     - Create project with global tag → verify tag is forked to project (not referenced)
     - Create project with custom icon/color → verify global tag is forked with customizations
     - Create project with non-existent tag → verify new project-specific tag is created
     - Verify all resolved tags have `is_global: false` and correct `project_id`
   - **Project Updates with Tags**:
     - Update project tags → verify complete tag replacement with always-fork behavior
     - Add new global tag → verify it's forked to project, not referenced
     - Mix of existing and new tags → verify proper resolution and assignment
   - **Tag Independence**:
     - Modify project tag → verify global tag remains unchanged
     - Delete project tag → verify global tag and other project tags unaffected
     - Verify same global tag can be forked differently across projects
   - **Traditional Tag Operations**:
     - Create standalone tags with colors/icons
     - Assign/unassign to documents and file tree items
     - Search and filter tags with precedence logic
     - Archive/unarchive operations

5. **Error Scenarios**
   - Invalid project ID → 404
   - Malformed JSON → 400
   - Server errors → 500

### File Tree vs Document Architecture Testing

**Understanding the Three-Entity System**: Test the separation between organization (file tree) and content (documents).

#### **Entity Relationship Tests**

1. **Document Creation Workflow**:
   ```bash
   # Step 1: Create document with nested path
   POST /projects/proj_123/documents
   {
     "title": "Character Background",
     "path": "/characters/protagonists/hero-backstory"
   }
   
   # Verify 3 entities were created:
   # 1. Document with content
   GET /documents/{document_id} → Rich content, word count
   
   # 2. File tree folders (auto-created)
   GET /projects/proj_123/file-tree
   # Should show: /characters (folder) → /protagonists (folder) → hero-backstory (file)
   
   # 3. File tree item linking to document
   # File at /characters/protagonists/hero-backstory should have document_id
   ```

2. **File vs Document Independence**:
   ```bash
   # Move file in tree (organization change)
   PUT /projects/proj_123/file-tree/{file_id}/move
   {"new_path": "/world/characters/hero-backstory"}
   
   # Verify document content unchanged
   GET /documents/{document_id} → Same content, same word count
   
   # Verify file moved but still links to same document
   GET /projects/proj_123/file-tree → File in new location, same document_id
   ```

3. **Folder vs File vs Document Distinction**:
   ```bash
   # Create manual folder
   POST /projects/proj_123/file-tree
   {"name": "research", "type": "folder", "path": "/research"}
   
   # Verify folder has no content
   GET /projects/proj_123/file-tree → type: "folder", document_id: null
   
   # Files have linked documents
   GET /projects/proj_123/file-tree → type: "file", document_id: "doc_123"
   
   # Documents have actual content
   GET /documents/doc_123 → content: {ProseMirror JSON}, word_count: 150
   ```

#### **Path-Based Creation Tests**

1. **Single Document Creation**:
   ```bash
   POST /projects/proj_123/documents {"path": "/notes"}
   # Result: Creates document + file tree item (no folders needed)
   ```

2. **Deep Hierarchy Creation**:
   ```bash
   POST /projects/proj_123/documents {"path": "/world/regions/kingdoms/stormlands/cities/kings-landing"}
   # Result: Auto-creates 5 folders + 1 file + 1 document
   ```

3. **Existing Folder Reuse**:
   ```bash
   # First document creates folders
   POST /projects/proj_123/documents {"path": "/characters/heroes/aragorn"}
   
   # Second document reuses existing folders
   POST /projects/proj_123/documents {"path": "/characters/heroes/legolas"}
   # Result: Reuses /characters and /heroes folders, creates new file + document
   ```

### Integration Testing

Test the complete flow:
1. Create project
2. Create documents with @-references
3. Add tags and assign to documents
4. Export content in different formats
5. Collaborate with other users

---

## Conclusion

This specification covers the complete ShuScribe API, from currently implemented endpoints to the full roadmap for a comprehensive Universe Content Management Platform. The API is designed to scale from individual creators to enterprise studio workflows while maintaining simplicity and performance.

**Recent Major Updates:**
- **Path-Based Document Creation**: Automatic folder hierarchy creation eliminates manual folder management
- **API Simplification**: Removed redundant `file_tree_parent_id` field for cleaner API design
- **Enhanced UX**: Users can create complex organizational structures in single API calls

**Next Steps:**
1. Implement missing file tree management endpoints
2. Add @-reference system endpoints
3. Build real-time collaboration features
4. Create comprehensive export/import capabilities
5. Add analytics and progress tracking

---

*For implementation details, see individual endpoint files in `/backend/src/api/v1/endpoints/`*