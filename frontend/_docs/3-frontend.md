# ShuScribe Backend MVP Technical Specification

**Context-Aware Fiction Writing Platform - Backend MVP**

_Practical technical planning for FastAPI + Supabase + AI Services_

---

## Core MVP Features

### What We're Actually Building

1. **Project data API** - Load complete project data (documents + tags) in single request
2. **Document CRUD API** - Create, read, update, delete documents via REST
3. **Reference extraction** - Parse saved documents for @-references and tags
4. **Auth middleware** - Validate Supabase JWT tokens
5. **Project management** - Basic project and file tree operations
6. **Mock AI endpoints** - Placeholder AI chat/context endpoints

### What We're NOT Building Yet

- Real AI chat implementation (just mock responses)
- Real-time collaboration endpoints
- Complex search/filtering (frontend handles local search)
- File upload/storage management
- Advanced caching strategies
- Performance optimizations

---

## Technology Stack

- **FastAPI** for REST API
- **Supabase** for database + auth validation
- **SQLAlchemy** with dependency injection pattern
- **Pydantic** for request/response models
- **Python-dotenv** for environment management
- **Pytest** for testing
- **Uvicorn** for development server

---

## Architecture Overview

### API Structure

```
/api/v1/
├── auth/                   # JWT validation, user info
├── projects/               # Project CRUD
│   └── {project_id}/
│       ├── data/           # Complete project data (documents + tags)
│       └── documents/      # Document CRUD operations
└── ai/                     # Mock AI endpoints (future)
```

### Dependency Injection Pattern

```
FastAPI App
├── Database Service (Injectable)
├── Auth Service (Injectable) 
├── Reference Service (Injectable)
└── AI Service (Injectable - Mock)
```

**Why Dependency Injection:**

- Easy to swap database implementations
- Simple testing with mock services
- Clean separation of concerns
- Future-proof for scaling

---

## Core Technical Components

### 1. Database Layer with Dependency Injection

**Database Service Interface:**

- Abstract base class defining database operations
- Concrete implementation for Supabase
- Easy to swap for PostgreSQL, SQLite, etc.

**Key Operations:**

- Projects: CRUD, list user projects
- Documents: CRUD, list by project, search by path
- References: Extract, validate, get suggestions

**Models (SQLAlchemy/Pydantic):**

```python
# Conceptual models - we'll define these properly
Project: id, user_id, title, created_at, updated_at
Document: id, project_id, path, title, content, tags, word_count
DocumentReference: source_id, target_path, position, is_valid
```

### 2. Authentication Middleware

**JWT Validation:**

- Validate Supabase JWT tokens from frontend
- Extract user ID from token
- Protect routes that need authentication
- Handle token expiry gracefully

**Auth Flow:**

1. Frontend sends JWT token in Authorization header
2. Middleware validates token with Supabase
3. Extract user info and attach to request
4. Route handlers can access current user

### 3. Project Data API

**Complete Project Loading:**

- `GET /projects/{id}/data` - Return all documents, metadata, tags in single response
- Optimized for client-side index building
- Include document relationships and reference mappings
- Efficient serialization for fast frontend processing

**Core Endpoints:**

- `GET /projects/{id}/data` - Complete project data for client-side indexing
- `GET /documents/{id}` - Get single document (for editing)
- `POST /projects/{id}/documents` - Create document
- `PUT /documents/{id}` - Update document content
- `DELETE /documents/{id}` - Delete document

**Key Features:**

- Single request loads entire project for client-side search
- Auto-extract references and tags on document save
- Update project index when documents change
- Handle concurrent edits (basic last-write-wins)

### 4. Reference & Tag Processing

**Reference Extraction:**

- Parse document content for @-references on save
- Extract different reference types (file, tag)
- Build reference mappings for project data response
- Track document relationships and dependencies

**Tag Management:**

- Extract and manage document tags
- Build tag-to-document mappings
- Support multiple tags per document
- Include in project data for client-side filtering

**Key Endpoints:**

- `POST /projects/{id}/references/validate` - Validate references (on demand)
- `GET /documents/{id}/references` - Get document reference data

**Processing Logic:**

- File references: `@characters/elara` → validate path exists
- Tag references: `@fire-magic` → build tag-document mappings
- Reference integrity checking across project
- Efficient data structure for frontend index building

### 5. Mock AI Services

**Purpose:** Provide API structure for future AI implementation

**Endpoints:**

- `POST /projects/{id}/ai/chat` - Mock chat responses
- `GET /documents/{id}/ai/context` - Extract context for AI
- `POST /documents/{id}/ai/suggestions` - Mock writing suggestions

**Mock Implementation:**

- Return hardcoded responses based on input
- Extract document references for context
- Provide realistic response structure
- Foundation for real AI integration later

---

## Implementation Steps

### Step 1: Project Setup

- Initialize FastAPI project with proper structure
- Set up virtual environment and dependencies
- Configure environment variables for Supabase
- Set up basic logging and error handling
- Create development database schema

### Step 2: Database Layer

- Define SQLAlchemy models for Project, Document, Reference
- Create database service interface (abstract base class)
- Implement Supabase database service
- Set up dependency injection container
- Create basic CRUD operations

### Step 3: Authentication

- Create JWT validation middleware
- Set up Supabase client for token verification
- Implement user extraction from tokens
- Add auth decorators/dependencies for routes
- Test auth flow with frontend

### Step 4: Project Data API

- Implement complete project data endpoint
- Optimize response for client-side index building
- Include all documents, metadata, tags, and relationships
- Handle efficient serialization for large projects
- Test frontend integration with local search

### Step 5: Reference & Tag Processing

- Create reference extraction from document content
- Build tag management and document relationships
- Implement reference validation logic
- Add reference integrity checking
- Support project data updates when content changes

### Step 6: Mock AI Integration

- Create placeholder AI service interface
- Implement mock chat endpoint with hardcoded responses
- Build context extraction from document references
- Add suggestion endpoint structure
- Prepare for future real AI integration

### Step 7: Testing & Polish

- Set up pytest with database fixtures
- Add unit tests for core business logic
- Create integration tests for API endpoints
- Add proper error handling and validation
- Configure for deployment

---

## Key Technical Challenges

### 1. Efficient Project Data Serialization

- Optimize complete project data response for large projects
- Efficient JSON serialization of documents, tags, references
- Structure data for fast client-side index building
- Handle projects with hundreds of documents

### 2. Reference & Tag Extraction

- Parse @-references from ProseMirror JSON content
- Handle different reference types (file, tag, complex)
- Extract and manage document tag systems
- Build efficient relationship mappings

### 3. Database Abstraction

- Design clean interface that works with different databases
- Handle Supabase-specific features while keeping abstraction
- Manage database connections and transactions
- Structure for easy testing and mocking

### 4. Content Processing Pipeline

- Parse ProseMirror document structure efficiently
- Extract text, references, and metadata
- Handle different document formats and versions
- Maintain content integrity during operations

---

## Database Schema Design

### Core Tables

```sql
-- Basic schema structure (we'll define properly later)
users (id, supabase_user_id, email, created_at)
projects (id, user_id, title, description, created_at, updated_at)
documents (id, project_id, path, title, content_json, tags[], word_count, updated_at)
document_references (source_doc_id, target_path, reference_type, position, is_valid)
```

### Key Relationships

- User → Projects (one-to-many)
- Project → Documents (one-to-many, hierarchical paths)
- Document → References (one-to-many, extracted from content)

### Indexes for Performance

- Documents: project_id, path (for file tree queries)
- References: source_doc_id, target_path (for validation)
- Full-text search on document content (for suggestions)

---

## API Design Patterns

### Request/Response Models

- Pydantic models for all API inputs/outputs
- Consistent error response format
- Proper HTTP status codes
- Request validation with clear error messages

### Error Handling

- Custom exception classes for business logic errors
- Global exception handler for consistent responses
- Proper logging of errors for debugging
- User-friendly error messages

### Dependency Injection Structure

```python
# Conceptual structure
@app.get("/documents/{doc_id}")
async def get_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: DatabaseService = Depends(get_database),
    references: ReferenceService = Depends(get_reference_service)
):
    # Route logic here
```

---

## Things to Keep in Mind (But Don't Build Yet)

### Future Enhancements:

- **Real AI integration** with OpenAI/Anthropic APIs
- **Real-time collaboration** with WebSocket support
- **Advanced search** with full-text and semantic search
- **File storage** for images, attachments
- **Performance optimizations** (caching, database optimization)
- **Background tasks** for heavy processing
- **Rate limiting** and API security
- **Monitoring and observability**

### Architectural Decisions:

- Database service pattern supports future scaling
- AI service interface ready for real implementation
- Reference system designed for complex query types
- API structure supports real-time features later

---

## Success Criteria

**MVP backend is successful when:**

- Frontend can authenticate users via Supabase JWT
- Complete project data loads efficiently in single request
- Document CRUD operations work reliably
- Reference and tag extraction processes documents correctly
- Project data structure supports fast client-side search
- Mock AI endpoints return structured responses

**Core API Flow:**

1. Frontend sends JWT → Backend validates → User authenticated
2. Load project → Backend returns complete project data → Frontend builds index
3. Create/edit document → Content saved with extracted references and tags
4. Frontend uses local index for instant @-reference autocomplete
5. AI panel requests → Backend returns mock but structured responses

---

This specification focuses on building a solid, testable API foundation that supports the frontend's @-reference system while preparing for future AI and collaboration features.