# ShuScribe Frontend Routes

Complete routing documentation for the ShuScribe frontend application.

## Table of Contents

- [Overview](#overview)
- [Public Routes](#public-routes)
- [Authentication Routes](#authentication-routes)
- [Application Routes](#application-routes)
- [API Routes (Next.js)](#api-routes-nextjs)
- [Route Parameters](#route-parameters)
- [Navigation Patterns](#navigation-patterns)

## Overview

**Framework**: Next.js 15 App Router  
**Base URL**: `http://localhost:3001`  
**Routing Strategy**: File-based routing with App Router conventions  
**Authentication**: Protected routes redirect to `/auth/login`

ShuScribe uses Next.js App Router for client-side navigation and server-side rendering. Routes are organized to provide a clear user flow from authentication through project management to the writing workspace.

## Public Routes

### Landing Page
- **Route**: `/`
- **Component**: `src/app/page.tsx`
- **Purpose**: Entry point - redirects to dashboard if no project selected
- **Behavior**: 
  - With `?project=<id>` → Shows workspace for specific project
  - Without project parameter → Redirects to `/dashboard`

## Authentication Routes

### Login Page
- **Route**: `/auth/login`
- **Component**: `src/app/auth/login/page.tsx`
- **Purpose**: User authentication with email/password or OAuth
- **Features**: Supabase Auth integration, form validation

### Signup Page
- **Route**: `/auth/signup`
- **Component**: `src/app/auth/signup/page.tsx`
- **Purpose**: New user registration
- **Features**: Account creation, email verification

### Auth Callback
- **Route**: `/auth/callback`
- **Component**: `src/app/auth/callback/route.ts`
- **Purpose**: OAuth callback handler for social login
- **Type**: Server-side route handler

### Auth Error Page
- **Route**: `/auth/auth-code-error`
- **Component**: `src/app/auth/auth-code-error/page.tsx`
- **Purpose**: Displays authentication errors
- **Features**: Error message display, retry options

## Application Routes

### Dashboard
- **Route**: `/dashboard`
- **Component**: `src/app/dashboard/page.tsx`
- **Purpose**: Project selection and management hub
- **Features**: 
  - Project list with metadata (word count, document count, last updated)
  - Create new project button
  - Project cards with click-to-open functionality
  - Empty state for new users

### New Project
- **Route**: `/dashboard/new`
- **Component**: `src/app/dashboard/new/page.tsx`
- **Purpose**: Project creation wizard
- **Features**: Template selection, project configuration

### Workspace (Main Editor)
- **Route**: `/?project=<projectId>`
- **Component**: `src/app/page.tsx`
- **Purpose**: Main writing workspace with three-panel layout
- **Features**:
  - File explorer panel
  - Multi-tab editor with @reference system
  - AI assistance panel (future)
  - Project-specific file tree and documents

### Test Storage Page
- **Route**: `/test-storage`
- **Component**: `src/app/test-storage/page.tsx`
- **Purpose**: Development utility for testing localStorage functionality
- **Environment**: Development only

## API Routes (Next.js)

ShuScribe includes Next.js API routes for development and MSW integration:

### Document Routes
- **Route**: `/api/documents/[id]`
- **Handler**: `src/app/api/documents/[id]/route.ts`
- **Methods**: GET, PUT, DELETE
- **Purpose**: Document CRUD operations (proxies to backend)

### Documents Collection
- **Route**: `/api/documents`
- **Handler**: `src/app/api/documents/route.ts`
- **Methods**: GET, POST
- **Purpose**: Document listing and creation

### Project Data
- **Route**: `/api/projects/[id]/data`
- **Handler**: `src/app/api/projects/[id]/data/route.ts`
- **Methods**: GET
- **Purpose**: Project data aggregation with file tree and documents

## Route Parameters

### Project ID Parameter
- **Format**: `?project=<projectId>`
- **Example**: `/?project=prj_fantasy_novel`
- **Validation**: Should match backend project ID format
- **Fallback**: Redirects to `/dashboard` if invalid or missing

### Document ID Parameter
- **Format**: `[id]` in dynamic routes
- **Example**: `/api/documents/doc_chapter_01`
- **Validation**: Backend validates document existence and access

## Navigation Patterns

### App Navigation Flow
```
Landing (/) 
    ↓ (no project)
Dashboard (/dashboard)
    ↓ (select project)
Workspace (/?project=<id>)
    ↓ (project-specific editing)
```

**Development URLs**:
- **Frontend**: `http://localhost:3001` (configured to avoid port conflicts)
- **Backend API**: `http://localhost:8000/api/v1`

### Authentication Flow
```
Protected Route
    ↓ (not authenticated)
Login (/auth/login)
    ↓ (social login)
Callback (/auth/callback)
    ↓ (success)
Original Route or Dashboard
```

### Error Handling
```
Authentication Error
    ↓
Auth Error Page (/auth/auth-code-error)
    ↓ (retry)
Login (/auth/login)
```

## Route Guards and Middleware

### Authentication Middleware
- **File**: `src/middleware.ts`
- **Purpose**: Protects routes requiring authentication
- **Logic**: Redirects unauthenticated users to `/auth/login`
- **Protected Routes**: `/*` (except auth routes and public assets)

### Route Protection Patterns
- **Public Routes**: `/auth/*`, `/api/*` (Next.js API routes)
- **Protected Routes**: `/`, `/dashboard/*`, main application routes
- **Conditional Routes**: `/` redirects based on project parameter

## Frontend Route Mapping to Backend

### Project Operations
- **Frontend**: `/dashboard` → **Backend**: `GET /api/v1/projects`
- **Frontend**: `/?project=<id>` → **Backend**: `GET /api/v1/projects/{id}/file-tree`

### Document Operations  
- **Frontend**: Editor workspace → **Backend**: `GET /api/v1/documents/{id}`
- **Frontend**: Document save → **Backend**: `PUT /api/v1/documents/{id}`

### File Tree Operations
- **Frontend**: File explorer → **Backend**: `GET /api/v1/projects/{id}/file-tree`
- **Frontend**: @references → **Local**: Frontend search on file tree data

## Development Notes

### Route Testing
- Use browser navigation to test route transitions
- Verify authentication redirects work correctly
- Test project parameter validation
- Ensure proper fallbacks for invalid routes

### Future Route Additions
Planned routes for future features:
- `/projects/{id}/settings` - Project configuration
- `/projects/{id}/collaborators` - Team management  
- `/ai/chat` - AI assistance interface
- `/profile` - User profile management

### Route Performance
- App Router enables automatic code splitting per route
- Static routes are pre-rendered where possible
- Dynamic routes use server-side rendering for SEO
- Client-side navigation provides instant transitions

## Related Documentation

- **Backend API**: [`/_docs/core/api-reference.md`](./api-reference.md)
- **Frontend Architecture**: [`/_docs/high-level/3-frontend.md`](../high-level/3-frontend.md)
- **Authentication Guide**: [`/_docs/api/authentication.md`](../api/authentication.md) (planned)