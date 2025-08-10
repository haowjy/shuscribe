# System Architecture

**ShuScribe Universe Content Management Platform**

## Architecture Overview

ShuScribe is a **frontend-centric** platform with hierarchical project organization, rich document management, and AI-powered features for fantasy writers.

```
┌─────────────────────────────────────────────────────────┐
│                SYSTEM ARCHITECTURE                     │
├─────────────────────────────────────────────────────────┤
│  🎯 PROJECT LAYER                                      │
│  Project Container → File Tree → Documents             │
│                                                         │
│  📝 CONTENT LAYER                                      │
│  ProseMirror Documents → Word Tracking → @-References  │
│                                                         │
│  🏷️ ORGANIZATION LAYER                                 │
│  Many-to-Many Tags → Categories → Search               │
│                                                         │
│  🤖 AI LAYER                                           │
│  LLM Integration → WikiGen → Context-Aware Assistance  │
│                                                         │
│  💾 DATA LAYER                                         │
│  PostgreSQL → Repository Pattern → Multi-Backend       │
└─────────────────────────────────────────────────────────┘
```

## Core Data Models

### Project
```python
class Project:
    id: UUID
    name: str           # "The Chronicles of Eldoria"
    description: str    # Project overview
    user_id: UUID       # Owner
    settings: dict      # Project configuration
    created_at: datetime
```

### File Tree Item
```python
class FileTreeItem:
    id: UUID
    project_id: UUID
    name: str           # "Aria_Stormwind" 
    type: str          # "file" | "folder"
    path: str          # "/characters/protagonists/aria_stormwind"
    parent_id: UUID    # Optional parent folder
    document_id: UUID  # Optional linked document
    icon: str          # UI icon reference
    word_count: int    # Auto-calculated
```

### Document
```python
class Document:
    id: UUID
    project_id: UUID
    title: str         # "Aria Stormwind"
    content: dict      # ProseMirror JSON
    word_count: int    # Auto-calculated
    version: int       # Version tracking
    tags: List[Tag]    # Many-to-many relationship
    created_at: datetime
    updated_at: datetime
```

### Tag
```python
class Tag:
    id: UUID
    project_id: UUID
    name: str          # "fire-magic"
    category: str      # "magic-system"
    color: str         # "#ff6b6b"
    icon: str          # "flame"
    usage_count: int   # Track popularity
```

## Key Features

### Hierarchical Organization
- **Path-Based Creation**: Documents automatically create folder hierarchy
- **File Tree Navigation**: VS Code-like project explorer
- **Parent-Child Relationships**: Proper folder structure

### Rich Content Support
- **ProseMirror JSON**: Rich text with formatting, headings, lists
- **@-Reference System**: Cross-document linking (frontend implementation)
- **Version Control**: Document versioning and change tracking
- **Auto Word Count**: Automatic word count calculation

### Tag System
- **Many-to-Many**: Documents can have multiple tags, tags apply to multiple documents
- **Categorized**: Organize tags by type (character-traits, magic-systems, locations)
- **Visual**: Colors and icons for easy recognition
- **Analytics**: Track tag usage and popularity

### AI Integration
- **Portkey Gateway**: Self-hosted LLM gateway supporting multiple providers
- **WikiGen Agent**: AI-powered wiki generation for worldbuilding
- **Context-Aware**: AI understands project structure and relationships
- **Spoiler Prevention**: AI avoids revealing future plot points

## Technology Stack

### Frontend
- **Next.js 15** with App Router
- **React 19** with TypeScript
- **TanStack Query** for state management
- **shadcn/ui** component library
- **Tailwind CSS v4** for styling

### Backend
- **FastAPI** with async support
- **SQLAlchemy ORM** with relationships
- **Repository Pattern** for clean architecture
- **Pydantic** for validation and serialization
- **Supabase** PostgreSQL with auth

### Development
- **Frontend-First Design**: API matches TypeScript interfaces
- **Offline-First**: LocalStorage + TanStack Query
- **API Consistency**: `ApiResponse<T>` wrapper for all responses
- **Field Naming**: Backend handles both camelCase and snake_case

## Integration Patterns

### Frontend ↔ Backend
1. **Frontend defines API contract** in `src/types/api.ts`
2. **Backend implements matching endpoints** with field aliases
3. **Consistent response format** using `ApiResponse<T>` wrapper
4. **Authentication** via Supabase JWT tokens

### Development Workflow
1. **Design UI/UX** in frontend with mock data
2. **Define TypeScript interfaces** for expected API responses
3. **Backend implements endpoints** matching frontend expectations
4. **Integration testing** ensures consistency

## Deployment Architecture

### Production
- **Frontend**: Vercel with Next.js
- **Backend**: Railway with FastAPI
- **Database**: Supabase PostgreSQL
- **AI**: Self-hosted Portkey Gateway

### Development
- **Frontend**: Local Next.js dev server
- **Backend**: Local FastAPI with hot reload
- **Database**: Local PostgreSQL via Docker
- **AI**: Local Portkey Gateway

The architecture prioritizes developer experience, user experience, and scalability while maintaining clean separation of concerns and consistent data flow.