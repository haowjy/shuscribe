# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. It is Aug 2025.

## Essential Tools

* context7: when the user requests code examples, setup or configuration steps, or library/API documentation
* Use `uv run python` for running Python commands in the backend

## Key Development Notes

### Critical Rules

- **Always think about best practices and patterns for the code you are writing**
- **Always think about the user experience and the code you are writing**
- **Always think about the code you are writing**
- **Reasoning-First Documentation**: Always explain WHY we follow a pattern, rule, or make a design decision, not just what to do. Understanding reasoning helps developers adapt principles to new situations and avoid cargo-cult programming. For all future documentation: Include the rationale behind every significant decision.
- **Question for Understanding**: When faced with unclear requirements or non-straightforward problems, always ask the user for the reasoning and context behind what they're trying to achieve. Understanding the WHY helps create better solutions than just implementing the WHAT.
- **Frontend Dev Server**: NEVER run `npm run dev`, `pnpm dev` via Claude Code - user handles this (WHY: Maintains user workflow control and prevents port conflicts with their development environment)
- **Cross-References**: Update all CLAUDE.md and other documentation files when making changes that affect the documentation
- **Never directly edit `pyproject.toml` or `package.json`**: ALWAYS use the package manager (`uv` for backend, or `pnpm` for frontend) (WHY: Package managers handle dependency resolution, lock files, and virtual environments correctly)
- **Always use absolute file paths for Python FastAPI, never use relative paths** (WHY: Prevents deployment issues and import resolution problems across different environments)
- **Tailwind Best Practices**: Use utility-first approach with direct classes in JSX. Never create CSS_CLASSES constants - this is an anti-pattern that defeats Tailwind's purpose and breaks JIT compilation (WHY: Constants prevent JIT optimization and break Tailwind's utility-first philosophy for maintainable styles)
- **Update CLAUDE.md**: Make sure to ALWAYS update the CLAUDE.md and/or other documentation files when making changes that affect the documentation.
- **Documentation**: Most documentation should be pretty sparse. Each document should not be excessively long. Please split out new documents if a document is becoming too long and has multiple purposes (WHY: Reduces maintenance burden and prevents documentation drift by keeping docs focused and manageable)

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

- **Implemented**: Comprehensive workspace system with studio projects (`/studio/[id]`), DocumentEditor with configurable toolbar/footer, Supabase auth integration, component gallery (`/component-gallery/editor/`), three-panel layout system (📚 [`/_docs/frontend/DOCUMENT-EDITOR.md`](_docs/frontend/DOCUMENT-EDITOR.md)).
- **In Development**: TanStack Query integration, API routes/mocks, @-reference system, backend synchronization.

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

- **🔗 Integration Work**: See [`/_docs/core/integration-architecture.md`](_docs/core/integration-architecture.md) for frontend-backend integration patterns

## Key Documentation

**📚 Essential**: [`/_docs/api/contracts.md`](_docs/api/contracts.md), [`/_docs/core/system-architecture.md`](_docs/core/system-architecture.md), [`/_docs/backend/overview.md`](_docs/backend/overview.md)

**🔗 Integration**: [`/_docs/core/integration-architecture.md`](_docs/core/integration-architecture.md) - Frontend-backend patterns and performance architecture

**🎨 UI Patterns**: [`/_docs/frontend/ui-patterns.md`](_docs/frontend/ui-patterns.md) - Sidebar, navigation, and component patterns

**🎯 Architecture**: [`/_docs/high-level/2-mvp.md`](_docs/high-level/2-mvp.md)

**⚙️ Development**: [`/_docs/development/environment-configuration.md`](_docs/development/environment-configuration.md)

## Architecture Overview

ShuScribe is a **frontend-centric** Universe Content Management Platform with VS Code-like three-panel workspace.

**Key Technologies**:
- **Frontend**: Next.js 15.3.5, React 19, TypeScript, shadcn/ui, TanStack Query
- **Backend**: FastAPI, SQLAlchemy, Supabase (PostgreSQL), Repository pattern
- **Authentication**: Supabase Auth with OAuth support
- **AI**: Self-hosted Portkey Gateway with multiple LLM providers
- **Deployment**: Railway (two-service architecture) + Vercel

📚 **Detailed Architecture**: See [`/_docs/core/system-architecture.md`](_docs/core/system-architecture.md)

### Frontend vs Backend Route Architecture

**Frontend Routes**: `/studio` (UI workspace concept)
- `/studio` - Author's creative workspace containing multiple projects
- `/studio/[id]` - Individual project workspace within studio
- Represents the user interface navigation and workspace organization

**Backend APIs**: `/projects` (data resource management)  
- `/projects` - CRUD operations for project data entities
- `/projects/{id}` - Individual project data management
- Represents RESTful resource management regardless of UI presentation

**Why Different?**
- **Separation of Concerns**: UI navigation vs data management
- **API Stability**: Backend endpoints remain consistent regardless of frontend redesigns
- **Semantic Clarity**: Frontend "studio" = workspace concept, Backend "projects" = data entities
- **Future Flexibility**: Frontend can rebrand/restructure without breaking API contracts

📚 **WHY**: This architecture prevents frontend UI changes from breaking backend APIs and allows independent evolution of presentation layer and data layer.

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

### Core Features

- **@-Reference System**: Cross-reference syntax (`@character/name`) with frontend-only search
- **Path-Based Organization**: Automatic folder creation from document paths
- **Dual Type System**: Performance-optimized with local cache and API layers

📚 **Implementation Details**: See [`/_docs/frontend/ui-patterns.md`](_docs/frontend/ui-patterns.md) and [`/_docs/core/integration-architecture.md`](_docs/core/integration-architecture.md)

## Documentation Philosophy

ShuScribe follows a **reasoning-first, code-centric documentation approach** that prioritizes maintainability and decision context.

### Core Principles

**1. Reasoning-First Documentation**
- Always start with WHY: Explain the problem context and reasoning behind decisions
- Document the rationale before describing the solution (WHY: Helps developers adapt principles to new situations rather than cargo-cult programming)
- Future documentation must include decision context for long-term maintainability
- WHY: Reasoning ages better than implementation details and enables better decision-making

**2. Documentation Points to Code, Never Duplicates It**
- Documentation explains architecture, design decisions, and file organization
- Code examples are avoided—instead, point to actual implementation files
- API signatures, interfaces, and configurations live only in code
- Documentation describes *what* and *why*, code shows *how*
- WHY: Code duplication in docs becomes stale immediately, while architecture reasoning remains relevant

**3. Structure Over Snippets**
- Document component hierarchies, folder organization, and relationships with reasoning for the structure
- Explain integration patterns and data flow with context for why these patterns were chosen
- Reference specific files and functions: `ComponentName.tsx:functionName()`
- Use diagrams and architectural overviews instead of code blocks
- WHY: Structural documentation remains relevant longer than implementation details

**4. Maintenance-First Approach**
- Documentation that duplicates code becomes stale immediately
- File references auto-break when renamed, forcing updates
- Keep docs focused on concepts that don't change frequently
- Prefer linking to implementation over describing implementation
- WHY: Reduces long-term maintenance burden and prevents documentation drift that misleads developers

**5. Audience-Specific Documentation**
- **CLAUDE.md files**: Development guidance and project coordination
- **_docs/ files**: Architecture, design decisions, and system overviews  
- **README files**: Quick setup and orientation
- **Comments in code**: Implementation details and complex logic
- **.cursor/ files**: IDE-specific documentation and context for AI assistants

### Documentation Types

**Architecture Documentation** (`_docs/`)
- System design and component relationships
- Integration patterns and data flow
- Future roadmap and evolution plans
- Design decisions and trade-offs

**Development Guidance** (`CLAUDE-*.md`)
- Development workflows and best practices
- File organization and naming conventions
- Common patterns and anti-patterns
- Tool usage and environment setup

**Code Documentation Standards** (within files)
- **File Headers**: Every significant file must have a purpose comment at the top explaining WHY it exists
- **Architecture Role**: Explain how the file fits into overall system design and WHY this approach was chosen
- **WHY-First Rationale**: Document why design decisions were made, not just what they do (essential for optimization and architectural patterns)
- **Problem Context**: Explain what problem the file solves and why this solution was chosen
- **Usage Patterns**: Guide developers on when and how to use the code, including reasoning for usage decisions
- **Integration Points**: Explain how the file connects to other parts of the system and WHY these connections exist

**Required File Header Format**:
```typescript
/**
 * [File Purpose] - [Architecture Role]
 * 
 * WHY: [Problem Context and Design Rationale]
 * [Integration Patterns and Reasoning]
 * [Usage Guidelines with Context]
 */
```

**Critical**: All file headers must explain the reasoning behind design decisions. Future developers need to understand WHY choices were made to adapt and extend the code correctly.

### Anti-Patterns to Avoid

❌ **Code Snippets in Documentation**
```tsx
// DON'T DO THIS - will become outdated
interface ComponentProps {
  prop1: string;
  prop2: boolean;
}
```

✅ **Reference Implementation**
```markdown
Props interface: See `ComponentProps` in `components/Component.tsx`
```

❌ **Describing Implementation Details**
"The component uses useState to manage open state and useEffect to handle..."

✅ **Describing Purpose and Usage**  
"Component provides collapsible content areas. See implementation: `CollapsiblePanel.tsx`"

❌ **Duplicating Configuration**
"Set these environment variables: NEXT_PUBLIC_SUPABASE_URL=..."

✅ **Pointing to Source**
"Environment setup: See `.env.local.example` for required variables"

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
- 