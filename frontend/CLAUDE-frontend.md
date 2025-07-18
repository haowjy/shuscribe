# CLAUDE.md - Frontend Development Guide

This file provides frontend-specific guidance to Claude Code (claude.ai/code) when working with the ShuScribe frontend.

## 🔗 Multi-Repository Context

This is the **frontend-specific** guide. For complete project context, see:
- **Main Guide**: `/CLAUDE.md` - Overall project philosophy and coordination
- **Backend Guide**: `/backend/CLAUDE-backend.md` - Backend architecture and agent systems

## Frontend-First Philosophy

**Core Principle**: The frontend drives the development process and user experience.

**Key Aspects**:
- **API Contract Definition**: Frontend `src/types/api.ts` defines the API structure
- **Mock-First Development**: Use MSW and Next.js API routes for rapid prototyping
- **Type-Safe Integration**: Frontend TypeScript interfaces become backend Pydantic models
- **Authentication Leadership**: Frontend handles Supabase Auth, backend trusts tokens
- **Offline-First**: LocalStorage + TanStack Query provide offline functionality

**Development Flow**:
1. **Design UI/UX**: Create components and define user interactions
2. **Define API Contract**: Update `src/types/api.ts` with expected data structures
3. **Mock Implementation**: Use MSW for API mocking during development
4. **Backend Alignment**: Backend implements endpoints matching frontend expectations

## Development Commands

### Package Management
```bash
# Dependencies (prefer pnpm)
pnpm install                              # Install dependencies
pnpm add [package]                        # Add runtime dependency
pnpm add -D [package]                     # Add dev dependency

# UI Components (shadcn/ui)
pnpm dlx shadcn@latest add [component]    # Add shadcn components
pnpm dlx shadcn@latest add button input card dialog  # Example: multiple components
```

### Development Workflow
```bash
# CRITICAL: Never run these commands via Claude Code - user handles dev server
# User will run: npm run dev or pnpm dev

# Other commands you can run:
npm run build                             # Production build
npm run lint                              # Run ESLint
npm run start                             # Start production server
```

### Environment Setup
```bash
# 1. Copy environment template
cp .env.local.example .env.local

# 2. Configure Supabase variables in .env.local:
# NEXT_PUBLIC_SUPABASE_URL=your-supabase-project-url
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key

# 3. Restart dev server after environment changes (user handles this)
```

## Frontend Architecture

### Technology Stack
- **Framework**: Next.js 15.3.5 with App Router
- **React**: Version 19 with TypeScript
- **Styling**: Tailwind CSS v4 with design tokens
- **UI Components**: shadcn/ui + Radix UI primitives
- **Authentication**: Supabase Auth with SSR support
- **Layout**: react-resizable-panels for workspace
- **Build Tool**: Turbopack for fast development

### Core Application Design

**Three-Panel Workspace** (VS Code-like):
1. **File Explorer** - Project file tree with hierarchical organization
2. **Editor** - Tabbed document editor with @-reference system  
3. **AI Panel** - Context-aware AI assistance (future feature)

**Key Features**:
- **@-Reference System**: `@character/name` syntax for cross-document linking
- **Resizable Panels**: Collapsible sidebars with state persistence
- **Document Management**: Multi-tab editor with file operations
- **Authentication**: Email/password + Google OAuth integration

### Component Architecture

**Directory Structure**:
```
src/
   app/                 # Next.js App Router pages
      auth/           # Authentication flow pages
      layout.tsx      # Root layout with providers
      page.tsx        # Main workspace page
   components/         
      layout/         # Core workspace components
      ui/            # shadcn/ui components
   contexts/          # React contexts (AuthContext)
   lib/               # Utilities and configurations
      supabase/      # Supabase client setup
      utils.ts       # Utility functions
   middleware.ts      # Authentication middleware
```

**Component Patterns**:
- **Composition**: `<WorkspaceLayout fileExplorer={<FileExplorer />} editor={<Editor />} />`
- **Client Components**: Use `"use client"` for interactive components
- **Context Pattern**: AuthContext for global authentication state
- **Controlled Components**: Explicit state management for forms and modals

### Authentication System

**Architecture**:
- **Middleware Protection**: Route-level auth at `src/middleware.ts`
- **Dual Clients**: Browser (`createClient()`) and server (`await createClient()`)
- **Context Provider**: `useAuth()` hook for user state access
- **OAuth Flow**: Google OAuth with callback handling

**Usage Patterns**:
```typescript
// Access auth state in components
const { user, session, loading, signOut } = useAuth();

// Protect API routes (server components)
const supabase = await createClient();
const { data: { user } } = await supabase.auth.getUser();

// Client-side operations
const supabase = createClient();
await supabase.auth.signInWithPassword({ email, password });
```

**Route Structure**:
- `/auth/login` - Email/password + Google OAuth login
- `/auth/signup` - User registration with email confirmation
- `/auth/callback` - OAuth callback handler
- `/auth/auth-code-error` - Authentication error handling

### UI Development Patterns

**Design System**:
- **shadcn/ui**: Component library with consistent design tokens
- **Tailwind CSS**: Utility-first styling with custom properties
- **Lucide Icons**: Comprehensive icon library
- **Typography**: Geist Sans (UI) + Geist Mono (code)

**Component Development**:
```typescript
// Add new shadcn components
pnpm dlx shadcn@latest add sheet toast tabs

// Component composition pattern
export function NewFeature() {
  return (
    <WorkspaceLayout
      fileExplorer={<FileExplorer />}
      editor={<MyCustomEditor />}
      aiPanel={<AiPanel />}
    />
  );
}

// State management pattern
const [isCollapsed, setIsCollapsed] = useState(false);
const { user } = useAuth();
```

**Styling Guidelines**:
- Use Tailwind utility classes for consistent spacing/colors
- Leverage CSS custom properties for theme compatibility
- Prefer shadcn/ui components over custom implementations
- Use `cn()` utility for conditional class merging

### Key Development Notes

**@-Reference System** (Core Feature):
- Documents support `@character/name`, `@location/place` syntax
- References are visually highlighted in editor interface
- File explorer shows contextual tags on hover
- **Frontend-Only Implementation**: Search uses local file tree data for instant results
- **No Backend Integration**: Reference search stays in frontend for performance

**Panel Management**:
- Resizable panels use `react-resizable-panels` library
- Panel state persists across sessions (future enhancement)
- Collapse/expand functionality for both sidebars
- Responsive design adapts to screen size

**File Organization**:
- Hierarchical project structure: characters/, locations/, chapters/
- File tree supports nested folders and tagging
- Document tabs for multi-file editing
- Word count and auto-save indicators

**Error Handling**:
- Authentication errors redirect to `/auth/auth-code-error`
- Form validation using built-in HTML5 + custom logic
- Loading states use skeleton components
- Environment variable validation at runtime

### Common Development Tasks

**Adding New Components**:
1. Create component in appropriate directory (`components/layout/` or `components/ui/`)
2. Use TypeScript interfaces for props
3. Add `"use client"` if component needs interactivity
4. Export from index file if creating a component library

**Authentication Integration**:
1. Use `useAuth()` hook for client-side user state
2. Server components: use `await createClient()` from `@/lib/supabase/server`
3. Protected routes handled by middleware automatically
4. Manual redirects: `window.location.href = '/auth/login'`

**State Management** (Preferred Patterns):
1. **TanStack Query**: PREFERRED for server state, data fetching, and global state management (already configured)
2. **Local state**: `useState` for component-specific UI state only
3. **Context pattern**: Only for authentication state (AuthContext) - avoid for other global state
4. **Form state**: `react-hook-form` for complex forms with validation
5. **Async state**: Use TanStack Query hooks instead of manual loading states

**State Management Guidelines**:
- **ALWAYS prefer TanStack Query** for data that comes from APIs or needs to be shared across components
- Use `useState` only for purely local UI state (modals open/closed, form inputs, etc.)
- Avoid prop drilling - use TanStack Query's `useQueryClient()` to access shared state
- Create custom hooks in `src/lib/query/hooks.ts` for reusable state management patterns

**Environment Variables**:
- All public vars must be prefixed with `NEXT_PUBLIC_`
- Supabase configuration required for authentication
- Environment changes require dev server restart (user handles)
- Use TypeScript for environment variable validation

### Important Restrictions

**Development Server**:
- **NEVER run `npm run dev`, `pnpm dev`, or similar commands via Claude Code**
- User handles all development server operations
- Environment changes require manual server restart
- Build and lint commands are safe to run

**Component Library**:
- Prefer shadcn/ui components over custom implementations
- Use Radix UI primitives for complex interactive components
- Maintain design system consistency with existing patterns
- Test component accessibility and keyboard navigation

**Authentication Security**:
- Never expose private keys or sensitive config
- Use server-side auth validation for protected data
- Client-side auth is for UX only, not security
- Always validate auth state on server for API calls

## Backend Integration

### API Integration Patterns

**Response Format**:
- Backend returns `ApiResponse<T>` wrapper matching frontend expectations
- Consistent error handling with `{ error: string, message: string, status: number }`
- Success responses: `{ data: T, status: number }`

**Field Naming**:
- Frontend uses camelCase: `projectId`, `wordCount`, `createdAt`
- Backend uses Pydantic aliases to handle both camelCase and snake_case
- Models automatically convert between naming conventions

**Authentication Flow**:
- Frontend handles all Supabase Auth operations
- Backend extracts tokens from `Authorization: Bearer <token>` header
- Backend trusts frontend authentication, doesn't validate tokens
- Backend uses token context for logging and user identification

### API Contract Definition

**Primary Contract**: `src/types/api.ts`
- Defines all API request/response interfaces
- Used by backend to create matching Pydantic models
- Single source of truth for API structure

**Key Interfaces**:
- `ApiResponse<T>`: Standard response wrapper
- `Document`, `DocumentContent`: ProseMirror document structure
- `ProjectDetails`, `FileTreeResponse`: Project and file system data
- `ApiError`: Standardized error responses

### Integration Development

**When Adding New API Endpoints**:
1. **Define in Frontend**: Add interfaces to `src/types/api.ts`
2. **Create Mock**: Add MSW handler for development
3. **Update Backend**: Backend implements matching endpoint
4. **Test Integration**: Verify field naming and response format consistency

**When Backend Changes**:
1. **Check Contract**: Ensure changes match `src/types/api.ts`
2. **Update Frontend**: Modify interfaces if needed
3. **Update Mocks**: Keep MSW handlers in sync
4. **Test Flow**: Verify entire frontend-backend integration

## Frontend Route Architecture

### Route Structure and Navigation

**Entry Point Behavior** (Updated):
- **Route**: `/`
- **Behavior**: 
  - With `?project=<id>` → Shows workspace for specific project
  - Without project parameter → **Redirects to `/dashboard`** for project selection

**Core Application Flow**:
```
Landing (/) 
    ↓ (no project ID)
Dashboard (/dashboard) ← NEW: Proper project selection
    ↓ (user selects project)
Workspace (/?project=<id>) ← Project-specific editing workspace
```

**Authentication Flow**:
```
Protected Route → Login (/auth/login) → Dashboard or Original Route
```

**Key Route Features**:
- **Dashboard-First**: Users see project list instead of hardcoded project
- **Project Validation**: Routes validate project existence and access
- **Graceful Fallbacks**: Invalid projects redirect to dashboard
- **Deep Linking**: Direct workspace URLs work with proper project IDs

### Route-Component Mapping

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | `src/app/page.tsx` | Entry point - redirects to dashboard or shows workspace |
| `/dashboard` | `src/app/dashboard/page.tsx` | Project selection hub |
| `/dashboard/new` | `src/app/dashboard/new/page.tsx` | Project creation wizard |
| `/auth/login` | `src/app/auth/login/page.tsx` | Authentication |
| `/auth/signup` | `src/app/auth/signup/page.tsx` | User registration |

### API Route Integration

**Next.js API Routes** (Development):
- `/api/documents/[id]` - Document CRUD operations (proxies to backend)
- `/api/projects/[id]/data` - Project data aggregation

**Backend API Mapping**:
- Dashboard projects → `GET /api/v1/projects`
- Workspace file tree → `GET /api/v1/projects/{id}/file-tree`
- Document operations → `GET/PUT /api/v1/documents/{id}`

## Documentation Resources

### Core Documentation (`/_docs/core/`)
- **📚 API Reference**: [`/_docs/core/api-reference.md`](/_docs/core/api-reference.md) - Complete API documentation with request/response examples
- **🗺️ Frontend Routes**: [`/_docs/core/frontend-routes.md`](/_docs/core/frontend-routes.md) - Complete routing documentation and navigation patterns
- **🎨 Frontend Guide**: [`/_docs/core/frontend-guide.md`](/_docs/core/frontend-guide.md) - Component architecture, @-reference system, UI patterns (planned)
- **🔗 Integration Guide**: [`/_docs/core/integration-guide.md`](/_docs/core/integration-guide.md) - Frontend-backend integration patterns (planned)

### High-Level Documentation (`/_docs/high-level/`)
- **📖 Product Overview**: [`/_docs/high-level/1-product-overview.md`](/_docs/high-level/1-product-overview.md) - System architecture and goals
- **🎨 Frontend Architecture**: [`/_docs/high-level/3-frontend.md`](/_docs/high-level/3-frontend.md) - High-level frontend design decisions

### API Documentation (`/_docs/api/`)
- **📝 API Contracts**: [`/_docs/api/contracts.md`](/_docs/api/contracts.md) - Frontend-backend interface definitions
- **🔗 Field Mapping**: [`/_docs/api/field-mapping.md`](/_docs/api/field-mapping.md) - camelCase/snake_case conversion guide (planned)
- **🔐 Authentication**: [`/_docs/api/authentication.md`](/_docs/api/authentication.md) - Auth implementation details (planned)

### Development Documentation (`/_docs/development/`)
- **🛠️ Environment Setup**: [`/_docs/development/environment-setup.md`](/_docs/development/environment-setup.md) - Complete dev environment guide (planned)
- **🧪 Testing Strategy**: [`/_docs/development/testing-strategy.md`](/_docs/development/testing-strategy.md) - Frontend testing approach (planned)
- **🚀 Deployment Guide**: [`/_docs/development/deployment-guide.md`](/_docs/development/deployment-guide.md) - Production deployment (planned)

### Frontend-Specific Resources
- **shadcn/ui Components**: Use `pnpm dlx shadcn@latest add [component]` for new UI components
- **Tailwind Documentation**: CSS utility classes and design system integration
- **TanStack Query**: State management and server synchronization patterns
- **Next.js Documentation**: App Router, middleware, and SSR patterns

## Frontend Documentation Maintenance

When making frontend changes, update documentation in this order:

#### Core Documentation Updates
- **Component Pattern Changes**: Update `/_docs/core/frontend-guide.md` (when created) with new patterns
- **API Interface Changes**: Update `/_docs/api/contracts.md` with new interface definitions
- **Integration Changes**: Update `/_docs/core/integration-guide.md` (when created) if affecting backend

#### This CLAUDE File Updates
- **Add short description** of any significant frontend architecture changes
- **Update component examples** if new UI patterns are introduced
- **Note new dependencies** or environment variable requirements

#### Cross-Reference Updates
- **API Contract Changes**: Update `src/types/api.ts` and notify backend team
- **Authentication Changes**: Update `/_docs/api/authentication.md` (when created)
- **Main CLAUDE.md**: Update if core integration principles change

### Frontend Documentation Scope
- **Component Architecture**: Three-panel workspace, composition patterns, client components
- **Authentication**: Supabase Auth integration, middleware protection, dual client setup
- **UI Patterns**: shadcn/ui usage, Tailwind styling, responsive design
- **State Management**: TanStack Query, LocalStorage, offline-first approach
- **@-Reference System**: Cross-document linking, search implementation, file tree integration