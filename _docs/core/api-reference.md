# ShuScribe API Reference

Complete API documentation for the ShuScribe backend service.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Health Endpoints](#health-endpoints)
- [Projects API](#projects-api)
- [Documents API](#documents-api)
- [LLM API](#llm-api)
- [Testing Guide](#testing-guide)

## Overview

**Base URL**: `http://localhost:8000/api/v1`  
**API Version**: v1  
**Content-Type**: `application/json`  
**Date Format**: ISO 8601 (`2024-01-15T10:30:00Z`)

The ShuScribe API is a RESTful service that provides endpoints for managing fiction writing projects, documents, and AI-powered features. All endpoints return data in a consistent `ApiResponse<T>` wrapper format.

## Authentication

Most endpoints require authentication using Bearer tokens from Supabase Auth.

### Required Header
```http
Authorization: Bearer <your-supabase-jwt-token>
```

### Authentication Notes
- The backend **validates** Supabase JWT tokens from the Authorization header
- Token validation ensures security and user identification
- Authentication is handled via Supabase Auth on the frontend
- Some endpoints like `/health/ping` do not require authentication

## Response Format

All API responses use a consistent `ApiResponse<T>` wrapper:

```typescript
interface ApiResponse<T> {
  data: T | null;           // Response data (null on error)
  error: string | null;     // Error message (null on success)
  message: string | null;   // Optional additional message
  status: number;           // HTTP status code
}
```

### Success Response Example
```json
{
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "My Story Project"
  },
  "error": null,
  "message": null,
  "status": 200
}
```

### Error Response Example
```json
{
  "data": null,
  "error": "Project with ID abc123 not found",
  "message": "Project with ID abc123 not found",
  "status": 404
}
```

## Error Handling

### Common HTTP Status Codes

| Status | Meaning | Description |
|--------|---------|-------------|
| 200    | OK | Request successful |
| 201    | Created | Resource created successfully |
| 400    | Bad Request | Invalid request data |
| 401    | Unauthorized | Authentication required or invalid |
| 403    | Forbidden | Access denied |
| 404    | Not Found | Resource not found |
| 500    | Internal Server Error | Server error |

### Error Response Structure
```typescript
interface ApiError {
  error: string;           // Main error message
  message: string;         // Detailed error description
  details?: object;        // Additional error context (optional)
  requestId?: string;      // Request tracking ID (optional)
}
```

## Health Endpoints

### Ping Check

Simple health check for service availability.

```http
GET /api/v1/health/ping
```

**Authentication**: None required

**Response**:
```json
{
  "message": "pong"
}
```

### Status Check

Detailed service status including database health.

```http
GET /api/v1/health/status
```

**Authentication**: None required

**Response**:
```json
{
  "status": "healthy (memory fallback)",
  "service": "shuscribe-api",
  "version": "0.1.0",
  "database": "healthy (memory fallback)",
  "database_type": "memory",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Projects API

### List Projects

Retrieve paginated list of projects with sorting options.

```http
GET /api/v1/projects?limit=20&offset=0&sort=updated_at&order=desc
```

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | number | 20 | Number of projects to return (1-100) |
| `offset` | number | 0 | Number of projects to skip |
| `sort` | string | "updated_at" | Sort field: "title", "created_at", "updated_at" |
| `order` | string | "desc" | Sort order: "asc", "desc" |

**Response**:
```typescript
interface ProjectListResponse {
  data: {
    projects: ProjectSummary[];
    pagination: {
      total: number;
      limit: number;
      offset: number;
      has_more: boolean;
      next_offset?: number;
    };
  };
}

interface ProjectSummary {
  id: string;
  title: string;
  description: string;
  word_count: number;
  document_count: number;
  created_at: string;
  updated_at: string;
  tags: string[];
  collaborators: ProjectCollaborator[];
}

interface ProjectCollaborator {
  user_id: string;
  role: "owner" | "editor" | "viewer";
  name: string;
  avatar?: string;
}
```

### Get Project Details

Retrieve complete project information by ID.

```http
GET /api/v1/projects/{projectId}
```

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `projectId` | string | Project UUID |

**Response**:
```typescript
interface ProjectDetails extends ProjectSummary {
  settings: {
    auto_save_interval: number;  // milliseconds
    word_count_target: number;
    backup_enabled: boolean;
  };
}
```

**Example Response**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "The Quantum Chronicles",
    "description": "A science fiction series about time travel",
    "word_count": 15420,
    "document_count": 8,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "tags": ["sci-fi", "time-travel", "adventure"],
    "collaborators": [
      {
        "user_id": "user-123",
        "role": "owner",
        "name": "Jane Author",
        "avatar": "https://example.com/avatar.jpg"
      }
    ],
    "settings": {
      "auto_save_interval": 30000,
      "word_count_target": 80000,
      "backup_enabled": true
    }
  },
  "error": null,
  "message": null,
  "status": 200
}
```

### Get Project File Tree

Retrieve hierarchical file tree structure for a project.

```http
GET /api/v1/projects/{projectId}/file-tree
```

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `projectId` | string | Project UUID |

**Response**:
```typescript
interface FileTreeResponse {
  fileTree: FileTreeItem[];
  metadata: {
    total_files: number;
    total_folders: number;
    last_updated: string;
  };
}

interface FileTreeItem {
  id: string;
  name: string;
  type: "file" | "folder";
  path: string;
  parent_id?: string;
  children?: FileTreeItem[];
  
  // File-specific properties
  document_id?: string;
  icon?: string;
  tags: string[];
  word_count?: number;
  
  // Timestamps
  created_at: string;
  updated_at: string;
}
```

### Create Project

Create a new project.

```http
POST /api/v1/projects
```

**Authentication**: Required

**Request Body**:
```typescript
interface CreateProjectRequest {
  title: string;
  description: string;
  tags?: string[];
  settings?: {
    auto_save_interval?: number;
    word_count_target?: number;
    backup_enabled?: boolean;
  };
}
```

**Example Request**:
```json
{
  "title": "My New Story",
  "description": "An epic fantasy adventure",
  "tags": ["fantasy", "adventure"],
  "settings": {
    "auto_save_interval": 30000,
    "word_count_target": 100000,
    "backup_enabled": true
  }
}
```

**Response**: Returns `ProjectDetails` with status 201

### Update Project

Update an existing project.

```http
PUT /api/v1/projects/{projectId}
```

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `projectId` | string | Project UUID |

**Request Body**:
```typescript
interface UpdateProjectRequest {
  title?: string;
  description?: string;
  tags?: string[];
  settings?: {
    auto_save_interval?: number;
    word_count_target?: number;
    backup_enabled?: boolean;
  };
}
```

**Response**: Returns updated `ProjectDetails`

### Delete Project

Delete a project and all associated data.

```http
DELETE /api/v1/projects/{projectId}
```

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `projectId` | string | Project UUID |

**Response**:
```json
{
  "data": {
    "message": "Project 550e8400-e29b-41d4-a716-446655440000 deleted successfully"
  },
  "error": null,
  "message": null,
  "status": 200
}
```

## Documents API

### Get Document

Retrieve a document with full content.

```http
GET /api/v1/documents/{documentId}
```

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `documentId` | string | Document UUID |

**Response**:
```typescript
interface DocumentResponse {
  id: string;
  project_id: string;
  title: string;
  path: string;
  content: ProseMirrorContent;
  tags: string[];
  word_count: number;
  created_at: string;
  updated_at: string;
  version: string;
  is_locked: boolean;
  locked_by?: string;
  file_tree_id?: string;
}

interface ProseMirrorContent {
  type: "doc";
  content: ProseMirrorNode[];
}

interface ProseMirrorNode {
  type: string;
  text?: string;
  content?: ProseMirrorNode[];
  attrs?: Record<string, any>;
  marks?: ProseMirrorMark[];
}

interface ProseMirrorMark {
  type: string;
  attrs?: Record<string, any>;
}
```

**Example Response**:
```json
{
  "data": {
    "id": "doc-123",
    "project_id": "project-456",
    "title": "Chapter 1: The Beginning",
    "path": "/chapters/chapter-01.md",
    "content": {
      "type": "doc",
      "content": [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "It was a dark and stormy night..."
            }
          ]
        }
      ]
    },
    "tags": ["chapter", "intro"],
    "word_count": 1247,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "version": "1.2.0",
    "is_locked": false,
    "locked_by": null,
    "file_tree_id": "tree-item-789"
  },
  "error": null,
  "message": null,
  "status": 200
}
```

### Create Document

Create a new document in a project.

```http
POST /api/v1/documents
```

**Authentication**: Required

**Request Body**:
```typescript
interface CreateDocumentRequest {
  project_id: string;
  title: string;
  path: string;
  content?: ProseMirrorContent;
  tags?: string[];
  file_tree_parent_id?: string;
}
```

**Example Request**:
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Chapter 2: The Discovery",
  "path": "/chapters/chapter-02.md",
  "content": {
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "The next morning brought unexpected revelations..."
          }
        ]
      }
    ]
  },
  "tags": ["chapter"],
  "file_tree_parent_id": "chapters-folder-id"
}
```

**Response**: Returns `DocumentResponse` with status 201

### Update Document

Update an existing document.

```http
PUT /api/v1/documents/{documentId}
```

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `documentId` | string | Document UUID |

**Request Body**:
```typescript
interface UpdateDocumentRequest {
  title?: string;
  content?: ProseMirrorContent;
  tags?: string[];
  version?: string;
}
```

**Response**: Returns updated `DocumentResponse`

**Notes**:
- Word count is automatically recalculated when content is updated
- Project word count is updated accordingly
- Document `updated_at` timestamp is automatically set

### Delete Document

Delete a document.

```http
DELETE /api/v1/documents/{documentId}
```

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `documentId` | string | Document UUID |

**Response**:
```json
{
  "data": {
    "success": true
  },
  "error": null,
  "message": null,
  "status": 200
}
```

## LLM API

### Chat Completion

Generate AI chat completion using various LLM providers.

```http
POST /api/v1/llm/chat
```

**Authentication**: Required

**Request Body**:
```typescript
interface ChatCompletionRequest {
  provider: "openai" | "anthropic" | "google" | "ollama";
  model: string;
  messages: LLMMessage[];
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
  thinking?: "low" | "medium" | "high";
  trace_id?: string;
  metadata?: Record<string, any>;
  api_key?: string;  // Optional: use temporary API key instead of stored key
}

interface LLMMessage {
  role: "system" | "user" | "assistant";
  content: string;
}
```

**Example Request**:
```json
{
  "provider": "openai",
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful writing assistant."
    },
    {
      "role": "user",
      "content": "Help me write a compelling opening for a sci-fi story."
    }
  ],
  "temperature": 0.7,
  "max_tokens": 500,
  "stream": false
}
```

**Non-Streaming Response**:
```typescript
interface ChatCompletionResponse {
  content: string;
  model: string;
  chunk_type: "content" | "thinking";
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  metadata: Record<string, any>;
}
```

**Streaming Response**:
When `stream: true`, returns Server-Sent Events with `Content-Type: text/event-stream`:

```
data: {"data": {"content": "The", "model": "gpt-4", "chunk_type": "content", "is_final": false}, "status": 200}

data: {"data": {"content": " year", "model": "gpt-4", "chunk_type": "content", "is_final": false}, "status": 200}

data: {"data": {"content": "", "model": "gpt-4", "chunk_type": "content", "is_final": true}, "status": 200}
```

### Validate API Key

Test an API key without storing it.

```http
POST /api/v1/llm/validate-key
```

**Authentication**: Required

**Request Body**:
```typescript
interface ValidateAPIKeyRequest {
  provider: "openai" | "anthropic" | "google";
  api_key: string;
  test_model?: string;  // Optional: specific model to test with
}
```

**Response**:
```typescript
interface APIKeyValidationResponse {
  provider: string;
  is_valid: boolean;
  validation_status: "valid" | "invalid" | "error";
  message: string;
  tested_with_model: string;
  error_details?: string;
}
```

### Store API Key

Encrypt and store an API key for future use.

```http
POST /api/v1/llm/store-key
```

**Authentication**: Required

**Request Body**:
```typescript
interface StoreAPIKeyRequest {
  provider: "openai" | "anthropic" | "google";
  api_key: string;
  validate_key?: boolean;  // Default: false
  provider_metadata?: Record<string, any>;
}
```

**Response**:
```typescript
interface StoredAPIKeyResponse {
  provider: string;
  validation_status: string;
  last_validated_at?: string;
  provider_metadata?: Record<string, any>;
  message: string;
  created_at: string;
  updated_at: string;
}
```

### Delete API Key

Remove a stored API key.

```http
DELETE /api/v1/llm/keys/{provider}
```

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `provider` | string | LLM provider: "openai", "anthropic", "google" |

**Response**:
```typescript
interface DeleteAPIKeyResponse {
  provider: string;
  deleted: boolean;
  message: string;
}
```

### List User API Keys

Retrieve all stored API keys (without decrypting them).

```http
GET /api/v1/llm/keys
```

**Authentication**: Required

**Response**:
```typescript
interface ListUserAPIKeysResponse {
  api_keys: StoredAPIKeyResponse[];
  total_keys: number;
}
```

### List LLM Providers

Get available LLM providers and their models.

```http
GET /api/v1/llm/providers?includeModels=true
```

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_models` | boolean | true | Include model details for each provider |

**Response**:
```typescript
interface ListProvidersResponse {
  providers: ProviderResponse[];
  total_providers: number;
  total_models: number;
}

interface ProviderResponse {
  provider_id: string;
  display_name: string;
  api_key_format_hint: string;
  default_model: string;
  models: ModelCapabilityResponse[];
}
```

### List Models

Get available models, optionally filtered by provider.

```http
GET /api/v1/llm/models?provider=openai&includeCapabilities=true
```

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `provider` | string | - | Filter by specific provider |
| `include_capabilities` | boolean | true | Include model capabilities |

**Response**:
```typescript
interface ListModelsResponse {
  models: ModelCapabilityResponse[];
  total_models: number;
  provider_filter?: string;
}

interface ModelCapabilityResponse {
  model_name: string;
  provider: string;
  display_name: string;
  description?: string;
  capabilities: string[];
  input_token_limit: number;
  output_token_limit: number;
  default_temperature: number;
  supports_thinking: boolean;
  thinking_budget_min?: number;
  thinking_budget_max?: number;
  input_cost_per_million: number;
  output_cost_per_million: number;
}
```

## Testing Guide

### Insomnia/Postman Collection

To test the API effectively, set up the following environment variables:

```
base_url=http://localhost:8000/api/v1
auth_token=your-supabase-jwt-token
```

### Example Test Sequence

1. **Health Check**:
   ```http
   GET {{base_url}}/health/ping
   ```

2. **List Projects**:
   ```http
   GET {{base_url}}/projects
   Authorization: Bearer {{auth_token}}
   ```

3. **Create Project**:
   ```http
   POST {{base_url}}/projects
   Authorization: Bearer {{auth_token}}
   Content-Type: application/json
   
   {
     "title": "Test Project",
     "description": "A test project for API validation"
   }
   ```

4. **Create Document**:
   ```http
   POST {{base_url}}/documents
   Authorization: Bearer {{auth_token}}
   Content-Type: application/json
   
   {
     "project_id": "{{project_id_from_step_3}}",
     "title": "Test Document",
     "path": "/test.md",
     "content": {
       "type": "doc",
       "content": [
         {
           "type": "paragraph",
           "content": [{"type": "text", "text": "Hello, world!"}]
         }
       ]
     }
   }
   ```

5. **LLM Chat**:
   ```http
   POST {{base_url}}/llm/chat
   Authorization: Bearer {{auth_token}}
   Content-Type: application/json
   
   {
     "provider": "openai",
     "model": "gpt-3.5-turbo",
     "messages": [
       {"role": "user", "content": "Say hello"}
     ],
     "api_key": "your-openai-api-key"
   }
   ```

### Common Issues

1. **401 Unauthorized**: Check that your Bearer token is valid and properly formatted
2. **404 Not Found**: Verify the endpoint URL and that referenced resources exist
3. **400 Bad Request**: Check request body format and required fields
4. **500 Internal Server Error**: Check server logs for database connectivity issues

### Database Seeding

The development server automatically seeds test data when `ENABLE_DATABASE_SEEDING=true` in `.env`. This creates:
- 2 sample projects
- 35 sample documents
- 45 file tree items

You can use this seeded data for testing API endpoints without creating your own test data.