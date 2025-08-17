# Frontend-Backend Integration Architecture

## Core Integration Principles

**CRITICAL**: Backend defines good API design, frontend defines the feature set and user experience.

### Balanced Design Philosophy

- **Backend**: Provides well-designed APIs, data validation, and business logic
- **Frontend**: Drives feature development and user experience decisions
- **API Contract**: Backend creates robust endpoints, frontend consumes and extends with local-first patterns
- **Data Validation**: Backend ensures data integrity, frontend handles user interaction patterns

## Performance-Optimized Type Architecture

ShuScribe uses a dual type system optimized for performance and offline-first functionality:

### Backend Interface Layer (`/frontend/src/types/api.ts`)
- **Purpose**: Server communication types (269 lines)
- **Handles**: HTTP requests, API responses, field mapping utilities
- **Used for**: Fetching from server, posting to server, real-time sync

### Local Storage Cache Layer (`/frontend/src/lib/localdb/types.ts`)
- **Purpose**: Local cache optimization (173 lines)
- **Optimized for**: Instant UI responses and offline-first experience
- **Used for**: Component state, local queries, optimistic updates

### Performance Benefits
- UI reads from local cache instantly (no network latency)
- Background sync keeps cache updated asynchronously
- Offline-first: App works without network connection

### Data Flow Pattern
```
User Action → Update localdb cache → Update UI (fast) → Background API sync
```

## Authentication Strategy

- **Frontend**: Handles all authentication via Supabase Auth
- **Backend**: Validates Supabase JWT tokens from Authorization header
- **Token Validation**: Backend validates tokens with Supabase for security

## Data Flow Architecture

- **Frontend-Centric**: Frontend drives development with local-first patterns
- **Backend Integration**: API layer handles data synchronization when online
- **Field Mapping**: `FIELD_MAPPINGS` array in `api.ts` handles case conversion automatically
- **Error Handling**: Consistent error format with frontend-friendly messaging

## Field Naming Conventions

- **Backend**: snake_case (database/API - `project_id`, `created_at`, `word_count`)
- **Frontend**: camelCase (application layer - `projectId`, `createdAt`, `wordCount`)
- **Conversion**: Automatic mapping via utilities in `localdb/types.ts`

## Integration Development Workflow

### For Frontend Features (Primary)
1. **Design Frontend Experience**: Create UI components and define user interactions
2. **Define Local Types**: Use `/frontend/src/lib/localdb/types.ts` for working with data
3. **Mock Data**: Use local storage for immediate development and testing
4. **API Integration**: Align with backend contracts via `/frontend/src/types/api.ts`
5. **Field Mapping**: Ensure automatic conversion between naming conventions

### For Backend API Updates
1. **Review Frontend Needs**: Check what frontend features require from the API
2. **Design API Contract**: Create backend endpoints that serve frontend requirements
3. **Update API Types**: Modify `/frontend/src/types/api.ts` to match backend responses
4. **Test Integration**: Verify field mapping and data synchronization works correctly

### Critical Rule
⚠️ **IMPORTANT**: Changes to either type system should maintain compatibility through the field mapping utilities.

## Common Integration Patterns

- Frontend `src/types/api.ts` defines the API contract
- Backend `src/schemas/` models match frontend types with field aliases
- Both systems use `ApiResponse<T>` wrapper for consistent responses
- Authentication context flows from frontend to backend via Bearer tokens
- **Path-Based Document Creation**: Documents automatically create folder hierarchies from paths (e.g., `/characters/locations/taverns/document` creates all missing folders)

## @-Reference System Implementation

- Documents support `@character/name`, `@location/place` syntax for cross-references
- References are highlighted and clickable in editor
- **Frontend-Only Implementation**: Search uses local file tree data for instant results
- **No Backend Integration**: Reference search stays in frontend for performance