# ShuScribe Storage Architecture v3.0 (Simplified)

## Overview

ShuScribe implements a **workspace-centric storage architecture** with **domain-specific repositories** that supports both file-based local development and Supabase-backed web deployment. The system is built around **workspaces** containing **content** with **chapter-based versioning** for spoiler prevention and **user-guided content evolution**.

## Repository Domains

The storage architecture is organized around five core domains:

1. **`user`** - User profiles, authentication, BYOK API keys
2. **`workspace`** - Workspace management, arcs, processing state  
3. **`story`** - All story content: published chapters, drafts, chapter versions, story metadata
4. **`wiki`** - AI-generated articles with versioning, connections, spoiler protection
5. **`writing`** - Author workspace tools: AI conversations, research notes, outlines, writing prompts, planning tools

This domain separation eliminates circular imports and provides clear boundaries for implementation backends (memory, file, supabase).

## Core Concepts

### 1. Workspace
A **workspace** is the top-level container for a complete story project. Each workspace contains all content, metadata, and generated artifacts for a single story.

### 2. Content Types
All content is classified by type using standardized enums:

```python
class ContentType(Enum):
    STORY_CHAPTER = "story_chapter"
    WIKI_ARTICLE = "wiki_article"
    CHARACTER_PROFILE = "character_profile"
    LOCATION_GUIDE = "location_guide"
    TIMELINE_ENTRY = "timeline_entry"
    CONCEPT_ARTICLE = "concept_article"
    USER_NOTES = "user_notes"
    OTHER = "other"
    USER_DEFINED = "user_defined"
```

### 3. Chapter-Based Versioning
Two orthogonal versioning systems:

- **Chapter-Safe Versioning**: Article content evolves as story progresses, with versions safe through specific chapters (spoiler prevention)
- **Edit Versioning**: Track author changes to any chapter-safe version (content history)

### 4. Living Current Version
Each article maintains a "current working version" that incorporates user notes and guidance for future AI generation.

## Simplified Workspace Structure

```
workspace_name/
├── content/           # All user-visible content
│   ├── story/         # Story chapters
│   ├── wiki/          # Wiki articles (current versions)
│   └── notes/         # User notes and research
└── _system/           # System data
    ├── versions/      # Chapter-safe versions and edit history
    ├── connections/   # Article relationships
    ├── processing/    # Arc processing state
    └── metadata/      # Workspace metadata
```

## Content Versioning System

### Chapter-Safe Versions (Spoiler Prevention)

```python
@dataclass
class ChapterVersion:
    """Version of content safe through specific chapter"""
    article_id: str
    content_type: ContentType
    chapter: int                # Safe through this chapter
    content: str               # Full content (no diffs)
    created_at: datetime
    created_by: str           # "arc_processing" or "user_edit"
    edit_version: int = 1     # Latest edit version number

@dataclass
class CurrentVersion:
    """Living working version with user guidance"""
    article_id: str
    content_type: ContentType
    content: str
    user_notes: List[str]                    # User corrections/additions
    next_update_guidance: str                # Guidance for next AI generation
    last_updated: datetime
    last_updated_by: str
```

### Edit Versions (Content History)

```python
@dataclass
class EditVersion:
    """Author edit of a specific chapter-safe version"""
    article_id: str
    chapter: int              # Which chapter version this edits
    edit_number: int          # 1, 2, 3...
    content: str             # Full edited content
    edit_summary: str        # "Fixed typo", "Added backstory"
    created_at: datetime
    created_by: str          # Author ID
```

## Wikigen Pipeline Integration

### Arc Processing Creates Chapter Versions

```python
def process_arc(self, arc: Arc):
    """Process arc and create chapter-level versions"""
    
    # 1. Generate content for whole arc using current versions + user notes
    arc_articles = {}
    for article_id in self.get_affected_articles(arc):
        current = self.get_current_version(article_id)
        user_guidance = current.user_notes + current.next_update_guidance
        
        updated_content = self.ai_generate_article_update(
            arc_content=arc.content,
            existing_content=current.content,
            user_guidance=user_guidance
        )
        
        arc_articles[article_id] = updated_content
    
    # 2. Create chapter-safe versions for each chapter in arc
    for chapter_num in range(arc.start_chapter, arc.end_chapter + 1):
        for article_id, article_content in arc_articles.items():
            
            # Filter content to be safe through this chapter
            chapter_safe_content = self.filter_content_for_chapter(
                article_content, chapter_num
            )
            
            # Store chapter version
            self.save_chapter_version(
                article_id=article_id,
                chapter=chapter_num,
                content=chapter_safe_content,
                created_by=f"arc_{arc.id}_processing"
            )
    
    # 3. Update current versions for next arc
    for article_id, updated_content in arc_articles.items():
        self.update_current_version(article_id, updated_content)
```

### Reader Experience

```python
def get_article_for_reader(self, article_id: str, reader_chapter: int) -> Optional[str]:
    """Get article version safe for reader's progress"""
    
    # Get latest chapter version safe for this reader
    version = db.query("""
        SELECT content FROM chapter_versions 
        WHERE article_id = ? AND chapter <= ? 
        ORDER BY chapter DESC 
        LIMIT 1
    """, article_id, reader_chapter)
    
    return version.content if version else None
```

## User Editing System

### Types of User Edits

```python
class EditType(Enum):
    CORRECT_CHAPTER_VERSION = "correct_chapter_version"  # Fix specific chapter version
    UPDATE_CURRENT_VERSION = "update_current_version"    # Edit current working version
    ADD_USER_NOTES = "add_user_notes"                    # Add guidance for AI
    SET_UPDATE_GUIDANCE = "set_update_guidance"          # Set next update instructions

def handle_user_edit(self, article_id: str, edit_type: EditType, content: str, chapter: int = None):
    """Handle different types of user edits"""
    
    if edit_type == EditType.CORRECT_CHAPTER_VERSION:
        # Create new edit version of specific chapter version
        self.create_edit_version(
            article_id=article_id,
            chapter=chapter,
            content=content,
            edit_summary="User correction"
        )
        
        # Queue for correction propagation
        self.queue_correction_propagation(article_id, chapter, content)
        
    elif edit_type == EditType.UPDATE_CURRENT_VERSION:
        # Update current working version directly
        self.update_current_version(article_id, content)
        
    elif edit_type == EditType.ADD_USER_NOTES:
        # Add user guidance
        current = self.get_current_version(article_id)
        current.user_notes.append(content)
        self.save_current_version(current)
```

### Correction Propagation Agent

```python
class CorrectionPropagationAgent:
    """Intelligently propagates user corrections to current version"""
    
    async def propagate_correction(self, article_id: str, corrected_chapter: int, correction: str):
        """Apply correction to current version and future chapter versions"""
        
        current = self.get_current_version(article_id)
        corrected_version = self.get_chapter_version(article_id, corrected_chapter)
        
        # Use AI to intelligently merge correction
        propagated_content = await self.ai_merge_correction(
            current_content=current.content,
            correction=correction,
            correction_context=corrected_version.content
        )
        
        # Update current version
        current.content = propagated_content
        current.user_notes.append(f"Auto-propagated correction from chapter {corrected_chapter}")
        self.save_current_version(current)
        
        # Mark for regeneration in next arc processing
        self.mark_for_regeneration(article_id, reason="user_correction_propagated")
```

## Storage Implementation

### Database Schema (Domain-Organized)

```sql
-- User Domain
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    subscription_tier VARCHAR DEFAULT 'free_byok', -- 'local', 'free_byok', 'premium', 'enterprise'
    display_name VARCHAR,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_api_keys (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR NOT NULL,
    encrypted_api_key TEXT NOT NULL,
    provider_metadata JSONB DEFAULT '{}',
    validation_status VARCHAR DEFAULT 'pending',
    last_validated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, provider)
);

-- Workspace Domain
CREATE TABLE workspaces (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR DEFAULT 'active',
    last_processed_chapter INTEGER DEFAULT 0,
    processing_state JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE arcs (
    id UUID PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    start_chapter INTEGER NOT NULL,
    end_chapter INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Story Domain
CREATE TABLE chapters (
    id UUID PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    chapter_number INTEGER NOT NULL,
    title VARCHAR NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR DEFAULT 'draft', -- draft, published, archived
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    UNIQUE(workspace_id, chapter_number)
);

CREATE TABLE story_metadata (
    workspace_id UUID PRIMARY KEY REFERENCES workspaces(id) ON DELETE CASCADE,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    synopsis TEXT DEFAULT '',
    genres JSONB DEFAULT '[]',
    tags JSONB DEFAULT '[]',
    total_chapters INTEGER DEFAULT 0,
    published_chapters INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Wiki Domain
CREATE TABLE wiki_chapter_versions (
    id UUID PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    article_id VARCHAR NOT NULL,
    article_type VARCHAR NOT NULL,
    chapter INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR NOT NULL,
    edit_version INTEGER DEFAULT 1,
    UNIQUE(workspace_id, article_id, chapter)
);

CREATE TABLE wiki_current_versions (
    id UUID PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    article_id VARCHAR NOT NULL,
    article_type VARCHAR NOT NULL,
    content TEXT NOT NULL,
    user_notes JSONB DEFAULT '[]',
    next_update_guidance TEXT DEFAULT '',
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    last_updated_by VARCHAR NOT NULL,
    UNIQUE(workspace_id, article_id)
);

CREATE TABLE wiki_connections (
    id UUID PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    source_article_id VARCHAR NOT NULL,
    target_article_id VARCHAR NOT NULL,
    connection_type VARCHAR NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Writing Domain
CREATE TABLE ai_conversations (
    id UUID PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    conversation_type VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    messages JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE author_notes (
    id UUID PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    title VARCHAR NOT NULL,
    content TEXT NOT NULL,
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE writing_prompts (
    id UUID PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    title VARCHAR NOT NULL,
    template TEXT NOT NULL,
    variables JSONB DEFAULT '{}',
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### File-Based Storage (Desktop-Optimized)

```
my-story-project/                    # Workspace root
├── .shuscribe/                      # System directory (hidden)
│   ├── config.json                  # User config + API keys (encrypted)
│   ├── workspace.json               # Workspace metadata
│   ├── processing.json              # Arc processing state
│   └── connections.json             # Wiki article connections
├── story/                           # Story content
│   ├── metadata.json                # Story metadata  
│   ├── chapters/                    # Published chapters
│   │   ├── 01-beginning.md
│   │   ├── 02-discovery.md
│   │   └── ...
│   └── drafts/                      # Draft chapters
│       ├── 03-draft.md
│       └── outline.md
├── wiki/                            # Current wiki articles (user-visible)
│   ├── characters/
│   │   ├── protagonist.md
│   │   ├── dr-aris.md
│   │   └── general-kaelen.md
│   ├── locations/
│   │   ├── capital-city.md
│   │   └── research-facility.md
│   └── concepts/
│       ├── temporal-mechanics.md
│       └── the-resonator.md
├── wiki-versions/                   # Chapter-specific versions (spoiler prevention)
│   ├── characters/
│   │   ├── protagonist/
│   │   │   ├── ch01.md
│   │   │   ├── ch03.md
│   │   │   └── ch05.md
│   │   └── dr-aris/
│   │       ├── ch02.md
│   │       ├── ch04.md
│   │       └── ch06.md
│   └── locations/
│       └── capital-city/
│           ├── ch01.md
│           └── ch04.md
├── notes/                           # Author notes and research
│   ├── character-development.md
│   ├── world-building.md
│   └── plot-outline.md
└── conversations/                   # AI conversation history
    ├── character-chat-2024-01.json
    ├── plotting-session-2024-01.json
    └── worldbuilding-2024-01.json
```

### Key Benefits of Desktop-Optimized Structure

1. **User-Friendly Organization**: Content is organized in intuitive directories (`story/`, `wiki/`, `notes/`) that make sense for local file browsing
2. **Hidden System Files**: All implementation details are kept in `.shuscribe/` directory, maintaining a clean user experience
3. **Flatter Hierarchy**: Reduces nesting complexity while maintaining all core functionality
4. **Spoiler Prevention**: `wiki-versions/` directory maintains chapter-based versioning for spoiler-safe content
5. **Same Repository Interfaces**: File structure is an implementation detail - all repository interfaces remain unchanged

### File Content Examples

#### Chapter-Specific Version (Spoiler Prevention)
```markdown
<!-- wiki-versions/characters/dr-aris/ch03.md -->
---
article_id: "characters/dr-aris"
chapter: 3
created_at: "2024-01-01T00:00:00Z"
created_by: "arc_1_processing"
content_type: "character_profile"
---

# Dr. Aris

Dr. Aris is a mysterious scientist who first appears in Chapter 1. He works at the Temporal Research Institute and seems to be observing the protagonist's activities.

## Background
- First appearance: Chapter 1
- Occupation: Temporal research scientist
- Current status: Active observer

## Related Articles
- [[Temporal Research Institute]]
- [[The Protagonist]]
```

#### Current Working Version (User-Visible)
```markdown
<!-- wiki/characters/dr-aris.md -->
---
article_id: "characters/dr-aris"
last_updated: "2024-01-20T10:30:00Z"
last_updated_by: "author_123"
user_notes:
  - "User correction: He worked at Temporal Institute, not Physics Lab"
  - "User addition: Should mention his daughter Sarah in next update"
  - "User preference: Focus more on his relationship with protagonist"
next_update_guidance: "Incorporate relationship dynamics and family connections when processing arc 3. Emphasize the father-figure aspect and his protective instincts."
---

# Dr. Aris

Dr. Aris is a former government researcher who was fired from the Temporal Research Institute for conducting unauthorized experiments on temporal mechanics. He has a complex relationship with the protagonist and harbors secret motivations.

## Background
- Former employee of the Temporal Research Institute
- Specializes in quantum chronodynamics  
- Has a hidden agenda involving the protagonist
- Father figure with complicated past

## Appearances
- Chapter 1: First appearance as mysterious observer
- Chapter 3: Revealed as former government scientist
- Chapter 5: Backstory revealed through flashbacks
- Chapter 7: Confrontation with protagonist

## Related Articles
- [[Temporal Research Institute]]
- [[Quantum Chronodynamics]]
- [[The Protagonist]]
```

#### Local Configuration File
```json
// .shuscribe/config.json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "workspace_name": "My Story Project",
  "display_name": "Local Author",
  "email": "author@example.com",
  "subscription_tier": "local",
  "api_keys": {
    "openai": {
      "encrypted_key": "gAAAAABh...",
      "provider_metadata": {
        "model": "gpt-4",
        "max_tokens": 4000
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  },
  "preferences": {
    "default_provider": "openai",
    "encrypt_keys": true
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Core APIs (High-Level)

### Domain Manager APIs

Each domain provides focused management interfaces:

- **`UserManager`** - User CRUD, BYOK API key management with validation
- **`WorkspaceManager`** - Workspace lifecycle, arc processing, user ownership
- **`StoryManager`** - Chapter management, draft/publish workflow, story metadata
- **`WikiManager`** - Article versioning, spoiler prevention, connection management
- **`WritingManager`** - AI conversation tracking, note organization, prompt management

### Core Operations

**Spoiler-Safe Reading**:
- `get_article_for_reader(article_id, max_chapter)` - Returns content safe through reader's progress
- `get_published_chapters(workspace_id, max_chapter)` - Returns story content for reader

**Content Evolution**:
- `process_arc(workspace_id, arc)` - Generate chapter-safe versions for arc range
- `update_current_version(article_id, content, user_notes)` - Update working version with guidance
- `propagate_correction(article_id, chapter, correction)` - Intelligent correction propagation

**User-Guided AI**:
- `add_user_notes(article_id, notes)` - Add guidance for future AI generation
- `create_conversation(workspace_id, type, title)` - Start AI conversation session
- `validate_api_key(user_id, provider)` - BYOK key validation and storage

## Benefits of Simplified Architecture

### User Experience
- **Perfect spoiler prevention**: Chapter-granular content filtering
- **User-guided evolution**: Authors can correct and guide AI generation
- **Simple editing**: Clear distinction between current and historical versions
- **Intuitive versioning**: "I'm on chapter 5" → get chapter 5 safe content

### Developer Experience
- **Simple storage**: Full content per version, no complex diff application
- **Easy queries**: Single SELECT with simple WHERE clause
- **Clear data model**: Only 4 main tables instead of 7+ repositories
- **Testable**: Easy to create test workspaces and verify behavior

### System Architecture
- **Scalable**: Chapter-based versions scale linearly with story length
- **Maintainable**: Minimal complexity, clear separation of concerns
- **Flexible**: Easy to add new content types via enum
- **Storage efficient**: ~300MB for 300-chapter, 200-article story (~$0.02/month)

## Migration Strategy

### Phase 1: Core Infrastructure
1. **Workspace Manager**: Create/manage workspaces
2. **Content Manager**: Store/retrieve content with versioning
3. **Chapter Versioning**: Implement chapter-safe version storage
4. **Basic Reader Experience**: Get spoiler-safe content

### Phase 2: Wikigen Integration
1. **Arc Processing**: Integrate with existing wikigen pipeline
2. **Chapter Version Creation**: Generate chapter-safe versions during arc processing
3. **Current Version Management**: Maintain living current versions

### Phase 3: User Editing
1. **Edit Interfaces**: Allow user corrections and guidance
2. **Correction Propagation**: Agent to merge corrections intelligently
3. **User Notes System**: Capture user guidance for AI generation

### Phase 4: Advanced Features
1. **Incremental Chapter Processing**: Add chapters one-by-one after initial arcs
2. **Advanced Connections**: Rich relationship modeling between content
3. **Collaboration Features**: Multi-user editing and review

This simplified architecture provides the same core functionality with 80% less complexity while maintaining all the essential features for spoiler prevention and user-guided content evolution.