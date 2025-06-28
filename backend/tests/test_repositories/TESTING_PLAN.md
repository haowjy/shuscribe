# 🧪 Repository Testing Plan for ShuScribe Article Snapshot Architecture

## Overview

This document outlines the comprehensive unit testing strategy for ShuScribe's new article snapshot architecture, focusing on testing the in-memory repository implementations with the Pokemon Amber test data.

## Test Structure

```
backend/tests/
├── conftest.py                    # Pytest configuration and fixtures
├── test_repositories/
│   ├── test_story_repository.py   # Story repository tests
│   ├── test_wiki_repository.py    # Wiki repository tests  
│   └── test_integration.py        # Integration tests
├── resources/
│   └── pokemon_amber/
│       └── story/                 # Pokemon Amber test data (17 chapters + metadata)
└── TESTING_PLAN.md               # This document
```

## 🎯 Test Coverage Goals

### 1. Story Repository Tests (`test_story_repository.py`)

**Core CRUD Operations:**
- ✅ `test_create_story()` - Story creation with proper owner assignment  
- ✅ `test_get_story_existing()` - Retrieve existing stories
- ✅ `test_get_story_nonexistent()` - Return empty story for non-existent IDs
- ✅ `test_update_story()` - Update story status and metadata
- ✅ `test_delete_story()` - Story deletion with verification
- ✅ `test_get_stories_by_owner()` - Filter stories by owner

**Chapter Operations:**
- ✅ `test_create_chapter()` - Chapter creation with story association
- ✅ `test_get_chapters_for_story()` - Retrieve chapters sorted by number
- ✅ `test_get_chapters_basic()` - Basic chapter retrieval functionality

**Story Arc Operations:**
- ✅ `test_create_story_arc()` - Arc creation with chapter ranges
- ✅ `test_get_story_arcs()` - Retrieve arcs sorted by start chapter
- ✅ `test_update_story_arc()` - Update arc processing status

**Enhanced Chapter Operations:**
- ✅ `test_create_enhanced_chapter()` - Enhanced chapters with wiki links
- ✅ `test_get_enhanced_chapters_by_story()` - Filter by story
- ✅ `test_get_enhanced_chapters_by_arc()` - Filter by arc

### 2. Wiki Repository Tests (`test_wiki_repository.py`)

**Wiki Page Operations:**
- ✅ `test_create_wiki_page()` - Wiki page creation with safety settings
- ✅ `test_get_wiki_page_existing()` - Retrieve existing wiki pages  
- ✅ `test_get_wiki_page_nonexistent()` - Return empty wiki for non-existent IDs
- ✅ `test_update_wiki_page()` - Update safety levels and metadata
- ✅ `test_delete_wiki_page()` - Wiki page deletion

**Base Article Operations:**
- ✅ `test_create_article()` - Create conceptual articles (characters, locations)
- ✅ `test_get_article_existing()` - Retrieve existing articles
- ✅ `test_update_article()` - Update article metadata and tags

**Article Snapshot Operations (Core Innovation):**
- ✅ `test_create_article_snapshot()` - Create versioned content snapshots
- ✅ `test_article_snapshot_versioning()` - Test parent-child snapshot chains
- ✅ Progressive safety levels (chapter 1 → 2 → 3 content evolution)
- ✅ Cross-story snapshots (same article, different story contexts)

**Article-Story Associations:**
- ✅ `test_create_article_story_association()` - Backlinking articles to stories
- ✅ Article importance levels and relationship types
- ✅ First mention tracking for spoiler prevention

**Wiki Page-Article Linking:**  
- ✅ `test_create_wiki_page_article_link()` - Link pages to specific snapshots
- ✅ Display order and featured article management
- ✅ Multiple snapshots per wiki page with proper ordering

### 3. Integration Tests (`test_integration.py`) 

**StoryWorkspace Integration:**
- ✅ `test_load_pokemon_amber_story()` - Load real test data (17 chapters)
- ✅ `test_workspace_chapter_range()` - Test lazy loading and chunk access
- ✅ Verify metadata parsing (title, author, genres, tags)
- ✅ Chapter title and content validation

**Repository Integration:**
- ✅ `test_create_story_with_wiki()` - End-to-end story + wiki creation
- ✅ `test_article_snapshot_workflow()` - Complete snapshot lifecycle
- ✅ `test_spoiler_safety_filtering()` - Verify safety level enforcement

**Complete Article Snapshot Workflow Test:**
```
Story: "Pokemon Adventures" (3 chapters)
├── Chapter 1: "Meeting Pikachu" 
├── Chapter 2: "First Battle"
└── Chapter 3: "New Powers"

Article: "Pikachu" (CHARACTER type)
├── Snapshot v1: Basic info (safe through ch.1)
├── Snapshot v2: Shows loyalty (safe through ch.2) 
└── Snapshot v3: Full development (safe through ch.3)

Wiki Page: Links to latest snapshot (v3)
Association: Pikachu ↔ Pokemon Adventures (importance: 10, protagonist)
```

## 🔧 Test Fixtures & Data

**Core Fixtures (`conftest.py`):**
- `test_user_id()` - Standard UUID for test ownership
- `story_repo()` - Fresh InMemoryStoryRepository instance
- `wiki_repo()` - Fresh InMemoryWikiPageRepository instance  
- `pokemon_story_path()` - Path to Pokemon Amber test data
- `sample_story()` - Pre-created test story
- `sample_wiki_page()` - Pre-created test wiki page
- `sample_article()` - Pre-created test article

**Test Data Sources:**
- **Pokemon Amber Story**: 17 chapters, complete metadata, real content
- **Synthetic Data**: Generated test stories for specific scenarios
- **Edge Cases**: Empty content, missing references, boundary conditions

## 🎨 Key Testing Scenarios

### Scenario 1: Progressive Article Development
```python
# Character starts unknown, develops through story
v1: "Mystery character appears" (safe: ch.1)
v2: "Character shows heroic traits" (safe: ch.3) 
v3: "SPOILER: Character is the chosen one" (safe: ch.5)
```

### Scenario 2: Cross-Story Article Sharing
```python
# Same character appears in multiple stories/universes
Article: "Pikachu"
├── Pokemon Adventures Snapshot: "Ash's loyal partner"
├── Pokemon Mystery Snapshot: "Wild electric pokemon" 
└── Pokemon Legends Snapshot: "Ancient guardian spirit"
```

### Scenario 3: Spoiler Safety Validation
```python
# Different wiki pages show appropriate content
Safe Wiki (ch.1-2): Shows basic character info only
Spoiler Wiki (ch.1-5): Shows full character development + major reveals
```

### Scenario 4: Version Chain Integrity
```python
# Snapshots form proper parent-child chains
v1 ← v2 ← v3 ← v4
└── Audit trail of how understanding evolved
```

## 🚀 Running the Tests

### Prerequisites
```bash
cd backend
pip install pytest pytest-asyncio
```

### Test Execution
```bash
# Run all repository tests
python -m pytest tests/test_repositories/ -v

# Run specific test categories
python -m pytest tests/test_repositories/test_story_repository.py -v
python -m pytest tests/test_repositories/test_wiki_repository.py -v  
python -m pytest tests/test_repositories/test_integration.py -v

# Run with coverage
python -m pytest tests/test_repositories/ --cov=src/database/repositories --cov-report=html
```

### Expected Output
```
🧪 Testing Story Repository...
✅ Created story: Test Story (ID: uuid...)
✅ Created chapter 1: Chapter 1
✅ Created chapter 2: Chapter 2  
✅ Retrieved 2 chapters
✅ Found 1 stories for user

🧪 Testing Wiki Repository...
✅ Created wiki page: Test Wiki (ID: uuid...)
✅ Created article: Test Character (ID: uuid...)
✅ Created article snapshot (ID: uuid...)
✅ Retrieved 1 snapshots for article

🧪 Testing Article Snapshot Workflow...
✅ Created snapshot v1 (safe through chapter 1)
✅ Created snapshot v2 (safe through chapter 2)
✅ Created snapshot v3 (safe through chapter 3)
✅ Retrieved 3 total snapshots
   v1: Safe through ch.1 - Pikachu is an Electric-type Pokemon.
   v2: Safe through ch.2 - Pikachu is an Electric-type Pokemon. Shows loyalty...
   v3: Safe through ch.3 - Pikachu is an Electric-type Pokemon. Loyal partner...
✅ Created story-article association
🎉 Article snapshot workflow test completed successfully!
```

## 📊 Architecture Validation Goals

### Repository Pattern Compliance
- ✅ Abstract interfaces properly implemented
- ✅ Factory functions work correctly (`get_story_repository()`, `get_wikipage_repository()`)
- ✅ In-memory implementations satisfy all contracts
- ✅ "Always return valid objects" pattern enforced

### Article Snapshot Architecture Benefits
- ✅ **Immutable Snapshots**: Never modify existing content → no spoiler leakage
- ✅ **Cross-Story Sharing**: Same article, different story contexts  
- ✅ **Granular Safety**: Chapter-based filtering prevents spoilers
- ✅ **Audit Trail**: Complete version history of article evolution
- ✅ **Performance**: Lazy loading + efficient indexing

### Schema Integration  
- ✅ Story schemas work seamlessly with Wiki schemas
- ✅ UUID consistency across all entities
- ✅ Timestamp tracking for all operations
- ✅ Proper foreign key relationships maintained

## 🔮 Future Enhancements

### Test Expansion
- **Performance Tests**: Large dataset handling (1000+ chapters, 10000+ snapshots)
- **Concurrent Access**: Multi-user scenario testing  
- **Data Migration**: Schema version upgrade testing
- **Error Handling**: Network failures, data corruption recovery

### Supabase Repository Tests  
- **Database Integration**: Real PostgreSQL testing
- **Transaction Handling**: ACID compliance validation
- **Query Optimization**: Performance benchmarking
- **Connection Pooling**: Resource management testing

### API Layer Tests
- **FastAPI Integration**: Repository → Service → API testing
- **Authentication**: User permission enforcement
- **Rate Limiting**: API usage pattern testing  
- **WebSocket**: Real-time updates for wiki changes

## 📝 Test Development Notes

### Known Issues
- Some repository methods may return `None` instead of empty objects (needs fixing)
- `StoryWorkspace` integration needs method signature verification
- Async fixture handling requires proper `await` usage

### Best Practices
- Always use fresh repository instances per test (prevent data bleed)
- Test both happy path and edge cases
- Verify complete object graphs (snapshots → articles → stories)  
- Use realistic test data (Pokemon Amber) alongside synthetic data
- Assert intermediate states, not just final outcomes

### Repository-Specific Patterns
```python
# Story Repository: Focus on hierarchical data (story → arc → chapter)
story = await repo.create_story(StoryCreate(...))
chapter = await repo.create_chapter(ChapterCreate(story_id=story.id, ...))

# Wiki Repository: Focus on versioned relationships  
article = await repo.create_article(ArticleCreate(...))
snapshot = await repo.create_article_snapshot(ArticleSnapshotCreate(article_id=article.id, ...))
link = await repo.create_wiki_page_article_link(WikiPageArticleLinkCreate(...))
```

---

**This testing plan ensures comprehensive validation of ShuScribe's innovative article snapshot architecture, providing confidence that the repository layer correctly implements our spoiler-safe, cross-story wiki system.** 