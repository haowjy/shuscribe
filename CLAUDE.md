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
pnpm install                              # Install dependencies (preferred)
npm install                               # Alternative: npm install

# Development
# IMPORTANT: Never run dev server via Claude Code - let user handle this
# User will run: npm run dev or pnpm dev
npm run build                             # Production build
npm run start                             # Start production server
npm run lint                              # Run ESLint

# UI Components (shadcn/ui)
pnpm dlx shadcn@latest add [component]    # Add shadcn components
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

### Overall System Architecture
ShuScribe is a **context-aware fiction writing platform** with a three-panel VS Code-like workspace. The system consists of:

- **Backend**: FastAPI with repository pattern for data persistence
- **Frontend**: Next.js 15 with React 19, implementing a workspace UI for fiction writers
- **Authentication**: Supabase Auth with OAuth support
- **Database**: Supabase (PostgreSQL) for production, file-based repos for development

### Frontend Architecture (Next.js)

**Core Design**: Three-panel workspace layout for fiction writing:
1. **File Explorer** - Hierarchical project organization (characters, locations, chapters)
2. **Editor** - Tabbed document editor with @-reference system
3. **AI Panel** - Context-aware AI assistance (future implementation)

**Key Technologies**:
- **Next.js 15.3.5** with App Router and Turbopack
- **React 19** with TypeScript
- **shadcn/ui** + **Radix UI** for component library
- **Tailwind CSS v4** for styling
- **react-resizable-panels** for workspace layout
- **Supabase Auth** with SSR support

**Authentication Flow**:
- Middleware-based route protection (`src/middleware.ts`)
- Dual Supabase clients: browser (`src/lib/supabase/client.ts`) and server (`src/lib/supabase/server.ts`)
- AuthContext provider for global auth state
- OAuth callback handling at `/auth/callback`

**Component Patterns**:
- **Composition**: WorkspaceLayout accepts pluggable panels
- **Client Components**: Most components use `"use client"` for interactivity
- **Context Pattern**: AuthContext for user state management

### Backend Repository Pattern
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

**Backend Setup**:
1. Copy `.env.example` to `.env` and configure
2. Generate encryption key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. Start Docker services: `docker-compose up -d`
4. Backend: `cd backend && uv sync`

**Frontend Setup**:
1. `cd frontend && pnpm install`
2. Copy `.env.local.example` to `.env.local`
3. Configure Supabase environment variables:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your-supabase-project-url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
   ```
4. In Supabase dashboard:
   - Enable authentication providers (Email, Google OAuth)
   - Add redirect URLs: `http://localhost:3000/auth/callback`
   - Set Site URL: `http://localhost:3000`

### Testing Strategy
- **Backend**: pytest with async support, coverage threshold 40%
- Database tests: `tests/test_database/` with test runner
- Factories: `tests/factories.py` for test data generation
- **Frontend**: No tests currently configured (recommended: Jest + Testing Library)

### Code Quality
**Backend**:
- **Formatting**: Black (88 char line length)
- **Type checking**: mypy with strict settings
- **Import sorting**: isort with black profile
- **Linting**: flake8

**Frontend**:
- **TypeScript**: Strict type checking with path aliases (`@/*`)
- **ESLint**: Next.js recommended configuration
- **Prettier**: Auto-formatting via Tailwind CSS classes
- **Component Library**: shadcn/ui with consistent design tokens

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

### Frontend Development Patterns

**Component Architecture**:
- Components follow composition pattern: `<WorkspaceLayout fileExplorer={<FileExplorer />} />`
- Use `"use client"` directive for interactive components
- Leverage shadcn/ui components: `pnpm dlx shadcn@latest add [component-name]`
- UI state managed with React hooks (`useState`, `useContext`)

**Authentication Integration**:
- Use `useAuth()` hook to access user state: `const { user, signOut } = useAuth()`
- Protected routes handled by middleware, not component-level guards
- Supabase client selection: browser context uses `createClient()`, server uses `await createClient()`

**@-Reference System** (Core Feature):
- Documents support `@character/name` syntax for cross-references
- References are highlighted and clickable in editor
- File explorer shows contextual tags on hover
- Future: Will integrate with backend for validation and autocomplete

**Development Server Behavior**:
- **CRITICAL**: Claude Code should NEVER run `npm run dev`, `pnpm dev`, or similar
- Environment changes require server restart (user handles this)
- Turbopack provides fast rebuilds during development

**Component State Patterns**:
- Resizable panels: Use `react-resizable-panels` with persistence
- Modal/Dialog state: Prefer controlled components with explicit state
- Form handling: `react-hook-form` with `zod` validation (when needed)
- Loading states: Use skeleton components from shadcn/ui

