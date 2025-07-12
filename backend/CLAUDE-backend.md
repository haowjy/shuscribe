# CLAUDE.md - Backend Development Guide

This guide provides backend-specific information for working with the ShuScribe backend.

## 🔗 Multi-Repository Context

This is the **backend-specific** guide. For complete project context, see:
- **Main Guide**: `/CLAUDE.md` - Overall project philosophy and coordination
- **Frontend Guide**: `/frontend/CLAUDE-frontend.md` - Frontend patterns and API contract definition

## Frontend-First Integration

**Core Principle**: The backend implements APIs to match frontend expectations.

**Key Integration Points**:
- **API Contract Source**: Frontend `src/types/api.ts` defines the expected API structure
- **Response Format**: Backend returns `ApiResponse<T>` wrapper matching frontend
- **Field Naming**: Backend uses Pydantic aliases for camelCase/snake_case compatibility
- **Authentication**: Backend trusts frontend auth tokens, extracts for context only
- **Error Handling**: Consistent error format matching frontend expectations

**Development Flow**:
1. **Check Frontend Contract**: Review `/frontend/src/types/api.ts` for expected API structure
2. **Implement Backend**: Create endpoints with matching response format and field aliases
3. **Validate Integration**: Ensure ProseMirror content structure and field naming match
4. **Test Consistency**: Verify `ApiResponse<T>` wrapper and error handling work correctly

## Quick Start

```bash
# Setup environment
cd backend
uv sync
source .venv/bin/activate

# Start development server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest
uv run pytest tests/test_database/         # Database-specific tests
uv run pytest --cov=src --cov-report=html  # With coverage

# Code quality
uv run black .                             # Format code
uv run isort .                             # Sort imports
uv run flake8                              # Lint
uv run mypy src/                           # Type checking

# Database migrations
uv run alembic revision --autogenerate -m "Description"
uv run alembic upgrade head
```

## Project Structure

```
backend/
├── src/
│   ├── agents/          # AI agents for wiki generation
│   ├── api/             # FastAPI endpoints and dependencies
│   ├── background/      # Background task processing
│   ├── core/            # Core utilities and shared code
│   ├── database/        # Repository pattern implementations
│   ├── prompts/         # LLM prompt templates
│   ├── schemas/         # Pydantic models
│   │   └── db/          # Database-specific Pydantic models
│   ├── services/        # Business logic layer
│   ├── utils/           # Helper utilities
│   ├── config.py        # Application configuration
│   └── main.py          # FastAPI application entry point
├── tests/               # Test suite
├── scripts/             # Utility scripts (story import, etc.)
├── notebooks/           # Jupyter notebooks for experimentation
├── temp/                # Local file storage (gitignored)
└── supabase/            # Database migrations and schema
```

## Key Architecture Concepts

### Repository Pattern
- Supports three backends: `memory` (testing), `file` (local development), `database` (production)
- Access through `RepositoryFactory` in `src/database/factory.py`
- Repository model schemas are defined in `src/schemas/db/`
- **CRITICAL**: File backend always uses `backend/temp/` directory (gitignored)

### Domain Organization
- **User**: Authentication, profiles, encrypted API keys
- **Workspace**: Story processing state
- **Story**: Chapter content and metadata
- **Wiki**: Generated articles with versioning
- **Writing**: Author tools, notes, AI conversations

### LLM Integration
- All LLM calls route through self-hosted Portkey Gateway (Docker service)
- Default model: `google/gemini-2.0-flash-001` (cost optimization)
- Model catalog in `src/core/llm/catalog.py` defines capabilities
- Supports thinking modes, structured output, and streaming

### Agent System
- Base class `BaseAgent` provides common LLM functionality
- WikiGen agents handle the wiki generation workflow:
  - ArcSplitter: Divides story into narrative arcs
  - WikiPlanner: Plans wiki structure
  - ArticleWriter: Generates content
  - ChapterBacklinker: Creates wiki links
- Orchestrator coordinates agent execution

### Spoiler Prevention
- Wiki articles have chapter-specific versions
- Arc-based processing ensures content safety:
  - Arc 1 (Ch 1-10): Wiki safe through Ch 10
  - Arc 2 (Ch 11-20): Wiki safe through Ch 20
  - And so on...
- "Living current version" incorporates user edits

## Development Workflow

### Environment Setup

1. Copy `.env.example` to `.env`
2. Generate encryption key:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
3. Configure environment variables:
   - `ENCRYPTION_KEY`: For API key encryption
   - `PORTKEY_BASE_URL`: Usually `http://localhost:8787`
   - `SKIP_DATABASE`: Set `true` for file-based mode
   - `THINKING_BUDGET_*_PERCENT`: For thinking mode costs

### Docker Services

```bash
# Start required services (PostgreSQL, Portkey Gateway)
docker-compose up -d

# View logs
docker-compose logs -f

# Connect to database
docker-compose exec postgres psql -U postgres -d shuscribe
```

### Testing Strategy
- Write tests for all repository implementations
- Use `pytest` fixtures for test data
- Minimum 40% coverage requirement
- Test files in `tests/` mirror `src/` structure

### Code Standards
- **Formatting**: Black (88 char limit)
- **Imports**: isort with Black profile
- **Type hints**: Required, checked by mypy
- **Linting**: flake8 rules
- **Docstrings**: Required for public functions/classes

## Common Tasks

### Adding New Features
1. **Check Frontend Contract**: Review `/frontend/src/types/api.ts` for expected API structure
2. **Define Pydantic schemas**: Create models in `src/schemas/` with field aliases matching frontend
3. **Implement repository methods**: Add data access layer if needed
4. **Add business logic**: Implement services in `src/services/`
5. **Create API endpoints**: Build endpoints in `src/api/v1/endpoints/` with `ApiResponse<T>` wrapper
6. **Write tests**: Test each layer including API contract compliance

### Working with LLM Agents
1. Inherit from `BaseAgent`
2. Create prompt templates in `src/prompts/`
3. Implement `process()` method
4. Add to orchestrator workflow if needed

### Database Changes
1. Modify SQLAlchemy models in `src/database/models/`
2. Generate migration: `uv run alembic revision --autogenerate -m "Description"`
3. Review generated migration
4. Apply: `uv run alembic upgrade head`

## Important Notes

### Security
- API keys are encrypted using Fernet encryption
- Never store plaintext secrets
- All user inputs validated through Pydantic
- File paths sanitized to prevent traversal attacks

### Performance
- Use async/await throughout
- Batch operations where possible
- Choose appropriate LLM models for tasks
- Consider caching for repeated LLM calls

### File Storage
When using file backend, the structure in `temp/` is:
- `.shuscribe/`: System metadata
- `story/`: Chapter content
- `wiki/`: Current wiki articles
- `wiki-versions/`: Chapter-specific versions
- `notes/`: Author notes
- `conversations/`: AI chat history

## Troubleshooting

### Common Issues
- **Module not found**: Ensure venv is activated
- **Database connection**: Check Docker services are running
- **LLM errors**: Verify Portkey Gateway is accessible
- **File permissions**: Check `temp/` directory permissions

### Debug Mode
- Set `LOG_LEVEL=DEBUG` in `.env`
- Use `--reload` flag for auto-restart
- Check logs in console output

## Documentation Resources

### Core Documentation (`/_docs/core/`)
- **📚 API Reference**: [`/_docs/core/api-reference.md`](/_docs/core/api-reference.md) - Complete API documentation with request/response examples
- **⚙️ Backend Guide**: [`/_docs/core/backend-guide.md`](/_docs/core/backend-guide.md) - Repository patterns, LLM integration, agent systems (planned)
- **🔗 Integration Guide**: [`/_docs/core/integration-guide.md`](/_docs/core/integration-guide.md) - Frontend-backend integration patterns (planned)

### High-Level Documentation (`/_docs/high-level/`)
- **📖 Product Overview**: [`/_docs/high-level/1-product-overview.md`](/_docs/high-level/1-product-overview.md) - System architecture and goals
- **⚙️ Backend Architecture**: [`/_docs/high-level/4-backend.md`](/_docs/high-level/4-backend.md) - High-level backend design decisions

### API Documentation (`/_docs/api/`)
- **📝 API Contracts**: [`/_docs/api/contracts.md`](/_docs/api/contracts.md) - Frontend-backend interface definitions
- **🔗 Field Mapping**: [`/_docs/api/field-mapping.md`](/_docs/api/field-mapping.md) - camelCase/snake_case conversion guide (planned)
- **🔐 Authentication**: [`/_docs/api/authentication.md`](/_docs/api/authentication.md) - Auth implementation details (planned)

### Development Documentation (`/_docs/development/`)
- **🛠️ Environment Setup**: [`/_docs/development/environment-setup.md`](/_docs/development/environment-setup.md) - Complete dev environment guide (planned)
- **🧪 Testing Strategy**: [`/_docs/development/testing-strategy.md`](/_docs/development/testing-strategy.md) - Backend testing approach (planned)
- **🚀 Deployment Guide**: [`/_docs/development/deployment-guide.md`](/_docs/development/deployment-guide.md) - Production deployment (planned)

### Backend-Specific Resources
- **Notebooks**: `backend/notebooks/` - Jupyter notebooks for experimentation
- **Test Files**: `tests/` - Good examples of usage patterns and repository implementations
- **Type Hints**: IDE support for exploring repository interfaces and service classes

## Frontend-Backend Integration Examples

### API Endpoint Pattern

```python
# Standard endpoint with frontend integration
from src.schemas.base import ApiResponse
from src.api.dependencies import get_optional_user_context

@router.get("/{project_id}", response_model=ApiResponse[ProjectDetails])
async def get_project(
    project_id: str,
    user_context: dict = Depends(get_optional_user_context)
) -> ApiResponse[ProjectDetails]:
    # Implementation
    project = await repos.project.get_by_id(project_id)
    return ApiResponse.success(project_to_response(project))
```

### Pydantic Model with Field Aliases

```python
class ProjectDetails(BaseModel):
    """Project details matching frontend ProjectDetails interface"""
    model_config = {"populate_by_name": True}
    
    id: str
    word_count: int = Field(alias="wordCount")  # Frontend uses camelCase
    created_at: str = Field(alias="createdAt")  # Backend uses snake_case
```

### Authentication Integration

```python
# Authentication dependency (no validation, just extraction)
from src.api.dependencies import get_optional_user_context

async def endpoint(user_context: dict = Depends(get_optional_user_context)):
    # user_context contains: {"token": "...", "authenticated": bool}
    logger.info(f"Request from authenticated user: {user_context['authenticated']}")
```

## Code Snippets

```python
# use datetime.now(UTC) for all timestamps in UTC
from datetime import UTC, datetime
now = datetime.now(UTC)
```

## Documentation

### Backend Documentation Maintenance

When making backend changes, update documentation in this order:

#### Core Documentation Updates
- **Repository Pattern Changes**: Update `/_docs/core/backend-guide.md` (when created) with new patterns
- **API Endpoint Changes**: Update `/_docs/core/api-reference.md` with complete request/response schemas
- **Integration Changes**: Update `/_docs/core/integration-guide.md` (when created) if affecting frontend

#### This CLAUDE File Updates
- **Add short description** of any significant backend architecture changes
- **Update command examples** if new development workflows are introduced
- **Note new dependencies** or environment variable requirements

#### Cross-Reference Updates
- **API Contract Changes**: Update `/_docs/api/contracts.md` if interface definitions change
- **Authentication Changes**: Update `/_docs/api/authentication.md` (when created)
- **Main CLAUDE.md**: Update if core integration principles change

### Implementation Guidelines
- **Stub Implementation**: Use `NotImplementedError` with TODO comments for planned features
- **Frontend Contract**: Always check `/frontend/src/types/api.ts` before implementing new API endpoints
- **Response Format**: Use `ApiResponse<T>` wrapper for all API responses to match frontend expectations
- **Field Naming**: Include Pydantic aliases for camelCase/snake_case compatibility
- **Documentation**: Include complete request/response schemas with examples in API documentation

### Backend Documentation Scope
- **Repository Patterns**: Database, memory, and file backend implementations
- **LLM Integration**: Agent systems, model catalogs, streaming support
- **Authentication**: Token extraction and user context handling
- **Testing**: Repository testing patterns and service layer tests
- **Environment**: Configuration management and Docker service setup