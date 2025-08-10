# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Tools

* context7: when the user requests code examples, setup or configuration steps, or library/API documentation
* Use `uv run python` for running Python commands in the backend

## Key Development Notes

### Critical Rules

- **Always think about best practices and patterns for the code you are writing**
- **Always think about the user experience and the code you are writing**
- **Always think about the code you are writing**
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

- Frontend currently implements an editor demo only: landing (`/`) and `/editor-test` with a comprehensive Tiptap editor (📚 [`/_docs/frontend/TIPTAP-EDITOR.md`](_docs/frontend/TIPTAP-EDITOR.md)).
- Not yet implemented: dashboard/workspace layout, Supabase auth, TanStack Query, API routes/mocks, and @-reference system.

## Quick Start

### Essential Commands

**Frontend Development**:
```bash
cd frontend
pnpm install                              # Install dependencies
pnpm run build                             # Production build
pnpm run lint                              # Run ESLint
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

**CRITICAL**: The backend is the **source of truth** for all data models and API contracts.

### Core Integration Principles

**Backend-First Domain Models**:
- **Backend**: Domain models in `/backend/src/database/interfaces/models/` define the canonical data structure
- **Frontend**: Must align types exactly with backend models for seamless integration
- **API Contract**: Backend endpoint responses are authoritative
- **Data Validation**: Backend Pydantic schemas define the validation rules

**Authentication Strategy**:
- **Frontend**: Handles all authentication via Supabase Auth
- **Backend**: Validates Supabase JWT tokens from Authorization header
- **Token Validation**: Backend validates tokens with Supabase for security

**Data Flow**:
- **Backend-Driven**: Backend domain models drive frontend type definitions
- **Offline-First**: Frontend local storage mirrors backend structure exactly
- **API Consistency**: Both systems use `ApiResponse<T>` wrapper for all responses
- **Error Handling**: Consistent error format defined by backend

**Field Naming Conventions**:
- **Backend**: snake_case (authoritative - `project_id`, `created_at`, `word_count`)
- **Frontend**: camelCase with mapping utilities (`projectId`, `createdAt`, `wordCount`)
- **API**: Backend handles both formats via Pydantic aliases

### Integration Development Workflow

**For Backend Changes (Primary)**:
1. **Modify Backend Models**: Update domain models in `/backend/src/database/interfaces/models/`
2. **Update Frontend Types**: Align `/frontend/src/lib/localdb/types.ts` to match backend exactly
3. **Update Local Provider**: Ensure local storage handles all backend fields
4. **Update Seed Data**: Include all backend fields in sample data
5. **Test Integration**: Verify frontend works with extended types

**For Frontend Features**:
1. **Check Backend Contract**: Review backend domain models and API endpoints first
2. **Align Frontend Types**: Ensure frontend types match backend structure
3. **Mock Implementation**: Use local storage that mirrors backend exactly
4. **Integration**: Test that frontend can consume backend API format

**⚠️  IMPORTANT**: Any changes to backend domain models MUST be reflected in frontend types immediately to maintain compatibility.

## Key Documentation

**📚 Essential**: [`/_docs/api/contracts.md`](_docs/api/contracts.md), [`/_docs/core/system-architecture.md`](_docs/core/system-architecture.md), [`/_docs/backend/overview.md`](_docs/backend/overview.md)

**🎯 Architecture**: [`/_docs/high-level/2-mvp.md`](_docs/high-level/2-mvp.md)

**⚙️ Development**: [`/_docs/development/environment-configuration.md`](_docs/development/environment-configuration.md)

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

**Critical Rule**: Always update CLAUDE.md files and relevant `/_docs/` files when making changes.

**Update Order**: 
1. **API Changes**: Update `/_docs/core/api-reference.md` and `/_docs/api/contracts.md`
2. **Frontend/Backend Changes**: Update respective CLAUDE files and main `CLAUDE.md` if integration changes
3. **Keep Cross-References Current**: Maintain links between documentation files

---

**Need specific guidance?** Check the specialized guides:
- 🎨 **Frontend**: [`/frontend/CLAUDE-frontend.md`](frontend/CLAUDE-frontend.md)
- ⚙️ **Backend**: [`/backend/CLAUDE-backend.md`](backend/CLAUDE-backend.md)
- 📚 **API**: [`/_docs/api/contracts.md`](_docs/api/contracts.md)