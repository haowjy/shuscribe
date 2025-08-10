# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Tools

* context7: when the user requests code examples, setup or configuration steps, or library/API documentation
* Use `uv run python` for running Python commands in the backend

## Key Development Notes

### Critical Rules

- **Frontend Dev Server**: NEVER run `npm run dev`, `pnpm dev` via Claude Code - user handles this
- **Cross-References**: Update all CLAUDE.md and other documentation files when making changes that affect the documentation
- **Never directly edit `pyproject.toml` or `package.json`**: ALWAYS use the package manager (`uv` for backend, or `pnpm` for frontend)
- **Always use absolute file paths for Python FastAPI, never use relative paths**
- **Tailwind Best Practices**: Use utility-first approach with direct classes in JSX. Never create CSS_CLASSES constants - this is an anti-pattern that defeats Tailwind's purpose and breaks JIT compilation.
- **Update CLAUDE.md**: Make sure to ALWAYS update the CLAUDE.md and/or other documentation files when making changes that affect the documentation.

## Project Overview

ShuScribe is a **frontend-centric** Universe Content Management Platform built with Next.js 15 + React 19 (frontend) and FastAPI (backend), evolving from simple fiction writing tools to comprehensive universe management for creators at all scales.

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

### Current Implementation Snapshot

- Frontend currently implements an editor demo only: landing (`/`) and `/editor-test` with a comprehensive Tiptap editor.
- Not yet implemented: dashboard/workspace layout, Supabase auth, TanStack Query, API routes/mocks, and @-reference system.

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
uv run hypercorn src.main:app --reload --bind "[::]:8000"  # Dev server
uv run pytest                            # Run tests (quiet by default)
uv run pytest --log-level=DEBUG          # Run tests with debug logging
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

Note: The items below describe the target architecture. The current frontend does not yet include auth, dashboard, or API integration.

### Core Integration Principles

**Authentication Strategy**:
- **Frontend**: Handles all authentication via Supabase Auth
- **Backend**: Validates Supabase JWT tokens from Authorization header
- **Token Validation**: Backend validates tokens with Supabase for security

**Data Flow**:
- **Frontend-First**: UI state drives API requirements
- **Offline-First**: LocalStorage + TanStack Query provide offline functionality
- **API Consistency**: Both systems use `ApiResponse<T>` wrapper for all responses
- **Error Handling**: Consistent error format across frontend and backend

**Field Naming Conventions**:
- **Frontend**: camelCase (`projectId`, `createdAt`, `wordCount`)
- **Backend**: snake_case (Pydantic models can alias to/from camelCase)
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

- **📚 Complete API Specification**: [`/_docs/core/complete-api-specification.md`](_docs/core/complete-api-specification.md)
  - Comprehensive API documentation covering current + future endpoints
  - Authentication, error handling, and field naming conventions
  - Implementation roadmap and integration patterns
  - Insomnia/Postman testing guidance
- **🗺️ Frontend Routes**: [`/_docs/core/frontend-routes.md`](_docs/core/frontend-routes.md)
  - Complete routing documentation and navigation patterns
  - Route guards, parameters, and frontend-backend mapping
  - Entry point behavior and dashboard-first user flow

- **🏗️ Content Architecture**: [`/_docs/core/content-architecture.md`](_docs/core/content-architecture.md)
  - Multi-content system architecture supporting flexible publishing workflows
  - Database schema design for universe management
  - Scalability considerations and API architecture

### High-Level Documentation

- **📖 Product Overview**: [`/_docs/high-level/1-product-overview.md`](_docs/high-level/1-product-overview.md)
- **🎯 MVP Specification**: [`/_docs/high-level/2-mvp.md`](_docs/high-level/2-mvp.md)
- **🎨 Frontend Architecture**: [`/_docs/high-level/3-frontend.md`](_docs/high-level/3-frontend.md)
- **⚙️ Backend Architecture**: [`/_docs/high-level/4-backend.md`](_docs/high-level/4-backend.md)
- **🔮 Future Vision**: [`/_docs/high-level/5-future-vision.md`](_docs/high-level/5-future-vision.md)
- **📚 Publishing Strategy**: [`/_docs/high-level/6-publishing-strategy.md`](_docs/high-level/6-publishing-strategy.md)
- **📈 Market Strategy**: [`/_docs/high-level/7-market-strategy.md`](_docs/high-level/7-market-strategy.md)

### API & Integration Documentation

- **📝 API Contracts**: [`/_docs/api/contracts.md`](_docs/api/contracts.md) - Frontend-backend interface definitions
- **🔐 Authentication**: [`/_docs/api/authentication.md`](_docs/api/authentication.md) - Auth implementation details (planned)

### Development Documentation

- **🛠️ Environment Setup**: [`/_docs/development/environment-setup.md`](_docs/development/environment-setup.md) - Complete dev environment guide (planned)
- **⚙️ Environment Configuration**: [`/_docs/development/environment-configuration.md`](_docs/development/environment-configuration.md) - Environment variables and behavior differences
- **🧪 Testing Strategy**: [`/_docs/development/testing-strategy.md`](_docs/development/testing-strategy.md) - Testing approach and tools (planned)
- **📤 Publication System**: [`/_docs/development/publication-system.md`](_docs/development/publication-system.md) - Future publication workflow design
- **🤖 AI Collaboration**: [`/_docs/development/ai-collaboration-conflict-resolution.md`](_docs/development/ai-collaboration-conflict-resolution.md) - AI-assisted editing and conflict resolution patterns
- **🚀 Deployment Guide**: [`/_docs/development/deployment-guide.md`](_docs/development/deployment-guide.md) - Production deployment process
- **🚂 Railway Deployment**: [`/backend/railway-deploy.md`](backend/railway-deploy.md) - Complete Railway deployment guide

### Design Documentation

Design docs for unimplemented features have been removed to keep the code context lean. When starting new major features, create focused docs under `/_docs/` alongside implementation.

## Architecture Overview

ShuScribe is a **Universe Content Management Platform** with a three-panel VS Code-like workspace, scaling from indie fiction writers to Hollywood studios:

1. **File Explorer** - Hierarchical project organization with path-based auto-folder creation
2. **Editor** - Tabbed document editor with @-reference system and ProseMirror rich content
3. **AI Panel** - Context-aware AI assistance (future implementation)

**Path-Based Organization**: Documents use intuitive file paths (e.g., `/world/regions/kingdoms/stormlands/cities`) with automatic folder creation, eliminating manual folder management.

**Key Technologies**:
- **Frontend**: Next.js 15.3.5, React 19, TypeScript, shadcn/ui, TanStack Query
- **Backend**: FastAPI, SQLAlchemy, Supabase (PostgreSQL), Repository pattern
- **Authentication**: Supabase Auth with OAuth support
- **AI**: Self-hosted Portkey Gateway with multiple LLM providers
- **Deployment**: Railway (two-service architecture) + Vercel

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
- **Path-Based Document Creation**: Documents automatically create folder hierarchies from paths (e.g., `/characters/locations/taverns/document` creates all missing folders)

## Documentation Maintenance

### Critical Documentation Rules

- **ALWAYS update relevant `/_docs/` files** when making changes to the codebase
- **ALWAYS update the appropriate CLAUDE.md file** when documentation changes
- **ALWAYS maintain cross-references** between all documentation files
- All documentation must include complete examples and clear descriptions

### Documentation Update Workflow

When making changes, update documentation in this order:

#### 1. API Changes
- **Update**: `/_docs/core/complete-api-specification.md` - Complete API documentation
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

#### 5. Design/Planning Changes
- **Create/Update**: Focused docs under `/_docs/` when starting implementation
- **Update**: Main `CLAUDE.md` - If new planning docs are added
- **Reference**: Keep cross-references current and minimal

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

**Design Documentation**:
- Keep planning lightweight. Prefer documenting alongside code in `/_docs/`.

### CLAUDE.md File Responsibilities

- **Main `CLAUDE.md`**: Project overview, navigation hub, core integration principles
- **Backend CLAUDE**: Backend-specific workflows, short descriptions of backend doc updates
- **Frontend CLAUDE**: Frontend-specific workflows, short descriptions of frontend doc updates

---

**Need specific guidance?** Check the specialized guides:
- 🎨 **Frontend**: [`/frontend/CLAUDE-frontend.md`](frontend/CLAUDE-frontend.md)
- ⚙️ **Backend**: [`/backend/CLAUDE-backend.md`](backend/CLAUDE-backend.md)
- 📚 **API**: [`/_docs/core/complete-api-specification.md`](_docs/core/complete-api-specification.md)