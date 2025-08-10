# Backend Architecture

**Clean Architecture with Repository Pattern + Dependency Injection**

## Implementation Status

### ✅ **IMPLEMENTED**
- **FastAPI REST API** - Projects, documents, tags, file tree, LLM endpoints
- **Repository Pattern** - Interface-based dependency injection with memory + database backends  
- **Authentication** - Supabase JWT validation and user context extraction
- **Document Management** - ProseMirror JSON content with word count tracking
- **Tag System** - Many-to-many relationships with categories and usage tracking
- **LLM Integration** - Self-hosted Portkey Gateway with multiple providers
- **WikiGen Agent System** - AI-powered wiki generation with spoiler prevention

### ❌ **NOT IMPLEMENTED**
- Real-time collaboration (WebSockets)
- File uploads (images, attachments)
- Advanced search (semantic search)
- Publishing system (public hosting)

## Technology Stack

- **FastAPI** - REST API with automatic OpenAPI documentation
- **SQLAlchemy** - ORM with async support and proper relationships
- **Repository Pattern** - Interface-based dependency injection for clean architecture
- **Supabase** - PostgreSQL database with auth token validation
- **Portkey Gateway** - Self-hosted LLM proxy supporting multiple providers

## Architecture Pattern

### Repository Pattern with Dependency Injection
```python
# Factory creates appropriate backend based on configuration
repositories = create_repositories(backend=settings.DATABASE_BACKEND)

# FastAPI endpoints use dependency injection
@router.get("/{project_id}")
async def get_project(
    project_id: str,
    repositories: RepositoryContainer = Depends(get_repositories)
):
    project = await repositories.project.get_by_id(project_id)
    return ApiResponse.success(project_to_response(project))
```

**Two Backend Implementations:**
- **Memory Backend**: Pure Python classes for testing (complete isolation)
- **Database Backend**: PostgreSQL with async SQLAlchemy relationships

### Core Models

**Domain Models** (pure dataclasses):
```python
@dataclass
class Project:
    id: str
    title: str
    description: str
    owner_id: Optional[str]
    word_count: int
    document_count: int
    tags: List[str]
    created_at: Optional[datetime]
```

**SQLAlchemy Models** (ORM):
- Relationships, indexes, JSON fields
- Mapped via dedicated mapper classes

### Authentication Strategy
- **Frontend-First**: Supabase Auth handled entirely in frontend
- **Backend Trust**: Backend validates JWT tokens for user context
- **Environment-Aware**: Development mode allows unfiltered access

## Key Endpoints

```
GET/POST/PUT/DELETE  /projects
GET/POST/PUT/DELETE  /projects/{id}/documents  
GET/POST/PUT/DELETE  /projects/{id}/file-tree
GET/POST/PUT/DELETE  /projects/{id}/tags
POST                 /projects/{id}/llm/generate
```

## Environment Configuration

**Backend Selection**:
- **Memory**: Pure Python, perfect for testing, no persistence
- **Database**: PostgreSQL + Supabase, production environment

```bash
# Environment behavior configuration
ENVIRONMENT=development|testing|production
DATABASE_BACKEND=memory|database
DATABASE_URL=postgresql://...     # Supabase PostgreSQL

# LLM configuration
PORTKEY_BASE_URL=http://localhost:8787
```

## Development Commands

```bash
cd backend
uv sync && source .venv/bin/activate
uv run hypercorn src.main:app --reload --bind "[::]:8000"
uv run pytest                              # Run tests
uv run black . && uv run isort .           # Format code
```

The backend provides a clean, well-architected foundation with comprehensive testing and seamless frontend integration.