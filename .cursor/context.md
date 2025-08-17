# ShuScribe Project Context

This file provides essential context for AI assistants and IDE tools working with the ShuScribe codebase.

## Project Overview

**ShuScribe** is a frontend-centric Universe Content Management Platform for fiction writers and content creators.

### Core Architecture

**Three-Panel VS Code-like Interface**:
1. **File Explorer** (left) - Hierarchical project organization
2. **Document Editor** (center) - Rich text editing with @-reference system  
3. **AI Assistant** (right) - Context-aware writing assistance

**Technology Stack**:
- **Frontend**: Next.js 15.3.5, React 19, TypeScript, shadcn/ui, TanStack Query
- **Backend**: FastAPI, SQLAlchemy, Supabase (PostgreSQL)
- **Authentication**: Supabase Auth with OAuth
- **AI**: Self-hosted Portkey Gateway

## Key Design Decisions

### Performance-Optimized Type System

**Dual Type Architecture** for performance:
- **`api.ts`**: Backend interface layer (server communication)
- **`localdb/types.ts`**: Local cache layer (instant UI responses)

**Data Flow Pattern**:
```
User Action → Update Local Cache → Update UI (fast) → Background API Sync
```

### Frontend-First Development

**Philosophy**: Frontend drives development, backend provides robust APIs
- UI/UX decisions drive API design
- Local-first with offline capabilities
- Optimistic updates for instant feedback

### Path-Based Organization

Documents use file paths like `/world/regions/kingdoms/stormlands/cities` with automatic folder creation, eliminating manual folder management.

## Common Patterns

### Sidebar Pattern

Sidebars use `SidebarContainer.tsx` with built-in collapse buttons that disappear when hidden. Developers must implement re-expand buttons in header/main content areas.

### @-Reference System

Documents support `@character/name`, `@location/place` syntax for cross-references:
- Frontend-only implementation for performance
- Uses local file tree data for instant search results
- No backend integration to maintain speed

### Authentication Flow

- Frontend handles all auth via Supabase
- Backend validates JWT tokens
- Bearer token passed in Authorization header

## Development Context

### File Organization

```
frontend/src/
├── components/           # UI components
│   ├── workspace/       # Main layout and workspace components
│   ├── editor/          # Document editing components
│   ├── ui/              # Reusable UI primitives (shadcn/ui)
│   └── auth/            # Authentication components
├── lib/
│   ├── localdb/         # Local cache and types
│   ├── data/            # Data providers
│   └── supabase/        # Supabase client setup
└── types/
    └── api.ts           # Backend interface types
```

### Critical Files

**Type System**:
- `frontend/src/types/api.ts` - Server communication types
- `frontend/src/lib/localdb/types.ts` - Local cache types

**Core Components**:
- `SidebarContainer.tsx` - Reusable sidebar pattern
- `DocumentEditor.tsx` - Main editing interface
- `WorkspaceLayout.tsx` - Three-panel layout

**Data Management**:
- `local-provider.ts` - Local storage data provider
- `seeds.ts` - Development data seeding

### Environment

- **Development**: Frontend runs on port 3001, backend on 8000
- **Docker**: PostgreSQL and Portkey Gateway via docker-compose
- **Package Managers**: pnpm (frontend), uv (backend)

## AI Assistant Guidelines

When working with this codebase:

1. **Understand the dual type system** - Use appropriate types for cache vs API operations
2. **Follow the frontend-first philosophy** - Design UI first, then align backend
3. **Maintain performance patterns** - Preserve local-first optimizations
4. **Document architectural decisions** - Add file headers explaining purpose and rationale
5. **Respect the three-panel layout** - Keep VS Code-like workspace experience

## Quick Reference

**Development Commands**:
- Frontend: `cd frontend && pnpm dev`
- Backend: `cd backend && uv run hypercorn src.main:app --reload`
- Services: `docker-compose up -d`

**Key Documentation**:
- Main guide: `CLAUDE.md`
- Frontend: `frontend/CLAUDE-frontend.md`
- Backend: `backend/CLAUDE-backend.md`
- Architecture: `_docs/core/system-architecture.md`