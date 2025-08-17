# ShuScribe API Contracts

**REST API contracts for currently implemented endpoints**

## Base Configuration
- **Base URL**: `http://localhost:8000/api/v1` (dev)
- **Content Type**: `application/json`
- **Authentication**: `Authorization: Bearer <supabase_jwt>`
- **Response Format**: `ApiResponse<T>` wrapper

## Core Principles
- **Frontend-First**: API matches `frontend/src/types/api.ts` interfaces
- **Path-Based**: Documents auto-create folder hierarchy from paths
- **Rich Content**: ProseMirror JSON for document content
- **Consistent Errors**: Standardized error responses

## Authentication
All endpoints require Supabase JWT token in Authorization header.

## Currently Implemented Endpoints

### Projects
```typescript
GET    /projects                    // List user projects
POST   /projects                    // Create project
GET    /projects/{id}               // Get project details
PUT    /projects/{id}               // Update project
DELETE /projects/{id}               // Delete project
```

### Documents
```typescript
GET    /projects/{id}/documents                    // List documents
POST   /projects/{id}/documents                    // Create document (auto-creates folders from path)
GET    /projects/{id}/documents/{doc_id}           // Get document
PUT    /projects/{id}/documents/{doc_id}           // Update document  
DELETE /projects/{id}/documents/{doc_id}           // Delete document
```

### File Tree
```typescript
GET    /projects/{id}/file-tree     // Get complete file tree
POST   /projects/{id}/file-tree     // Create folder/file
PUT    /projects/{id}/file-tree/{item_id}    // Update item
DELETE /projects/{id}/file-tree/{item_id}    // Delete item
```

### Tags
```typescript
GET    /projects/{id}/tags          // List project tags
POST   /projects/{id}/tags          // Create tag
PUT    /projects/{id}/tags/{tag_id} // Update tag
DELETE /projects/{id}/tags/{tag_id} // Delete tag
```

### LLM/AI
```typescript
POST   /projects/{id}/llm/generate      // Generate content with AI
```

## Request/Response Examples

### Request/Response Format

**Document Creation**: POST requests include title, path (auto-creates folder hierarchy), ProseMirror JSON content, and tag arrays. Returns `ApiResponse<Document>` wrapper.

**File Tree Structure**: Hierarchical JSON structure with nested children, type indicators (folder/file), and metadata for each item.

**Error Responses**: Consistent error format with success boolean, error type, descriptive message, and HTTP status code.

**Example Implementations**: See request/response handling in `frontend/src/lib/api/` and backend models in `backend/src/schemas/`.

## Field Naming
- **Frontend**: camelCase (`createdAt`, `wordCount`)
- **Backend**: snake_case with Pydantic aliases
- **API**: Backend handles both formats automatically

## Integration Notes
- Documents use ProseMirror JSON format for rich content
- Path-based document creation eliminates manual folder management
- All responses wrapped in `ApiResponse<T>` for consistent error handling
- Word counts auto-calculated and tracked
- Tag system supports categories, colors, and icons

---

# TODO: Future Endpoints (Not Yet Implemented)

## Wiki Management (FUTURE)
```typescript
// TODO: Implement wiki generation system
POST   /projects/{id}/wiki/generate      // Generate wiki from references
GET    /wikis/{wiki_id}                  // Get wiki configuration
GET    /wikis/{wiki_id}/entries          // Get wiki entries
PUT    /wiki-entries/{entry_id}          // Update wiki entry
```

## Export and Publishing (FUTURE)
```typescript  
// TODO: Implement export system
POST   /documents/{document_id}/export   // Export content
GET    /exports/{export_id}              // Get export status

// TODO: Implement publishing system  
POST   /documents/{document_id}/publish  // Publish content
PUT    /publications/{publication_id}    // Update publication settings
```

## Public Content Access (FUTURE)
```typescript
// TODO: Implement public content system
GET    /public/stories/{slug}            // Get public story
GET    /public/wikis/{slug}              // Get public wiki
GET    /public/wikis/{slug}/entries/{entry_slug} // Get wiki entry detail
```

## Real-time Features (FUTURE)
```typescript
// TODO: Implement WebSocket support
ws://localhost:3001/api/ws/projects/{project_id}
// Events: document_updated, document_locked, user_joined, etc.

// TODO: Implement collaboration features
POST   /documents/{document_id}/lock     // Lock document
DELETE /documents/{document_id}/lock     // Unlock document
GET    /projects/{project_id}/active-users // Get active users
```

## Advanced Features (FUTURE)
```typescript
// TODO: Implement file uploads
POST   /projects/{id}/files              // Upload files

// TODO: Implement advanced search
GET    /projects/{id}/search             // Search project content

// TODO: Implement analytics
GET    /publications/{id}/analytics      // Get publication analytics
```