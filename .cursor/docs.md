# ShuScribe Documentation Guidelines

This file provides IDE-specific documentation standards for the ShuScribe project, designed for AI assistants and code analysis tools.

## Code Documentation Standards

### File Headers Required

Every significant file should start with a comprehensive header comment explaining:

```typescript
/**
 * [File Purpose] - [Architecture Role]
 * 
 * [Performance/Design Rationale]
 * [Integration Patterns]
 * [Usage Guidelines]
 */
```

### Priority Files for Documentation

**Type System Files** (Critical for understanding data flow):
- `/frontend/src/types/api.ts` - Backend interface layer
- `/frontend/src/lib/localdb/types.ts` - Local cache optimization layer

**Core UI Patterns**:
- `/frontend/src/components/workspace/shared/SidebarContainer.tsx` - Reusable sidebar pattern
- Layout components in `/frontend/src/components/workspace/layout/`
- Editor components in `/frontend/src/components/editor/`

**Data & State Management**:
- Provider components in `/frontend/src/components/providers/`
- Data management in `/frontend/src/lib/data/`
- Local database utilities in `/frontend/src/lib/localdb/`

### Documentation Balance

**In Code Comments**:
- Implementation details and complex logic
- Performance rationale and optimization decisions
- Integration patterns with other components
- Usage guidelines and examples

**External Documentation** (`_docs/`, `CLAUDE.md`):
- High-level architecture decisions
- System design and component relationships  
- Development workflows and best practices
- Cross-component integration patterns

## Architecture Context

### Performance-First Design

ShuScribe uses a **dual type system** for performance optimization:
- `api.ts`: Server communication layer (network calls)
- `localdb/types.ts`: Local cache layer (instant UI responses)

This pattern enables:
- Instant UI updates from local cache
- Background server synchronization
- Offline-first functionality

### Frontend-Centric Development

- Frontend drives feature development and UX decisions
- Backend provides well-designed APIs to support frontend needs
- Local-first data patterns with server sync
- Component-driven architecture with reusable UI patterns

## Comment Guidelines

### When to Document

**Always Document**:
- File purpose and architecture role
- Performance optimization decisions
- Complex business logic
- Integration patterns between components
- Non-obvious design decisions

**Avoid Over-Documenting**:
- Self-explanatory code
- Basic TypeScript patterns
- Standard React patterns
- Simple utility functions

### Comment Style

Use JSDoc format for functions and complex logic:

```typescript
/**
 * Converts backend snake_case fields to frontend camelCase
 * 
 * This enables the dual type system performance optimization
 * by allowing seamless data flow between cache and API layers.
 * 
 * @param backendData - Raw data from API response
 * @returns Frontend-optimized data structure
 */
```

## IDE Integration

This documentation is designed to help AI assistants and IDE tools understand:
- Why certain architectural decisions were made
- How components fit together in the larger system
- Performance implications of different patterns
- When to follow specific coding patterns

The goal is to make the codebase self-documenting while maintaining the performance-optimized architecture.