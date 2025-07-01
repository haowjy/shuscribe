# CLAUDE.md - Backend Development Guide

This guide provides essential information for working with the ShuScribe backend.

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
1. Define Pydantic schemas in `src/schemas/`
2. Implement repository methods if needed
3. Add business logic in `src/services/`
4. Create API endpoints in `src/api/v1/endpoints/`
5. Write tests for each layer

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

## Additional Resources
- Technical docs: `_docs/technical/backend/`
- Notebooks: `backend/notebooks/` for examples
- Test files: Good examples of usage patterns
- Type hints: IDE support for exploration