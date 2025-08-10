# CLAUDE.md - Backend Development Guide

This guide provides backend-specific information for working with the ShuScribe backend.

## 🔗 Multi-Repository Context

This is the **backend-specific** guide. For complete project context, see:
- **Main Guide**: `/CLAUDE.md` - Overall project philosophy and coordination
- **Frontend Guide**: `/frontend/CLAUDE-frontend.md` - Frontend patterns and API contract definition
- **Backend Architecture**: [`/_docs/backend/overview.md`](../_docs/backend/overview.md) - Detailed backend architecture

## Backend-First Integration

**Core Principle**: The backend domain models are the **source of truth** for all data structures.

**Key Integration Points**:
- **Domain Models Authority**: Backend models in `src/database/interfaces/models/` define canonical structure
- **Frontend Alignment**: Frontend types must exactly match backend domain models
- **Response Format**: Backend `ApiResponse<T>` wrapper is the authoritative format
- **Authentication**: Backend trusts frontend auth tokens, extracts for context only
- **Field Naming**: Backend snake_case is authoritative; frontend maps via utilities

**⚠️ CRITICAL**: When modifying domain models, you MUST update the frontend types:
1. Update domain model in `src/database/interfaces/models/`
2. Update frontend types in `/frontend/src/lib/localdb/types.ts`
3. Update local data provider in `/frontend/src/lib/data/local-provider.ts`
4. Update seed data in `/frontend/src/lib/localdb/seeds.ts`

## Quick Start

```bash
# Setup environment
cd backend
uv sync && source .venv/bin/activate

# Start development server
uv run hypercorn src.main:app --reload --bind "[::]:8000"

# Run tests
uv run pytest                              # Minimal output
uv run pytest --cov=src --cov-report=html  # With coverage
uv run pytest --log-level=DEBUG            # Debug logs

# Code quality
uv run black . && uv run isort .           # Format code
```

## Architecture Patterns

### Repository Pattern
**Interface-based dependency injection** with multiple backend support:
```python
# Dependency injection in endpoints
@router.get("/{project_id}")
async def get_project(
    project_id: str,
    repositories: RepositoryContainer = Depends(get_repositories)
):
    project = await repositories.project.get_by_id(project_id)
    return ApiResponse.success(project)
```

**Two backends supported**:
- **`memory`**: In-memory repositories (testing)
- **`database`**: PostgreSQL with SQLAlchemy (production)

### Database Models
Core entities with proper relationships:
- **Project**: Universe container with hierarchical file tree
- **Document**: Rich content with ProseMirror JSON
- **Tag**: Many-to-many with categories and metadata
- **User**: Authentication and project ownership

### LLM Integration
- **Portkey Gateway**: Self-hosted gateway (Docker service)
- **Agent System**: WikiGen agents for AI-powered content generation
- **Spoiler Prevention**: Chapter-aware content safety
- **Model Catalog**: Configurable LLM providers and capabilities

## Key Endpoints

**Currently Implemented**:
```
GET/POST/PUT/DELETE  /projects
GET/POST/PUT/DELETE  /projects/{id}/documents  
GET/POST/PUT/DELETE  /projects/{id}/file-tree
GET/POST/PUT/DELETE  /projects/{id}/tags
POST                 /projects/{id}/llm/generate
```

**Response Format**:
```python
# Success
{"success": true, "data": {...}, "status": 200}

# Error  
{"success": false, "error": "ValidationError", "message": "...", "status": 400}
```

## Development Guidelines

### Testing Strategy
- **Unit Tests**: Test repository interfaces and business logic
- **Integration Tests**: Test API endpoints with test database
- **Memory Backend**: Use for fast, isolated testing
- **Coverage**: Aim for >80% test coverage

### Database Migrations
- **SQLAlchemy Models**: Define schema in `src/database/models/`
- **Alembic Migrations**: Auto-generate migrations from model changes
- **Environment Sync**: Keep dev, test, and prod schemas consistent

### Error Handling
- **Consistent Format**: All endpoints return `ApiResponse<T>` wrapper
- **Validation**: Use Pydantic for request/response validation
- **Logging**: Structured logging with context information
- **Authentication**: Handle Supabase JWT validation errors gracefully

### API Development
1. **Define Domain Model**: Create/update domain model in `src/database/interfaces/models/`
2. **Update Frontend Types**: Align frontend types in `/frontend/src/lib/localdb/types.ts`
3. **Implement Backend**: Create endpoint with proper Pydantic schemas
4. **Add Tests**: Unit and integration tests for new endpoints
5. **Update Documentation**: Update relevant docs in `/_docs/`

### Domain Model Changes
**CRITICAL WORKFLOW** - When changing any domain model:
1. **Backend First**: Modify domain model in `src/database/interfaces/models/`
2. **Frontend Sync**: Update `/frontend/src/lib/localdb/types.ts` to match exactly
3. **Provider Update**: Update `/frontend/src/lib/data/local-provider.ts` with new fields
4. **Seed Data**: Update `/frontend/src/lib/localdb/seeds.ts` to include new fields
5. **Test Both**: Ensure both backend and frontend work with the updated model

## Environment Configuration

**Key Environment Variables**:
- `DATABASE_BACKEND`: "memory" | "database"
- `DATABASE_URL`: PostgreSQL connection string
- `SUPABASE_*`: Authentication configuration
- `PORTKEY_*`: LLM gateway configuration

**Development vs Production**:
- **Development**: Uses memory backend, local services  
- **Production**: Uses PostgreSQL, Supabase auth, hosted Portkey

## Documentation Resources

**📚 Backend Documentation**:
- **Architecture Overview**: [`/_docs/backend/overview.md`](../_docs/backend/overview.md)
- **Backend Capabilities**: [`/_docs/backend/capabilities.md`](../_docs/backend/capabilities.md)
- **API Reference**: [`/_docs/core/api-reference.md`](../_docs/core/api-reference.md)
- **System Architecture**: [`/_docs/core/system-architecture.md`](../_docs/core/system-architecture.md)

**🛠️ Development Guides**:
- **Environment Setup**: [`/_docs/development/environment-configuration.md`](../_docs/development/environment-configuration.md)
- **Deployment Guide**: [`/_docs/development/deployment-guide.md`](../_docs/development/deployment-guide.md)

## Common Tasks

### Adding New Endpoint
1. Define Pydantic request/response schemas
2. Create repository method if needed  
3. Implement FastAPI endpoint with dependency injection
4. Add comprehensive tests
5. Update API documentation

### Database Schema Changes
1. Modify SQLAlchemy models
2. Generate Alembic migration: `alembic revision --autogenerate -m "description"`
3. Test migration: `alembic upgrade head`
4. Update repository interfaces if needed

### LLM Agent Development
1. Inherit from `BaseAgent` class
2. Implement agent-specific prompts and logic
3. Add to agent catalog and orchestrator
4. Test with various input scenarios

The backend provides a robust foundation with clean architecture, comprehensive testing, and seamless frontend integration.