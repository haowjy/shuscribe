# API Reference

**ShuScribe REST API - Essential Endpoint Reference**

## Base Configuration
- **Base URL**: `http://localhost:8000/api/v1` (dev) / `https://api.shuscribe.com/api/v1` (prod)
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

### File Tree
```typescript
GET    /projects/{id}/file-tree     // Get complete file tree
POST   /projects/{id}/file-tree     // Create folder/file
PUT    /projects/{id}/file-tree/{item_id}    // Update item
DELETE /projects/{id}/file-tree/{item_id}    // Delete item
```

### Documents
```typescript
GET    /projects/{id}/documents                    // List documents
POST   /projects/{id}/documents                    // Create document (auto-creates folders from path)
GET    /projects/{id}/documents/{doc_id}           // Get document
PUT    /projects/{id}/documents/{doc_id}           // Update document  
DELETE /projects/{id}/documents/{doc_id}           // Delete document
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
POST   /projects/{id}/llm/wikigen       // Generate wiki entries
```

## Request/Response Examples

### Create Document
```typescript
POST /api/v1/projects/{id}/documents
{
  "title": "Aria Stormwind",
  "path": "/characters/protagonists/aria_stormwind", // Auto-creates folders
  "content": { /* ProseMirror JSON */ },
  "tags": ["character", "protagonist", "wind-magic"]
}

Response: ApiResponse<Document>
```

### File Tree Response
```typescript
GET /api/v1/projects/{id}/file-tree
{
  "success": true,
  "data": {
    "id": "root",
    "name": "Project Root", 
    "type": "folder",
    "children": [
      {
        "id": "characters",
        "name": "Characters",
        "type": "folder",
        "children": [/* nested items */]
      }
    ]
  }
}
```

## Error Handling
```typescript
{
  "success": false,
  "error": "ValidationError",
  "message": "Invalid document path",
  "status": 400
}
```

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

## Missing Endpoints (Planned)
- Real-time collaboration via WebSockets
- File uploads for images/attachments
- Advanced search across project content
- Public project sharing/publishing