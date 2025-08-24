# Universal @-Reference System Implementation Guide

**WHY**: ShuScribe needs a unified reference system that enables seamless cross-linking between files, tags, and other entities while maintaining stable references that don't break when content is renamed or moved. This system serves as the foundation for AI-powered universe management where context relationships are critical.

## System Overview

The universal @-reference system provides a unified interface for linking to any entity in the ShuScribe universe through a consistent `@` trigger mechanism with intelligent autocomplete.

### Core Principles

**1. Stable Reference Management**
- All references use stable UUIDs, never display names
- Display names can change without breaking links
- Backend maintains relationship integrity across renames

**2. AI-Optimized Format**
- References appear as natural text to AI models
- Markdown-native format with no conversion overhead
- Context-rich for AI understanding and generation

**3. Extensible Architecture**
- Unified picker supports multiple entity types
- Easy to add new reference types (locations, chapters, etc.)
- Consistent UX patterns across all reference types

**4. Frontend-First Performance**
- Instant autocomplete from local cache
- Real-time filtering and search
- Zero latency for typing and selection

## Reference Types

### File References
**Purpose**: Link to documents, characters, locations, chapters
**Format**: `::ref[Elara Mitchell]{#file-abc123 type="file" subtype="character"}`
**Trigger**: `@` followed by file name search
**Display**: Shows current file name, links to document

### Tag References  
**Purpose**: Link to thematic collections and categories
**Format**: `::ref[Fantasy]{#tag-def456 type="tag"}`
**Trigger**: `@#` or `@tag:` followed by tag name search
**Display**: Shows tag name with count, links to tag view

### Future Extensions
**Timeline References**: `@timeline:medieval-period`
**Chapter References**: `@chapter:the-awakening` 
**Location References**: `@location:thornfield-manor`
**Relationship References**: `@relationship:elara-thomas`

## Architecture & Data Flow

### Frontend Architecture

```
User Input (@) → Reference Picker → Selection → Directive Insertion
     ↓              ↓                ↓              ↓
Text Detection → Entity Search → Stable ID → Markdown Storage
```

### Backend Schema

**References Table**
```sql
CREATE TABLE references (
  id UUID PRIMARY KEY,
  source_document_id UUID NOT NULL,
  target_entity_id UUID NOT NULL,
  target_entity_type VARCHAR(50) NOT NULL, -- 'file', 'tag', etc.
  display_text VARCHAR(255) NOT NULL,
  position_start INTEGER NOT NULL,
  position_end INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Entity Resolution**
- Files: Resolved via `documents` table
- Tags: Resolved via `tags` table  
- Future: Extensible to any entity with stable ID

### Data Flow Sequence

1. **User types `@`** → Trigger detection in editor
2. **Picker opens** → Load entities from local cache
3. **User types filter** → Real-time search across entities
4. **User selects** → Insert directive with stable ID
5. **Background sync** → Update references table
6. **Display update** → Show current entity name
7. **AI processing** → Sees natural text in context

## Technical Implementation

### MDXEditor Integration

**Custom Reference Plugin**
```typescript
const universalReferencePlugin = realmPlugin({
  init(realm) {
    // Register @ trigger detection
    // Initialize entity picker component
    // Handle directive insertion and rendering
  }
})
```

**Directive Configuration**
```typescript
const ReferenceDirectiveDescriptor: DirectiveDescriptor = {
  name: 'ref',
  testNode(node) { return node.name === 'ref' },
  attributes: ['id', 'type', 'subtype'],
  hasChildren: false,
  Editor: ReferenceEditor
}
```

### Reference Picker Component

**Core Features**
- Fuzzy search across all entity types
- Type-ahead filtering with visual indicators
- Keyboard navigation (arrows, Enter, Escape)
- Category grouping (Files, Tags, etc.)
- Recent/frequent references priority

**Search Algorithm**
```typescript
interface EntitySearchResult {
  id: string
  type: 'file' | 'tag' | 'location' // etc.
  displayName: string
  subtype?: string // 'character', 'chapter', etc.
  path?: string // for files
  matchScore: number
  recentlyUsed: boolean
}
```

### Lexical Plugin Implementation

**@ Trigger Detection**
```typescript
// Monitor text input for @ character
// Show picker when @ detected
// Filter entities as user continues typing
// Handle selection and directive insertion
```

**State Management**
- Track picker open/closed state
- Manage filtered entity list
- Handle selection and insertion
- Sync with backend references table

## UX Patterns & Interface Design

### Picker Interface Design

**Visual Hierarchy**
- Group by entity type (Files, Tags, etc.)
- Show entity icons and type indicators
- Highlight matching text in search results
- Display entity metadata (path, count, etc.)

**Interaction Patterns**
- `@` opens picker with all entities
- `@#` or `@tag:` filters to tags only
- `@file:` filters to files only
- Arrow keys navigate, Enter selects
- Escape cancels, clicking outside closes

**Real-time Search**
- Filter as user types after `@`
- Fuzzy matching on names and paths  
- Prioritize recently used references
- Show "No matches" when filter returns empty

### Reference Display & Editing

**In-Editor Appearance**
- Clickable links with entity icons
- Hover shows entity preview/metadata
- Right-click menu for reference actions
- Visual indicators for broken references

**Reference Actions**
- Click → Navigate to referenced entity
- Hover → Show quick preview
- Right-click → Rename, Remove, Copy ID
- Bulk operations for multiple references

## AI Integration Strategy

### AI-Friendly Markdown Format

**What AI Sees**
```markdown
# Character Development

@Elara Mitchell is a 28-year-old historian who recently inherited 
@Thornfield Manor. Her analytical nature contrasts with the 
supernatural elements she encounters.

Key themes: @fantasy @gothic-horror @character-development

See also: @Chapter 1: The Inheritance
```

**What's Stored**
```markdown
::ref[Elara Mitchell]{#file-abc123 type="file" subtype="character"} is a 28-year-old 
historian who recently inherited ::ref[Thornfield Manor]{#file-def456 type="file" 
subtype="location"}. Her analytical nature contrasts with the supernatural 
elements she encounters.

Key themes: ::ref[fantasy]{#tag-ghi789 type="tag"} ::ref[gothic-horror]{#tag-jkl012 type="tag"} 
::ref[character-development]{#tag-mno345 type="tag"}

See also: ::ref[Chapter 1: The Inheritance]{#file-pqr678 type="file" subtype="chapter"}
```

### AI Context Resolution

**Reference Expansion for AI**
When sending content to AI, optionally expand references:
```markdown
# Character Development

Elara Mitchell [Character: Historian, age 28, protagonist] is a 28-year-old 
historian who recently inherited Thornfield Manor [Location: Gothic manor, 
central setting]. Her analytical nature contrasts with the supernatural 
elements she encounters.
```

**AI Generation with References**
AI can suggest references in natural format:
```
AI: "You might want to reference @the Shadow Lord here as the primary antagonist."
System: Converts to proper directive when user accepts suggestion
```

## Backend Integration

### References Management API

**Endpoints**
- `GET /api/references/{documentId}` - Get all references in document
- `POST /api/references` - Create new reference
- `PUT /api/references/{id}` - Update reference display text
- `DELETE /api/references/{id}` - Remove reference
- `GET /api/references/search?q={query}&type={type}` - Search entities

**Reference Validation**
- Verify target entity exists
- Update display text when entity renamed
- Mark orphaned references (target deleted)
- Provide reference health reports

### Sync Strategy

**Real-time Updates**
- WebSocket updates when entities renamed
- Auto-update reference display text
- Conflict resolution for concurrent edits
- Background reference integrity checks

**Bulk Operations**
- Batch reference updates on entity rename
- Efficient bulk reference creation/deletion
- Reference migration during entity moves
- Backup/restore reference relationships

## Migration & Implementation Phases

### Phase 1: Core Reference System
- Implement basic @-picker with file references
- Create directive format and storage
- Build reference picker UI component
- Basic backend references table

### Phase 2: Multi-Type Support
- Add tag references (@# trigger)
- Implement type-specific filtering
- Enhanced picker with category grouping
- Reference validation and health checking

### Phase 3: Advanced Features
- Reference preview and metadata
- Bulk reference operations
- AI context expansion
- Real-time collaborative reference updates

### Phase 4: Extended Entity Types
- Location, timeline, relationship references
- Custom entity type definitions
- Advanced AI integration patterns
- Reference analytics and insights

## Development Guidelines

### Code Organization
```
src/components/editor/references/
├── ReferencePlugin.ts           # Main MDXEditor plugin
├── ReferencePicker.tsx          # Autocomplete picker UI
├── ReferenceEditor.tsx          # Directive editor component
├── hooks/
│   ├── useEntitySearch.ts       # Entity search and filtering
│   ├── useReferenceSync.ts      # Backend sync management
│   └── useRecentReferences.ts   # Recent references tracking
├── utils/
│   ├── referenceFormat.ts       # Directive formatting utilities
│   ├── entityResolver.ts        # Entity ID → display name resolution
│   └── searchAlgorithm.ts       # Fuzzy search implementation
└── types/
    ├── reference.types.ts       # TypeScript interfaces
    └── entity.types.ts          # Entity type definitions
```

### Testing Strategy
- Unit tests for search algorithms
- Integration tests for picker component
- E2E tests for complete reference workflows
- Performance tests for large entity sets
- AI integration tests for context expansion

### Performance Considerations
- Entity search index for fast filtering
- Reference cache for frequently accessed entities
- Debounced search to avoid excessive API calls
- Virtual scrolling for large entity lists
- Lazy loading of entity metadata

---

**Next Steps**: Begin implementation with Phase 1 core reference system, starting with the MDXEditor plugin and basic file reference support.