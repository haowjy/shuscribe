# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ShuScribe is a **frontend-centric** full-stack application for fiction writers, built with Next.js 15 + React 19 (frontend) and FastAPI (backend).

### Development Philosophy: Frontend-First

**Core Principle**: The frontend drives the development process and user experience.

**Why Frontend-First?**
- **User Experience First**: UI/UX decisions drive API design, not the other way around
- **Rapid Prototyping**: Frontend can use mock data and Next.js API routes for immediate feedback
- **Type Safety**: Frontend TypeScript interfaces define the API contract
- **Authentication**: Supabase Auth handled entirely in frontend, backend trusts the auth tokens
- **State Management**: TanStack Query + LocalStorage provides offline-first experience

**How It Works**:
1. **Design in Frontend**: Create UI components and define TypeScript interfaces
2. **Mock Data**: Use MSW (Mock Service Worker) and Next.js API routes for development
3. **API Contract**: Frontend `src/types/api.ts` defines the expected API structure
4. **Backend Implementation**: Backend implements endpoints to match frontend expectations
5. **Validation**: Frontend types become backend Pydantic models with field aliases

## Quick Start

### Essential Commands

**Frontend Development**:
```bash
cd frontend
pnpm install                              # Install dependencies
npm run build                             # Production build
npm run lint                              # Run ESLint
pnpm dlx shadcn@latest add [component]    # Add UI components

# IMPORTANT: Never run dev server via Claude Code - let user handle this
# User will run: npm run dev or pnpm dev
```

**Backend Development**:
```bash
cd backend
uv sync && source .venv/bin/activate     # Setup environment
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000  # Dev server
uv run pytest                            # Run tests
uv run black . && uv run isort .         # Format code
```

**Docker Services**:
```bash
# From project root
docker-compose up -d                     # Start PostgreSQL & Portkey Gateway
docker-compose down                      # Stop all services
```

## Specialized Development Guides

### When to Use Which Guide

- **🎨 Frontend Work**: Refer to [`/frontend/CLAUDE-frontend.md`](frontend/CLAUDE-frontend.md)
  - Component patterns, state management, and UI development
  - Authentication integration and @-reference system
  - shadcn/ui components and Tailwind CSS patterns

- **⚙️ Backend Work**: Refer to [`/backend/CLAUDE-backend.md`](backend/CLAUDE-backend.md)  
  - Repository patterns, database models, and agent systems
  - LLM integration, API endpoints, and security
  - FastAPI development and testing strategies

- **🔗 Integration Work**: Use this guide for understanding how frontend and backend work together

## Frontend-Backend Integration

### Core Integration Principles

**Authentication Strategy**:
- **Frontend**: Handles all authentication via Supabase Auth
- **Backend**: Extracts tokens from Authorization header, trusts frontend validation
- **No Token Validation**: Backend doesn't validate tokens, just extracts for context

**Data Flow**:
- **Frontend-First**: UI state drives API requirements
- **Offline-First**: LocalStorage + TanStack Query provide offline functionality
- **API Consistency**: Both systems use `ApiResponse<T>` wrapper for all responses
- **Error Handling**: Consistent error format across frontend and backend

**Field Naming Conventions**:
- **Frontend**: snake_case (`project_id`, `created_at`, `word_count`)
- **Backend**: snake_case (prefer no aliases)
- **API**: Backend handles both formats seamlessly

### Integration Development Workflow

**For Frontend Features**:
1. **Design First**: Create UI components and define TypeScript interfaces in `/frontend/src/types/api.ts`
2. **Mock Implementation**: Use MSW and Next.js API routes for rapid prototyping
3. **Backend Alignment**: Backend implements endpoints to match frontend TypeScript interfaces
4. **Integration**: Both systems use consistent `ApiResponse<T>` wrapper and field naming

**For Backend Features**:
1. **API Contract**: Check frontend expectations in `/frontend/src/types/api.ts`
2. **Implementation**: Create backend endpoints with proper response format and field aliases
3. **Frontend Integration**: Update frontend to use new endpoints if needed
4. **Validation**: Ensure ProseMirror content structure matches between systems

## Documentation Structure

### Core Documentation

- **📚 API Reference**: [`/_docs/core/api-reference.md`](_docs/core/api-reference.md)
  - Complete API documentation with request/response examples
  - Authentication, error handling, and field naming conventions
  - Insomnia/Postman testing guidance
- **🗺️ Frontend Routes**: [`/_docs/core/frontend-routes.md`](_docs/core/frontend-routes.md)
  - Complete routing documentation and navigation patterns
  - Route guards, parameters, and frontend-backend mapping
  - Entry point behavior and dashboard-first user flow

### High-Level Documentation

- **📖 Product Overview**: [`/_docs/high-level/1-product-overview.md`](_docs/high-level/1-product-overview.md)
- **🎯 MVP Specification**: [`/_docs/high-level/2-mvp.md`](_docs/high-level/2-mvp.md)
- **🎨 Frontend Architecture**: [`/_docs/high-level/3-frontend.md`](_docs/high-level/3-frontend.md)
- **⚙️ Backend Architecture**: [`/_docs/high-level/4-backend.md`](_docs/high-level/4-backend.md)

### API & Integration Documentation

- **📝 API Contracts**: [`/_docs/api/contracts.md`](_docs/api/contracts.md) - Frontend-backend interface definitions
- **🔐 Authentication**: [`/_docs/api/authentication.md`](_docs/api/authentication.md) - Auth implementation details (planned)

### Development Documentation

- **🛠️ Environment Setup**: [`/_docs/development/environment-setup.md`](_docs/development/environment-setup.md) - Complete dev environment guide (planned)
- **🧪 Testing Strategy**: [`/_docs/development/testing-strategy.md`](_docs/development/testing-strategy.md) - Testing approach and tools (planned)
- **🚀 Deployment Guide**: [`/_docs/development/deployment-guide.md`](_docs/development/deployment-guide.md) - Production deployment process (planned)

## Architecture Overview

ShuScribe is a **context-aware fiction writing platform** with a three-panel VS Code-like workspace:

1. **File Explorer** - Hierarchical project organization (characters, locations, chapters)
2. **Editor** - Tabbed document editor with @-reference system
3. **AI Panel** - Context-aware AI assistance (future implementation)

**Key Technologies**:
- **Frontend**: Next.js 15.3.5, React 19, TypeScript, shadcn/ui, TanStack Query
- **Backend**: FastAPI, SQLAlchemy, Supabase (PostgreSQL), Repository pattern
- **Authentication**: Supabase Auth with OAuth support
- **AI**: Self-hosted Portkey Gateway with multiple LLM providers

## Environment Setup

### Quick Environment Setup

**Backend**:
1. Copy `.env.example` to `.env` and configure
2. Generate encryption key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. Start Docker services: `docker-compose up -d`

**Frontend**:
1. Copy `.env.local.example` to `.env.local`
2. Configure Supabase environment variables
3. In Supabase dashboard: Enable auth providers, add redirect URLs

## Key Development Notes

### Critical Rules

- **Frontend Dev Server**: NEVER run `npm run dev`, `pnpm dev` via Claude Code - user handles this
- **File Storage**: Backend file repositories MUST use `backend/temp/` directory (gitignored)
- **API Documentation**: ALWAYS update `/_docs/core/api-reference.md` when modifying API endpoints
- **Cross-References**: Update all CLAUDE.md files when making documentation changes

### @-Reference System (Core Feature)

- Documents support `@character/name`, `@location/place` syntax for cross-references
- References are highlighted and clickable in editor
- **Frontend-Only Implementation**: Search uses local file tree data for instant results
- **No Backend Integration**: Reference search stays in frontend for performance

### Common Patterns

- Frontend `src/types/api.ts` defines the API contract
- Backend `src/schemas/` models match frontend types with field aliases
- Both systems use `ApiResponse<T>` wrapper for consistent responses
- Authentication context flows from frontend to backend via Bearer tokens

## Documentation Maintenance

### Critical Documentation Rules

- **ALWAYS update relevant `/_docs/` files** when making changes to the codebase
- **ALWAYS update the appropriate CLAUDE.md file** when documentation changes
- **ALWAYS maintain cross-references** between all documentation files
- All documentation must include complete examples and clear descriptions

### Documentation Update Workflow

When making changes, update documentation in this order:

#### 1. API Changes
- **Update**: `/_docs/core/api-reference.md` - Complete API documentation
- **Update**: Main `CLAUDE.md` - If integration patterns change
- **Update**: `/_docs/api/contracts.md` - If interface definitions change

#### 2. Frontend Changes
- **Update**: Relevant `/_docs/core/` or `/_docs/development/` files
- **Update**: `/frontend/CLAUDE-frontend.md` - Add short description of change
- **Update**: Main `CLAUDE.md` - If core patterns change

#### 3. Backend Changes  
- **Update**: Relevant `/_docs/core/` or `/_docs/development/` files
- **Update**: `/backend/CLAUDE-backend.md` - Add short description of change
- **Update**: Main `CLAUDE.md` - If core patterns change

#### 4. Integration/Architecture Changes
- **Update**: `/_docs/core/integration-guide.md` (when created)
- **Update**: Main `CLAUDE.md` - Core integration principles
- **Update**: Both specialized CLAUDE files if relevant

### Documentation Location Guidelines

**Core Technical Documentation** (`/_docs/core/`):
- Detailed technical guides, implementation patterns
- API reference, frontend/backend architecture guides

**High-Level Documentation** (`/_docs/high-level/`):
- Product overview, MVP specs, architectural decisions
- Business logic and system design documentation

**API Documentation** (`/_docs/api/`):
- Interface definitions, contracts, field mapping
- Authentication patterns, integration guides

**Development Documentation** (`/_docs/development/`):
- Environment setup, testing, deployment
- Workflow guides and development standards

### CLAUDE.md File Responsibilities

- **Main `CLAUDE.md`**: Project overview, navigation hub, core integration principles
- **Backend CLAUDE**: Backend-specific workflows, short descriptions of backend doc updates
- **Frontend CLAUDE**: Frontend-specific workflows, short descriptions of frontend doc updates

---

**Need specific guidance?** Check the specialized guides:
- 🎨 **Frontend**: [`/frontend/CLAUDE-frontend.md`](frontend/CLAUDE-frontend.md)
- ⚙️ **Backend**: [`/backend/CLAUDE-backend.md`](backend/CLAUDE-backend.md)
- 📚 **API**: [`/_docs/core/api-reference.md`](_docs/core/api-reference.md)