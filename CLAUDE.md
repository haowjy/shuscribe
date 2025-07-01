# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (Python/FastAPI)
```bash
cd backend

# Environment setup
uv sync                                    # Install/update dependencies
source .venv/bin/activate                  # Activate virtual environment (required for Python commands)

# Development server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Testing
uv run pytest                             # Run all tests
uv run pytest tests/test_database/        # Run database tests
uv run pytest --cov=src --cov-report=html # Run with coverage

# Code quality
uv run black .                            # Format code
uv run isort .                            # Sort imports
uv run flake8                             # Lint code
uv run mypy src/                          # Type checking

# Database migrations
uv run alembic revision --autogenerate -m "Description"  # Create migration
uv run alembic upgrade head                              # Apply migrations

# Dependencies
uv add package-name                       # Add runtime dependency
uv add --dev package-name                 # Add development dependency
```

### Frontend (Next.js/TypeScript)
```bash
cd frontend

# Dependencies
npm install                               # Install dependencies

# Development
npm run dev                               # Start dev server with hot reload
npm run build                             # Production build
npm run start                             # Start production server
npm run lint                              # Run ESLint
```

### Docker Services
```bash
# From project root
docker-compose up -d                      # Start PostgreSQL & Portkey Gateway
docker-compose down                       # Stop all services
docker-compose logs -f                    # View logs
docker-compose exec postgres psql -U postgres -d shuscribe  # Connect to database
```

## Architecture Overview

### Repository Pattern
ShuScribe uses a repository pattern with multiple backends:
- **File repositories**: Local file-based storage for development (`src/database/file/`)
- **Database repositories**: PostgreSQL for production (planned, see `src/database/models/`)
- **Interfaces**: Abstract base classes define repository contracts (`src/database/interfaces/`)

The `RepositoryFactory` (`src/database/factory.py`) creates appropriate repository implementations based on configuration.

**IMPORTANT**: File repositories always use `backend/temp/` directory to avoid accidentally committing local data files to git. This directory is gitignored.

### LLM Architecture
**Core Service**: `src/services/llm/llm_service.py` handles all LLM interactions through self-hosted Portkey Gateway.

**Agent System**: WikiGen agents (`src/agents/`) inherit from `BaseAgent`:
- Default model: `google/gemini-2.0-flash-001` (cost optimization)
- Supports streaming, structured output, and thinking modes
- Built-in error handling and model validation

**Key Components**:
- `src/core/llm/catalog.py`: Model definitions and capabilities
- `src/schemas/llm/`: Pydantic models for LLM requests/responses
- `src/agents/wikigen/`: Specialized agents for wiki generation workflow

### Configuration
`src/config.py` uses Pydantic Settings with `.env` file support:
- **Database**: Supabase URL/keys, skip database flag for in-memory mode
- **LLM**: Portkey Gateway configuration, encryption keys
- **Environment**: Development vs production settings

### API Structure
FastAPI app with versioned routing:
- `src/main.py`: Application entry point and middleware
- `src/api/v1/`: API endpoints organized by domain (stories, wiki, users, etc.)
- `src/services/`: Business logic layer

## Development Notes

### Environment Setup
1. Copy `.env.example` to `.env` and configure
2. Generate encryption key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. Start Docker services: `docker-compose up -d`
4. Backend: `cd backend && uv sync`
5. Frontend: `cd frontend && npm install`

### Testing Strategy
- Backend: pytest with async support, coverage threshold 40%
- Database tests: `tests/test_database/` with test runner
- Factories: `tests/factories.py` for test data generation

### Code Quality
- **Formatting**: Black (88 char line length)
- **Type checking**: mypy with strict settings
- **Import sorting**: isort with black profile
- **Linting**: flake8

### File Repository Storage
**CRITICAL**: When using file-based repositories for local development:
- All file repositories MUST use `backend/temp/` as the workspace directory
- Never use current directory (`.`) or project root for file storage
- The `temp/` directory is gitignored to prevent accidental commits of local data
- Dependencies and API endpoints are configured to use `temp/` automatically

Example:
```python
# Correct - uses temp directory
repos = get_repositories(backend="file", workspace_path=Path("temp"))

# Wrong - could commit local files
repos = get_repositories(backend="file", workspace_path=Path("."))
```

