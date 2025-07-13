# ShuScribe API Contracts

**Frontend-First API Design for MVP Development**

This document defines the REST API contracts from the frontend perspective, designed to support the current UI workflows and data models. These contracts will be implemented first as MSW mocks, then later as Python backend APIs.

## Core Principles

- **Frontend-Driven**: Designed based on actual UI needs and workflows
- **RESTful**: Standard HTTP methods and status codes
- **Consistent**: Uniform response formats and error handling
- **Realistic**: Proper pagination, validation, and edge cases
- **Future-Ready**: Designed for scalability and collaboration features

## Authentication

**Note**: Authentication is handled entirely by Supabase Auth on the frontend. The backend validates Supabase JWT tokens but does not provide auth endpoints since login/signup/logout happen directly between the frontend and Supabase.

**Authentication Flow**:
1. Frontend handles login/signup via Supabase Auth
2. Frontend receives JWT token from Supabase  
3. Frontend sends token in `Authorization: Bearer <token>` header
4. Backend validates JWT token with Supabase and extracts user info

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

## Wiki Management

### Generate Wiki from References

```http
POST /api/projects/{project_id}/wiki/generate
Authorization: Bearer {token}
Content-Type: application/json

{
  "generation_mode": "ai",
  "spoiler_management": {
    "arc_breakpoints": ["chapter-5", "chapter-12"],
    "spoiler_levels": [0, 5, 10]
  },
  "entity_categories": ["characters", "locations", "concepts"]
}

Response 201:
{
  "wiki_id": "wiki_123",
  "generation_status": "in_progress",
  "estimated_completion": "2025-01-01T12:05:00Z",
  "entities_found": 15,
  "processing_id": "proc_456"
}
```

### Get Wiki Configuration

```http
GET /api/wikis/{wiki_id}
Authorization: Bearer {token}

Response 200:
{
  "id": "wiki_123",
  "project_id": "prj_123",
  "generation_mode": "ai",
  "auto_update": true,
  "spoiler_management": {
    "arc_breakpoints": ["chapter-5", "chapter-12"],
    "spoiler_levels": [0, 5, 10]
  },
  "entity_categories": ["characters", "locations", "concepts"],
  "is_public": false,
  "last_generated": "2025-01-01T12:00:00Z",
  "entries_count": 15
}
```

### Get Wiki Entries

```http
GET /api/wikis/{wiki_id}/entries
Authorization: Bearer {token}
Query Parameters:
  - entity_type: string (optional filter)
  - spoiler_level: number (max spoiler level)
  - limit: number (default: 20)
  - offset: number (default: 0)

Response 200:
{
  "entries": [
    {
      "id": "entry_123",
      "entity_name": "Elara Moonwhisper",
      "entity_type": "character",
      "slug": "elara-moonwhisper",
      "content": {
        "summary": "Powerful fire mage and protagonist...",
        "description": "<detailed wiki content>",
        "relationships": [
          {
            "target": "Marcus Stormwind",
            "relationship": "mentor"
          }
        ]
      },
      "spoiler_level": 0,
      "appearances": [
        {
          "document_id": "doc_125",
          "document_title": "Chapter 1",
          "mention_count": 5
        }
      ],
      "ai_generated": true,
      "human_edited": false,
      "view_count": 42,
      "created_at": "2025-01-01T12:00:00Z",
      "updated_at": "2025-01-01T12:00:00Z"
    }
  ],
  "pagination": {
    "total": 15,
    "limit": 20,
    "offset": 0,
    "has_more": false
  }
}
```

### Update Wiki Entry

```http
PUT /api/wiki-entries/{entry_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": {
    "summary": "Updated summary...",
    "description": "<updated content>"
  },
  "spoiler_level": 2,
  "human_edited": true
}

Response 200:
{
  "id": "entry_123",
  "entity_name": "Elara Moonwhisper",
  "content": { ... },
  "spoiler_level": 2,
  "human_edited": true,
  "updated_at": "2025-01-01T12:30:00Z"
}
```

## Export and Publishing

### Export Content

```http
POST /api/documents/{document_id}/export
Authorization: Bearer {token}
Content-Type: application/json

{
  "format": "pdf",
  "options": {
    "include_wiki": true,
    "spoiler_level": 5,
    "styling": {
      "font_family": "serif",
      "font_size": 12,
      "page_margins": "normal"
    }
  }
}

Response 202:
{
  "export_id": "exp_123",
  "status": "processing",
  "estimated_completion": "2025-01-01T12:05:00Z",
  "format": "pdf",
  "file_size_estimate": "2.5MB"
}
```

### Get Export Status

```http
GET /api/exports/{export_id}
Authorization: Bearer {token}

Response 200:
{
  "id": "exp_123",
  "status": "completed",
  "format": "pdf",
  "download_url": "https://api.shuscribe.com/downloads/exp_123.pdf",
  "file_size": "2.7MB",
  "expires_at": "2025-01-02T12:00:00Z",
  "created_at": "2025-01-01T12:00:00Z",
  "completed_at": "2025-01-01T12:04:30Z"
}

Response 200 (if processing):
{
  "id": "exp_123",
  "status": "processing",
  "progress": 65,
  "estimated_completion": "2025-01-01T12:05:00Z"
}
```

### Publish Content

```http
POST /api/documents/{document_id}/publish
Authorization: Bearer {token}
Content-Type: application/json

{
  "publication_mode": "story-and-wiki",
  "visibility": "public",
  "custom_slug": "my-fantasy-novel",
  "wiki_config": {
    "spoiler_level": 5,
    "allow_comments": true
  },
  "seo_config": {
    "title": "My Fantasy Novel - Complete Story",
    "description": "An epic fantasy adventure with detailed world-building",
    "keywords": ["fantasy", "novel", "adventure"]
  }
}

Response 201:
{
  "publication_id": "pub_123",
  "public_url": "https://shuscribe.com/stories/my-fantasy-novel",
  "wiki_url": "https://shuscribe.com/wikis/my-fantasy-novel",
  "status": "published",
  "visibility": "public",
  "published_at": "2025-01-01T12:00:00Z"
}
```

### Update Publication Settings

```http
PUT /api/publications/{publication_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "visibility": "unlisted",
  "wiki_config": {
    "spoiler_level": 8,
    "allow_comments": false
  }
}

Response 200:
{
  "id": "pub_123",
  "visibility": "unlisted",
  "wiki_config": { ... },
  "updated_at": "2025-01-01T12:30:00Z"
}
```

## Public Content Access

### Get Public Story

```http
GET /api/public/stories/{slug}
No Authorization Required
Query Parameters:
  - chapter: number (optional, specific chapter)
  - reader_id: string (optional, for progress tracking)

Response 200:
{
  "id": "pub_123",
  "title": "My Fantasy Novel",
  "author": {
    "name": "John Doe",
    "profile_url": "https://shuscribe.com/authors/john-doe"
  },
  "description": "An epic fantasy adventure...",
  "chapters": [
    {
      "number": 1,
      "title": "The Beginning",
      "content": { ... },
      "word_count": 2500,
      "reading_time_minutes": 10,
      "published_at": "2025-01-01T12:00:00Z"
    }
  ],
  "wiki_available": true,
  "wiki_url": "https://shuscribe.com/wikis/my-fantasy-novel",
  "stats": {
    "total_views": 1500,
    "total_chapters": 25,
    "total_words": 75000,
    "average_rating": 4.7
  },
  "last_updated": "2025-01-01T12:00:00Z"
}
```

### Get Public Wiki

```http
GET /api/public/wikis/{slug}
No Authorization Required
Query Parameters:
  - spoiler_level: number (max spoiler level to show)
  - entity_type: string (filter by entity type)
  - reader_progress: number (chapter number for spoiler management)

Response 200:
{
  "id": "wiki_123",
  "title": "My Fantasy Novel - Universe Guide",
  "story_title": "My Fantasy Novel",
  "story_url": "https://shuscribe.com/stories/my-fantasy-novel",
  "entries": [
    {
      "entity_name": "Elara Moonwhisper",
      "entity_type": "character",
      "slug": "elara-moonwhisper",
      "summary": "Powerful fire mage and protagonist",
      "spoiler_level": 0,
      "view_count": 250
    }
  ],
  "categories": [
    {
      "name": "characters",
      "count": 8,
      "icon": "Users"
    },
    {
      "name": "locations",
      "count": 5,
      "icon": "MapPin"
    }
  ],
  "stats": {
    "total_entries": 15,
    "total_views": 3200,
    "last_updated": "2025-01-01T12:00:00Z"
  }
}
```

### Get Wiki Entry Detail

```http
GET /api/public/wikis/{slug}/entries/{entry_slug}
No Authorization Required
Query Parameters:
  - reader_progress: number (chapter number for spoiler management)

Response 200:
{
  "entity_name": "Elara Moonwhisper",
  "entity_type": "character",
  "content": {
    "summary": "Powerful fire mage and protagonist...",
    "description": "<detailed content>",
    "relationships": [
      {
        "target": "Marcus Stormwind",
        "target_slug": "marcus-stormwind",
        "relationship": "mentor"
      }
    ]
  },
  "spoiler_level": 0,
  "appearances": [
    {
      "chapter_number": 1,
      "chapter_title": "The Beginning",
      "mention_count": 5
    }
  ],
  "related_entries": [
    {
      "name": "Fire Magic",
      "slug": "fire-magic",
      "type": "concept"
    }
  ],
  "view_count": 250,
  "last_updated": "2025-01-01T12:00:00Z"
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

### Publishing Analytics

```http
GET /api/publications/{publication_id}/analytics
POST /api/public/stories/{slug}/track-view
GET /api/authors/{author_id}/dashboard
```

This API design provides a comprehensive foundation for ShuScribe's evolution from a simple writing tool to a full universe content management platform, supporting everything from basic document management to advanced publishing workflows with AI-generated wikis and interactive reading experiences.