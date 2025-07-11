# ShuScribe API Contracts

**Frontend-First API Design for MVP Development**

This document defines the REST API contracts from the frontend perspective, designed to support the current UI workflows and data models. These contracts will be implemented first as MSW mocks, then later as Python backend APIs.

## Core Principles

- **Frontend-Driven**: Designed based on actual UI needs and workflows
- **RESTful**: Standard HTTP methods and status codes
- **Consistent**: Uniform response formats and error handling
- **Realistic**: Proper pagination, validation, and edge cases
- **Future-Ready**: Designed for scalability and collaboration features

## Authentication & User Management

### Authentication

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response 200:
{
  "user": {
    "id": "usr_123",
    "email": "user@example.com",
    "name": "John Doe",
    "avatar": "https://...",
    "created_at": "2025-01-01T00:00:00Z"
  },
  "token": "jwt_token_here",
  "expires_at": "2025-01-02T00:00:00Z"
}

Response 401:
{
  "error": "invalid_credentials",
  "message": "Invalid email or password"
}
```

```http
POST /api/auth/logout
Authorization: Bearer {token}

Response 200:
{
  "message": "Logged out successfully"
}
```

```http
GET /api/auth/me
Authorization: Bearer {token}

Response 200:
{
  "user": {
    "id": "usr_123",
    "email": "user@example.com",
    "name": "John Doe",
    "avatar": "https://...",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

## Project Management

### List Projects

```http
GET /api/projects
Authorization: Bearer {token}
Query Parameters:
  - limit: number (default: 20, max: 100)
  - offset: number (default: 0)
  - sort: string (title|created_at|updated_at)
  - order: string (asc|desc)

Response 200:
{
  "projects": [
    {
      "id": "prj_123",
      "title": "Fantasy Novel",
      "description": "Epic fantasy adventure story",
      "word_count": 50000,
      "document_count": 25,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T12:00:00Z",
      "tags": ["fantasy", "novel"],
      "collaborators": [
        {
          "user_id": "usr_123",
          "role": "owner",
          "name": "John Doe"
        }
      ]
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 20,
    "offset": 0,
    "has_more": false
  }
}
```

### Get Project Details

```http
GET /api/projects/{project_id}
Authorization: Bearer {token}

Response 200:
{
  "id": "prj_123",
  "title": "Fantasy Novel",
  "description": "Epic fantasy adventure story",
  "word_count": 50000,
  "document_count": 25,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z",
  "tags": ["fantasy", "novel"],
  "collaborators": [
    {
      "user_id": "usr_123",
      "role": "owner",
      "name": "John Doe",
      "avatar": "https://..."
    }
  ],
  "settings": {
    "auto_save_interval": 2000,
    "word_count_target": 80000,
    "backup_enabled": true
  }
}

Response 404:
{
  "error": "project_not_found",
  "message": "Project not found or access denied"
}
```

### Create Project

```http
POST /api/projects
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "New Fantasy Novel",
  "description": "An epic adventure story",
  "tags": ["fantasy", "novel"],
  "settings": {
    "auto_save_interval": 2000,
    "word_count_target": 80000
  }
}

Response 201:
{
  "id": "prj_124",
  "title": "New Fantasy Novel",
  "description": "An epic adventure story",
  "word_count": 0,
  "document_count": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "tags": ["fantasy", "novel"],
  "collaborators": [
    {
      "user_id": "usr_123",
      "role": "owner",
      "name": "John Doe"
    }
  ]
}
```

## File Tree Management

### Get Project File Tree

```http
GET /api/projects/{project_id}/file-tree
Authorization: Bearer {token}

Response 200:
{
  "file_tree": [
    {
      "id": "ft_1",
      "name": "characters",
      "type": "folder",
      "path": "/characters",
      "children": [
        {
          "id": "ft_2",
          "name": "protagonists",
          "type": "folder",
          "path": "/characters/protagonists",
          "children": [
            {
              "id": "ft_3",
              "name": "elara.md",
              "type": "file",
              "path": "/characters/protagonists/elara.md",
              "document_id": "doc_123",
              "icon": "User",
              "tags": ["fire-magic", "trauma"],
              "word_count": 1200,
              "created_at": "2025-01-01T00:00:00Z",
              "updated_at": "2025-01-01T12:00:00Z"
            }
          ]
        }
      ]
    }
  ],
  "metadata": {
    "total_files": 15,
    "total_folders": 4,
    "last_updated": "2025-01-01T12:00:00Z"
  }
}
```

### Create Folder

```http
POST /api/projects/{project_id}/file-tree/folders
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "new-folder",
  "parent_id": "ft_1",
  "path": "/characters/new-folder"
}

Response 201:
{
  "id": "ft_5",
  "name": "new-folder",
  "type": "folder",
  "path": "/characters/new-folder",
  "parent_id": "ft_1",
  "children": [],
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### Move File/Folder

```http
PUT /api/projects/{project_id}/file-tree/{item_id}/move
Authorization: Bearer {token}
Content-Type: application/json

{
  "new_parent_id": "ft_2",
  "new_name": "renamed-item",
  "new_path": "/characters/protagonists/renamed-item"
}

Response 200:
{
  "id": "ft_3",
  "name": "renamed-item",
  "type": "file",
  "path": "/characters/protagonists/renamed-item",
  "parent_id": "ft_2",
  "updated_at": "2025-01-01T12:30:00Z"
}
```

## Document Management

### Get Document

```http
GET /api/documents/{document_id}
Authorization: Bearer {token}
Query Parameters:
  - include_content: boolean (default: true)
  - version: string (optional, for versioning)

Response 200:
{
  "id": "doc_123",
  "project_id": "prj_123",
  "title": "Elara Moonwhisper",
  "path": "/characters/protagonists/elara.md",
  "content": {
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "Elara is a powerful fire mage..."
          }
        ]
      }
    ]
  },
  "tags": ["fire-magic", "trauma"],
  "word_count": 1200,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z",
  "version": "v1.2.3",
  "is_locked": false,
  "locked_by": null,
  "file_tree_id": "ft_3"
}

Response 404:
{
  "error": "document_not_found",
  "message": "Document not found or access denied"
}
```

### Create Document

```http
POST /api/documents
Authorization: Bearer {token}
Content-Type: application/json

{
  "project_id": "prj_123",
  "title": "New Character",
  "path": "/characters/new-character.md",
  "content": {
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "content": []
      }
    ]
  },
  "tags": ["character"],
  "file_tree_parent_id": "ft_2"
}

Response 201:
{
  "id": "doc_124",
  "project_id": "prj_123",
  "title": "New Character",
  "path": "/characters/new-character.md",
  "content": { ... },
  "tags": ["character"],
  "word_count": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "version": "v1.0.0",
  "file_tree_id": "ft_6"
}
```

### Update Document

```http
PUT /api/documents/{document_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Updated Title",
  "content": {
    "type": "doc",
    "content": [...]
  },
  "tags": ["updated-tag"],
  "version": "v1.2.3"
}

Response 200:
{
  "id": "doc_123",
  "title": "Updated Title",
  "content": { ... },
  "tags": ["updated-tag"],
  "word_count": 1250,
  "updated_at": "2025-01-01T12:30:00Z",
  "version": "v1.2.4"
}

Response 409:
{
  "error": "version_conflict",
  "message": "Document has been modified by another user",
  "current_version": "v1.2.5",
  "provided_version": "v1.2.3"
}
```

### Get Document Metadata Only

```http
GET /api/documents/{document_id}/meta
Authorization: Bearer {token}

Response 200:
{
  "id": "doc_123",
  "project_id": "prj_123",
  "title": "Elara Moonwhisper",
  "path": "/characters/protagonists/elara.md",
  "tags": ["fire-magic", "trauma"],
  "word_count": 1200,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z",
  "version": "v1.2.3",
  "is_locked": false,
  "locked_by": null,
  "file_tree_id": "ft_3"
}
```

### Bulk Operations

```http
POST /api/documents/bulk
Authorization: Bearer {token}
Content-Type: application/json

{
  "operation": "get_multiple",
  "document_ids": ["doc_123", "doc_124", "doc_125"],
  "include_content": false
}

Response 200:
{
  "documents": [
    {
      "id": "doc_123",
      "title": "Elara Moonwhisper",
      "word_count": 1200,
      ...
    }
  ],
  "not_found": [],
  "access_denied": []
}
```

## Reference System

### Get Document References

```http
GET /api/documents/{document_id}/references
Authorization: Bearer {token}

Response 200:
{
  "outgoing_references": [
    {
      "target_document_id": "doc_124",
      "target_title": "Marcus Stormwind",
      "reference_text": "@marcus",
      "count": 3
    }
  ],
  "incoming_references": [
    {
      "source_document_id": "doc_125",
      "source_title": "Chapter 1",
      "reference_text": "@elara",
      "count": 5
    }
  ]
}
```

### Search References

```http
GET /api/projects/{project_id}/references/search
Authorization: Bearer {token}
Query Parameters:
  - q: string (search query)
  - type: string (file|folder|both)
  - limit: number (default: 10)

Response 200:
{
  "results": [
    {
      "id": "doc_123",
      "title": "Elara Moonwhisper",
      "type": "file",
      "path": "/characters/protagonists/elara.md",
      "icon": "User",
      "tags": ["fire-magic"],
      "match_score": 0.95
    }
  ],
  "total": 1
}
```

## Error Handling

### Standard Error Format

```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "details": {
    "field": "validation error details"
  },
  "request_id": "req_123456"
}
```

### Common HTTP Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `409 Conflict` - Version conflict or duplicate resource
- `422 Unprocessable Entity` - Validation errors
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Rate Limiting

All endpoints are subject to rate limiting:

```http
Response Headers:
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination:

```json
{
  "data": [...],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "has_more": true,
    "next_offset": 20
  }
}
```

## Versioning

API versioning through Accept header:

```http
Accept: application/json; version=1
```

## Future Considerations

### Real-time Features (WebSocket)

```
ws://localhost:3000/api/ws/projects/{project_id}

Events:
- document_updated
- document_locked
- document_unlocked
- user_joined
- user_left
- cursor_position
```

### Collaboration Features

```http
POST /api/documents/{document_id}/lock
DELETE /api/documents/{document_id}/lock
GET /api/projects/{project_id}/active-users
```

This API design provides a solid foundation for frontend-first development while being realistic about future backend implementation in Python.