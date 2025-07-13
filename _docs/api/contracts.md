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
    "has_more": false,
    "next_offset": null
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
  "id": "ft_new",
  "name": "new-folder",
  "type": "folder",
  "path": "/characters/new-folder",
  "parent_id": "ft_1",
  "children": [],
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### Create File

```http
POST /api/projects/{project_id}/file-tree/files
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "new-file.md",
  "parent_id": "ft_2",
  "path": "/characters/protagonists/new-file.md",
  "document_id": "doc_456"
}

Response 201:
{
  "id": "ft_new_file",
  "name": "new-file.md",
  "type": "file",
  "path": "/characters/protagonists/new-file.md",
  "parent_id": "ft_2",
  "document_id": "doc_456",
  "icon": null,
  "tags": [],
  "word_count": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### Update File Tree Item

```http
PUT /api/projects/{project_id}/file-tree/{item_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "updated-folder-name",
  "tags": ["new-tag"]
}

Response 200:
{
  "id": "ft_1",
  "name": "updated-folder-name",
  "type": "folder",
  "path": "/characters/updated-folder-name",
  "parent_id": null,
  "children": [],
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T13:00:00Z"
}
```

### Move File Tree Item

```http
PUT /api/projects/{project_id}/file-tree/{item_id}/move
Authorization: Bearer {token}
Content-Type: application/json

{
  "new_parent_id": "ft_new_parent",
  "new_position": 0
}

Response 200:
{
  "id": "ft_3",
  "name": "elara.md",
  "type": "file",
  "path": "/new-path/elara.md",
  "parent_id": "ft_new_parent",
  "document_id": "doc_123",
  "icon": "User",
  "tags": ["fire-magic", "trauma"],
  "word_count": 1200,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T14:00:00Z"
}
```

### Delete File Tree Item

```http
DELETE /api/projects/{project_id}/file-tree/{item_id}
Authorization: Bearer {token}

Response 200:
{
  "message": "File tree item deleted successfully."
}

Response 404:
{
  "error": "item_not_found",
  "message": "File tree item not found or access denied."
}
```

## Document Management

### Get Document by ID

```http
GET /api/documents/{document_id}
Authorization: Bearer {token}

Response 200:
{
  "id": "doc_123",
  "project_id": "prj_123",
  "title": "Elara's Character Profile",
  "path": "/characters/protagonists/elara.md",
  "tags": ["character", "magic"],
  "word_count": 1200,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z",
  "version": "1.0.0",
  "is_locked": false,
  "locked_by": null,
  "file_tree_id": "ft_3",
  "content": {
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "Elara is a powerful fire mage with a mysterious past."
          }
        ]
      }
    ]
  }
}
```

### Create Document

```http
POST /api/documents
Authorization: Bearer {token}
Content-Type: application/json

{
  "project_id": "prj_123",
  "title": "New Chapter",
  "path": "/chapters/chapter-1.md",
  "content": {
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "This is the content of the new chapter."
          }
        ]
      }
    ]
  },
  "tags": ["chapter", "draft"],
  "file_tree_parent_id": "ft_1"
}

Response 201:
{
  "id": "doc_456",
  "project_id": "prj_123",
  "title": "New Chapter",
  "path": "/chapters/chapter-1.md",
  "tags": ["chapter", "draft"],
  "word_count": 10,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "version": "1.0.0",
  "is_locked": false,
  "locked_by": null,
  "file_tree_id": "ft_1",
  "content": {
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "This is the content of the new chapter."
          }
        ]
      }
    ]
  }
}
```

### Update Document

```http
PUT /api/documents/{document_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Updated Chapter Title",
  "content": {
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "This is the updated content of the chapter."
          }
        ]
      }
    ]
  },
  "tags": ["chapter", "final"],
  "version": "1.1.0"
}

Response 200:
{
  "id": "doc_456",
  "project_id": "prj_123",
  "title": "Updated Chapter Title",
  "path": "/chapters/chapter-1.md",
  "tags": ["chapter", "final"],
  "word_count": 12,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T13:00:00Z",
  "version": "1.1.0",
  "is_locked": false,
  "locked_by": null,
  "file_tree_id": "ft_1",
  "content": {
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "This is the updated content of the chapter."
          }
        ]
      }
    ]
  }
}
```

### Delete Document

```http
DELETE /api/documents/{document_id}
Authorization: Bearer {token}

Response 200:
{
  "success": true,
  "message": "Document deleted successfully."
}

Response 404:
{
  "error": "document_not_found",
  "message": "Document not found or access denied"
}
```

## LLM Management

### Chat Completion

```http
POST /api/llm/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "provider": "openai",
  "model": "gpt-4o",
  "messages": [
    { "role": "user", "content": "Hello, how are you?" }
  ],
  "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "temperature": 0.7,
  "max_tokens": 100,
  "thinking": "low",
  "stream": false,
  "trace_id": "trace_123",
  "metadata": { "user_preference": "concise" }
}

Response 200:
{
  "content": "I am an AI assistant, how can I help you?",
  "model": "gpt-4o",
  "chunk_type": "content",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  },
  "metadata": { "request_latency_ms": 200 }
}
```

### Stream Chat Completion

```http
POST /api/llm/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "provider": "anthropic",
  "model": "claude-3-opus-20240229",
  "messages": [
    { "role": "user", "content": "Tell me a story." }
  ],
  "stream": true
}

Response 200 (Server-Sent Events):

```text
data: {"content": "Once upon a time", "model": "claude-3-opus-20240229", "chunk_type": "content", "is_final": false}

data: {"content": "there was a princess", "model": "claude-3-opus-202402029", "chunk_type": "content", "is_final": false}

data: {"content": "", "model": "claude-3-opus-20240229", "chunk_type": "content", "is_final": true}

```

### Validate API Key

```http
POST /api/llm/validate-key
Authorization: Bearer {token}
Content-Type: application/json

{
  "provider": "openai",
  "api_key": "sk-testkey",
  "test_model": "gpt-3.5-turbo"
}

Response 200 (Valid):
{
  "provider": "openai",
  "is_valid": true,
  "validation_status": "valid",
  "message": "API key is valid and working",
  "tested_with_model": "gpt-3.5-turbo"
}

Response 200 (Invalid):
{
  "provider": "openai",
  "is_valid": false,
  "validation_status": "invalid",
  "message": "API key validation failed: Incorrect API key",
  "tested_with_model": "gpt-3.5-turbo",
  "error_details": "Authentication error"
}
```

### Store API Key

```http
POST /api/llm/store-key
Authorization: Bearer {token}
Content-Type: application/json

{
  "provider": "openai",
  "api_key": "sk-stored-testkey",
  "validate_key": true,
  "provider_metadata": { "region": "us-east" }
}

Response 200:
{
  "provider": "openai",
  "validation_status": "valid",
  "last_validated_at": "2025-01-01T15:00:00Z",
  "provider_metadata": { "region": "us-east" },
  "message": "API key stored and validated successfully",
  "created_at": "2025-01-01T15:00:00Z",
  "updated_at": "2025-01-01T15:00:00Z"
}
```

### Delete API Key

```http
DELETE /api/llm/keys/{provider}
Authorization: Bearer {token}

Response 200:
{
  "provider": "openai",
  "deleted": true,
  "message": "API key for provider openai deleted successfully."
}
```

### List User API Keys

```http
GET /api/llm/keys
Authorization: Bearer {token}

Response 200:
{
  "api_keys": [
    {
      "provider": "openai",
      "validation_status": "valid",
      "last_validated_at": "2025-01-01T15:00:00Z",
      "provider_metadata": { "region": "us-east" },
      "message": "",
      "created_at": "2025-01-01T15:00:00Z",
      "updated_at": "2025-01-01T15:00:00Z"
    }
  ],
  "total_keys": 1
}
```

### List Providers

```http
GET /api/llm/providers
Authorization: Bearer {token}
Query Parameters:
  - include_models: boolean (default: true)

Response 200:
{
  "providers": [
    {
      "provider_id": "openai",
      "display_name": "OpenAI",
      "api_key_format_hint": "sk-...",
      "default_model": "gpt-4o",
      "models": [
        {
          "model_name": "gpt-4o",
          "provider": "openai",
          "display_name": "GPT-4o",
          "description": "OpenAI's most advanced, multimodal flagship model.",
          "capabilities": ["reasoning", "vision", "tool_use", "structured_output"],
          "input_token_limit": 128000,
          "output_token_limit": 4096,
          "default_temperature": 0.7,
          "supports_thinking": true,
          "thinking_budget_min": 10,
          "thinking_budget_max": 500,
          "input_cost_per_million": 5.0,
          "output_cost_per_million": 15.0
        }
      ]
    }
  ],
  "total_providers": 1,
  "total_models": 1
}
```

### List Models

```http
GET /api/llm/models
Authorization: Bearer {token}
Query Parameters:
  - provider: string (optional) - filter by provider ID (e.g., 'openai')
  - include_capabilities: boolean (default: true)

Response 200:
{
  "models": [
    {
      "model_name": "gpt-4o",
      "provider": "openai",
      "display_name": "GPT-4o",
      "description": "OpenAI's most advanced, multimodal flagship model.",
      "capabilities": ["reasoning", "vision", "tool_use", "structured_output"],
      "input_token_limit": 128000,
      "output_token_limit": 4096,
      "default_temperature": 0.7,
      "supports_thinking": true,
      "thinking_budget_min": 10,
      "thinking_budget_max": 500,
      "input_cost_per_million": 5.0,
      "output_cost_per_million": 15.0
    }
  ],
  "total_models": 1,
  "provider_filter": "openai"
}
```

## Health Check

### Ping

```http
GET /api/health/ping

Response 200:
{
  "message": "pong"
}
```

### Status

```http
GET /api/health/status

Response 200:
{
  "status": "healthy (memory fallback)",
  "service": "shuscribe-api",
  "version": "0.1.0",
  "database": "healthy (memory fallback)",
  "database_type": "memory",
  "timestamp": "2025-01-01T16:00:00.000000Z"
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
ws://localhost:3001/api/ws/projects/{project_id}

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