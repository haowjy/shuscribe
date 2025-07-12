# ShuScribe API Reference

Complete API documentation for the ShuScribe backend service.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Field Naming Conventions](#field-naming-conventions)
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
- The backend **extracts** tokens but does **not validate** them
- Token validation is handled by the frontend (Supabase Auth)
- The backend trusts the frontend's authentication state
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

## Field Naming Conventions

The API handles field name conversion between frontend (camelCase) and backend (snake_case):

| Frontend (camelCase) | Backend (snake_case) | Example |
|---------------------|---------------------|---------|
| `projectId` | `project_id` | Project identifier |
| `createdAt` | `created_at` | Creation timestamp |
| `updatedAt` | `updated_at` | Update timestamp |
| `wordCount` | `word_count` | Document word count |
| `documentCount` | `document_count` | Project document count |
| `isLocked` | `is_locked` | Document lock status |
| `fileTreeId` | `file_tree_id` | File tree reference |

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
      hasMore: boolean;
      nextOffset?: number;
    };
  };
}

interface ProjectSummary {
  id: string;
  title: string;
  description: string;
  wordCount: number;
  documentCount: number;
  createdAt: string;
  updatedAt: string;
  tags: string[];
  collaborators: ProjectCollaborator[];
}

interface ProjectCollaborator {
  userId: string;
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
    autoSaveInterval: number;  // milliseconds
    wordCountTarget: number;
    backupEnabled: boolean;
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
    "wordCount": 15420,
    "documentCount": 8,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-15T10:30:00Z",
    "tags": ["sci-fi", "time-travel", "adventure"],
    "collaborators": [
      {
        "userId": "user-123",
        "role": "owner",
        "name": "Jane Author",
        "avatar": "https://example.com/avatar.jpg"
      }
    ],
    "settings": {
      "autoSaveInterval": 30000,
      "wordCountTarget": 80000,
      "backupEnabled": true
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
    totalFiles: number;
    totalFolders: number;
    lastUpdated: string;
  };
}

interface FileTreeItem {
  id: string;
  name: string;
  type: "file" | "folder";
  path: string;
  parentId?: string;
  children?: FileTreeItem[];
  
  // File-specific properties
  documentId?: string;
  icon?: string;
  tags: string[];
  wordCount?: number;
  
  // Timestamps
  createdAt: string;
  updatedAt: string;
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
    autoSaveInterval?: number;
    wordCountTarget?: number;
    backupEnabled?: boolean;
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
    "autoSaveInterval": 30000,
    "wordCountTarget": 100000,
    "backupEnabled": true
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
    autoSaveInterval?: number;
    wordCountTarget?: number;
    backupEnabled?: boolean;
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
  projectId: string;
  title: string;
  path: string;
  content: ProseMirrorContent;
  tags: string[];
  wordCount: number;
  createdAt: string;
  updatedAt: string;
  version: string;
  isLocked: boolean;
  lockedBy?: string;
  fileTreeId?: string;
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
    "projectId": "project-456",
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
    "wordCount": 1247,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-15T10:30:00Z",
    "version": "1.2.0",
    "isLocked": false,
    "lockedBy": null,
    "fileTreeId": "tree-item-789"
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
  projectId: string;
  title: string;
  path: string;
  content?: ProseMirrorContent;
  tags?: string[];
  fileTreeParentId?: string;
}
```

**Example Request**:
```json
{
  "projectId": "550e8400-e29b-41d4-a716-446655440000",
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
  "fileTreeParentId": "chapters-folder-id"
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
  maxTokens?: number;
  stream?: boolean;
  thinking?: "low" | "medium" | "high";
  traceId?: string;
  metadata?: Record<string, any>;
  apiKey?: string;  // Optional: use temporary API key instead of stored key
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
  "maxTokens": 500,
  "stream": false
}
```

**Non-Streaming Response**:
```typescript
interface ChatCompletionResponse {
  content: string;
  model: string;
  chunkType: "content" | "thinking";
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  metadata: Record<string, any>;
}
```

**Streaming Response**:
When `stream: true`, returns Server-Sent Events with `Content-Type: text/event-stream`:

```
data: {"data": {"content": "The", "model": "gpt-4", "chunkType": "content", "isFinal": false}, "status": 200}

data: {"data": {"content": " year", "model": "gpt-4", "chunkType": "content", "isFinal": false}, "status": 200}

data: {"data": {"content": "", "model": "gpt-4", "chunkType": "content", "isFinal": true}, "status": 200}
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
  apiKey: string;
  testModel?: string;  // Optional: specific model to test with
}
```

**Response**:
```typescript
interface APIKeyValidationResponse {
  provider: string;
  isValid: boolean;
  validationStatus: "valid" | "invalid" | "error";
  message: string;
  testedWithModel: string;
  errorDetails?: string;
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
  apiKey: string;
  validateKey?: boolean;  // Default: false
  providerMetadata?: Record<string, any>;
}
```

**Response**:
```typescript
interface StoredAPIKeyResponse {
  provider: string;
  validationStatus: string;
  lastValidatedAt?: string;
  providerMetadata?: Record<string, any>;
  message: string;
  createdAt: string;
  updatedAt: string;
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
  apiKeys: StoredAPIKeyResponse[];
  totalKeys: number;
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
| `includeModels` | boolean | true | Include model details for each provider |

**Response**:
```typescript
interface ListProvidersResponse {
  providers: ProviderResponse[];
  totalProviders: number;
  totalModels: number;
}

interface ProviderResponse {
  providerId: string;
  displayName: string;
  apiKeyFormatHint: string;
  defaultModel: string;
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
| `includeCapabilities` | boolean | true | Include model capabilities |

**Response**:
```typescript
interface ListModelsResponse {
  models: ModelCapabilityResponse[];
  totalModels: number;
  providerFilter?: string;
}

interface ModelCapabilityResponse {
  modelName: string;
  provider: string;
  displayName: string;
  description?: string;
  capabilities: string[];
  inputTokenLimit: number;
  outputTokenLimit: number;
  defaultTemperature: number;
  supportsThinking: boolean;
  thinkingBudgetMin?: number;
  thinkingBudgetMax?: number;
  inputCostPerMillion: number;
  outputCostPerMillion: number;
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
     "projectId": "{{project_id_from_step_3}}",
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
     "apiKey": "your-openai-api-key"
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