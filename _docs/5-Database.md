# Database Storage and Relationships

### 1. Design Philosophy

ShuScribe employs a **flexible data storage architecture** that supports both persistent database storage and in-memory storage, depending on the deployment mode. The design is built around a repository pattern that abstracts the underlying storage mechanism while maintaining data integrity and consistency.

The architecture is designed to support:

*   **Multi-tenancy:** Cleanly separating data for different users and stories (web deployment).
*   **Hybrid API Key Model (BYOK):** Securely storing user-provided API keys in persistent storage (web) or managing them in-memory (local).
*   **Content Versioning:** Storing raw chapter content allows for easy reprocessing.
*   **Structured Wiki Data:** Modeling the wiki as a collection of versioned article snapshots.
*   **Spoiler Prevention:** Chapter-based article versioning prevents spoilers without user progress tracking.
*   **Local Development:** Supporting immediate local usage without requiring database setup.
*   **Shared Universe Support:** Articles can be referenced across multiple stories with story-specific versions.

### 2. Dual Storage Architecture

#### 2.1 Web Deployment: Supabase Backend

For web deployment, ShuScribe uses **Supabase** as the backend-as-a-service provider, offering:
- **PostgreSQL Database:** Fully managed PostgreSQL with real-time capabilities
- **Authentication:** Built-in user management and JWT-based authentication
- **Real-time Subscriptions:** Live updates for collaborative features (future)
- **API Layer:** Auto-generated REST and GraphQL APIs
- **Security:** Row-level security policies and encrypted connections

#### 2.2 Local Deployment: In-Memory Storage

For local/CLI usage, ShuScribe uses **in-memory repositories** that:
- **Store data in Python dictionaries:** Fast access with minimal overhead
- **Maintain referential integrity:** Proper relationship management in memory
- **Support export/import:** Optional persistence to local files
- **Enable rapid development:** No database setup required for testing

### 3. Repository Pattern Implementation

The system uses abstract repository interfaces that can be implemented by different storage backends:

```python
# Abstract interface
class AbstractUserRepository(ABC):
    async def get(self, id: UUID) -> Optional[User]
    async def create(self, obj_in: dict) -> User
    # ... other methods

# Supabase implementation  
class SupabaseUserRepository(AbstractUserRepository):
    def __init__(self, supabase_client: Client)
    # Implementation using Supabase client

# In-memory implementation
class InMemoryUserRepository(AbstractUserRepository):
    def __init__(self):
        self._users: Dict[UUID, User] = {}
    # Implementation using Python dictionaries
```

The factory function automatically selects the appropriate repository based on configuration:

```python
def get_user_repository(supabase_client=None) -> AbstractUserRepository:
    if settings.SKIP_DATABASE:
        return InMemoryUserRepository()  # Singleton for local mode
    else:
        return SupabaseUserRepository(supabase_client)
```

### 4. Core Schema (Supabase/Web Mode)

This schema applies to the Supabase deployment and reflects the current database structure:

```
┌──────────────┐      ┌────────────────┐      ┌──────────┐      ┌───────────┐
│    users     │◀────┬│ user_api_keys  │      │ stories  │◀────┬│ chapters  │
└──────────────┘    │ └────────────────┘      └─────┬────┘     │└─────┬─────┘
      ▲             │                               │          │      │
      │             │                               ▼          │      ▼
      │             │                      ┌─────────────┐     │ ┌─────────────────┐
      │             │                      │ story_arcs  │◀────┘ │enhanced_chapters│
      │             │                      └─────────────┘       └─────────────────┘
      │             │                               │
      │             │                               ▼
      │             │                      ┌─────────────┐      ┌─────────────────┐
      │             │                      │ wiki_pages  │      │    articles     │
      │             │                      └──────┬──────┘      └─────┬───────────┘
      │             │                             │                   │
      │             │                             ▼                   ▼
      │             │                   ┌───────────────────┐ ┌──────────────────┐
      └─────────────┼───────────────────│ wiki_page_article │ │ article_snapshots│
                    │                   │      _links       │ └─────┬────────────┘
                    │                   └───────────────────┘       │
                    │                             ▲                 │
                    │                             └─────────────────┘
                    │
                    ▼
           ┌─────────────────────┐
           │ article_story_assoc │
           └─────────────────────┘
```

---

### 5. Table Specifications (Supabase Schema)

#### 5.1. `users`
Managed primarily by Supabase Auth, with additional application-specific fields.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | **Primary Key.** References `auth.users.id` (Supabase Auth). |
| `email` | `TEXT` | User's email address (synced with Supabase Auth). |
| `subscription_tier` | `TEXT` | User's plan (`free_byok`, `premium`). Defaults to `free_byok`. |
| `created_at` | `TIMESTAMPTZ` | Timestamp of user creation. |
| `updated_at` | `TIMESTAMPTZ` | Timestamp of last profile update. |

#### 5.2. `user_api_keys`
Securely stores encrypted API keys provided by users.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `user_id` | `UUID` | **Foreign Key** to `users.id`. |
| `provider` | `TEXT` | The LLM provider for the key (e.g., `openai`, `anthropic`). |
| `encrypted_api_key` | `TEXT` | The user's LLM API key, **encrypted at rest** using Fernet encryption. |
| `provider_metadata` | `JSONB` | Additional provider-specific configuration. |
| `validation_status` | `TEXT` | Key validation status (`pending`, `valid`, `invalid`). |
| `last_validated_at` | `TIMESTAMPTZ` | Timestamp of last key validation. |
| `created_at` | `TIMESTAMPTZ` | Timestamp of key creation. |
| `updated_at` | `TIMESTAMPTZ` | Timestamp of the last key update. |

**Note:** Primary key is composite (`user_id`, `provider`) to allow multiple keys per user.

#### 5.3. `stories`
Represents a single narrative work uploaded by a user.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | **Primary Key.** |
| `owner_id` | `UUID` | **Foreign Key** to `users.id`. The user who uploaded the story. |
| `title` | `TEXT` | The title of the work (e.g., "The Crimson Seal"). |
| `author` | `TEXT` | The author of the work. |
| `status` | `TEXT` | The current processing status (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`). |
| `processing_plan` | `JSONB` | Stores the high-level plan from the Planner Agent (arcs, key article types). |
| `created_at` | `TIMESTAMPTZ` | Timestamp of upload. |
| `updated_at` | `TIMESTAMPTZ` | Timestamp of last modification or processing update. |

#### 5.4. `chapters`
Stores the raw text content for each chapter of a story.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | **Primary Key.** |
| `story_id` | `UUID` | **Foreign Key** to `stories.id`. |
| `chapter_number` | `INTEGER` | The sequential order of the chapter (1, 2, 3...). |
| `title` | `TEXT` | The title of the chapter (e.g., "The Descent"). |
| `raw_content` | `TEXT` | The full, original text of the chapter. |
| `created_at` | `TIMESTAMPTZ` | Timestamp of chapter creation. |

#### 5.5. `story_arcs`
Tracks the arc boundaries and metadata for each story.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | **Primary Key.** |
| `story_id` | `UUID` | **Foreign Key** to `stories.id`. |
| `arc_number` | `INTEGER` | Sequential arc number (1, 2, 3...). |
| `title` | `TEXT` | Arc title (e.g., "The Awakening"). |
| `start_chapter` | `INTEGER` | First chapter number in this arc. |
| `end_chapter` | `INTEGER` | Last chapter number in this arc. |
| `summary` | `TEXT` | Summary of the arc's narrative content. |
| `key_events` | `JSONB` | Important plot points and developments in this arc. |
| `token_count` | `INTEGER` | Approximate token count for the arc content. |
| `processing_status` | `TEXT` | Arc processing status (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`). |
| `created_at` | `TIMESTAMPTZ` | Timestamp of arc creation. |
| `updated_at` | `TIMESTAMPTZ` | Timestamp of last arc update. |

#### 5.6. `wiki_pages`
Collections of article snapshots at specific spoiler-safety levels for a story.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | **Primary Key.** |
| `story_id` | `UUID` | **Foreign Key** to `stories.id`. |
| `title` | `TEXT` | Display title for the wiki page (e.g., "Early Story Wiki"). |
| `description` | `TEXT` | Description of the wiki page contents and safety level. |
| `safe_through_chapter` | `INTEGER` | Maximum chapter number safe to read without spoilers. |
| `is_public` | `BOOLEAN` | Whether this wiki page is publicly accessible. |
| `creator_id` | `UUID` | **Foreign Key** to `users.id`. The user who created this wiki page. |
| `created_at` | `TIMESTAMPTZ` | Timestamp of wiki page creation. |
| `updated_at` | `TIMESTAMPTZ` | Timestamp of last wiki page update. |

#### 5.7. `articles`
Base article entities that can be shared across stories (characters, locations, concepts).

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | **Primary Key.** |
| `title` | `TEXT` | The human-readable title of the article (e.g., "Dr. Aris"). |
| `slug` | `TEXT` | A unique, URL-friendly identifier (e.g., "dr-aris"). **Globally unique**. |
| `article_type` | `TEXT` | Type of article (`character`, `location`, `concept`, `event`, `other`). |
| `canonical_name` | `TEXT` | The canonical name used for references and linking. |
| `creator_id` | `UUID` | **Foreign Key** to `users.id`. The user who created this article. |
| `metadata` | `JSONB` | Structured data about the entity (e.g., tags, aliases, categories). |
| `created_at` | `TIMESTAMPTZ` | Timestamp of the article's creation. |
| `updated_at` | `TIMESTAMPTZ` | Timestamp of the article's last update. |

#### 5.8. `article_snapshots`
Versioned content for articles tied to specific stories and spoiler-safety levels.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | **Primary Key.** |
| `article_id` | `UUID` | **Foreign Key** to `articles.id`. The base article this is a version of. |
| `content` | `TEXT` | The full article content in **Markdown format** with `[[Wikilinks]]`. |
| `preview` | `TEXT` | Short preview text for hover tooltips and quick reference. |
| `last_safe_chapter` | `INTEGER` | Last chapter number safe to read without spoilers. |
| `source_story_id` | `UUID` | **Foreign Key** to `stories.id`. The story that generated this version. |
| `version_number` | `INTEGER` | Version number within the source story (1, 2, 3...). |
| `parent_snapshot_id` | `UUID` | **Foreign Key** to `article_snapshots.id`. Previous version for history tracking. |
| `embedding` | `vector(1536)` | **(Using `pgvector` extension)**. Vector embedding for semantic search. |
| `created_at` | `TIMESTAMPTZ` | Timestamp of snapshot creation. |
| `updated_at` | `TIMESTAMPTZ` | Timestamp of snapshot update. |

**Note:** Article snapshots enable spoiler prevention by creating story-specific versions at different safety levels.

#### 5.9. `wiki_page_article_links`
Links wiki pages to specific article snapshots with display metadata.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | **Primary Key.** |
| `wiki_page_id` | `UUID` | **Foreign Key** to `wiki_pages.id`. |
| `article_snapshot_id` | `UUID` | **Foreign Key** to `article_snapshots.id`. |
| `display_order` | `INTEGER` | Order in which articles appear on the wiki page. |
| `is_featured` | `BOOLEAN` | Whether this article is featured prominently on the page. |
| `created_at` | `TIMESTAMPTZ` | Timestamp of link creation. |

#### 5.10. `article_story_associations`
Tracks which articles are referenced by which stories for cross-story relationships.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | **Primary Key.** |
| `article_id` | `UUID` | **Foreign Key** to `articles.id`. |
| `story_id` | `UUID` | **Foreign Key** to `stories.id`. |
| `association_type` | `TEXT` | Type of association (`referenced`, `originated`, `shared_universe`). |
| `context_metadata` | `JSONB` | Additional context about how the article relates to the story. |
| `created_at` | `TIMESTAMPTZ` | Timestamp of association creation. |

**Spoiler Prevention Logic:**
- Spoiler prevention is handled through chapter-based article snapshots
- Frontend applications track user reading progress locally
- Wiki pages are filtered by `safe_through_chapter` on the client side
- This ensures readers only see wiki content appropriate for their progress

#### 5.11. `enhanced_chapters`
Stores chapter content enhanced with wiki-style backlinks.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | **Primary Key.** |
| `chapter_id` | `UUID` | **Foreign Key** to `chapters.id`. |
| `arc_id` | `UUID` | **Foreign Key** to `story_arcs.id`. The arc this enhanced version belongs to. |
| `enhanced_content` | `TEXT` | Chapter content with `[[WikiLinks]]` added by ChapterBacklinker agent. |
| `link_metadata` | `JSONB` | Metadata about the links added (positions, target articles, context). |
| `created_at` | `TIMESTAMPTZ` | Timestamp of enhanced chapter creation. |
| `updated_at` | `TIMESTAMPTZ` | Timestamp of last enhancement update. |

**Note:** Multiple enhanced versions per chapter enable arc-specific linking that avoids spoilers.

---

### 6. In-Memory Storage Implementation (Local Mode)

For local/CLI deployment, the same data structures are maintained in memory using Python dictionaries:

```python
class InMemoryUserRepository:
    def __init__(self):
        self._users: Dict[UUID, User] = {}
        self._api_keys: Dict[str, UserAPIKey] = {}  # Composite key: f"{user_id}::{provider}"
    
    def _get_api_key_composite_key(self, user_id: UUID, provider: str) -> str:
        return f"{user_id}::{provider}"
```

**Key characteristics of in-memory storage:**
- **Ephemeral:** Data exists only during the application runtime
- **Fast:** Direct memory access with no network latency
- **Simple:** No database setup or migration management required
- **Consistent:** Same data models and relationships as persistent storage
- **Optional Persistence:** Can export/import data to/from JSON files for continuity

### 7. Chapter-Based Article Versioning Benefits

#### 7.1 Spoiler Prevention Through Article Snapshots
*   **Chapter-Specific Versions:** Each `article_snapshot` has a `last_safe_chapter`, enabling progressive disclosure
*   **Story-Specific Content:** Articles can have different versions across stories while sharing base entities
*   **Client-Side Filtering:** Frontend applications filter content based on user's current reading progress
*   **Flexible Safety Levels:** Wiki pages can be created for any chapter threshold (e.g., "Safe through Chapter 5")

#### 7.2 Shared Universe Support
*   **Base Articles:** `articles` table contains shared entities (characters, locations) across stories
*   **Story-Specific Snapshots:** Each story generates its own versions of shared articles
*   **Cross-Story References:** `article_story_associations` track how articles relate to different stories
*   **Version History:** `parent_snapshot_id` maintains evolution history within each story

#### 7.3 Incremental Processing Support
*   **Arc Boundaries:** `story_arcs` table still tracks processing units and their status
*   **Versioned Content:** Article snapshots can be updated chapter-by-chapter as processing progresses
*   **Processing State:** Each arc maintains independent processing status for robust error handling
*   **Content Evolution:** Character development tracked through snapshot versions with parent relationships

#### 7.4 Scalability and Performance
*   **Parallel Processing:** Different arcs and stories can be processed concurrently
*   **Efficient Queries:** Chapter-based filtering reduces dataset size for user queries
*   **Caching Friendly:** Snapshot-based content enables effective caching strategies per safety level
*   **Storage Optimization:** Only relevant snapshots need to be loaded based on user progress

### 8. Key Relationships and Data Flow

#### 8.1 Web Deployment (Supabase)
*   **User and Keys:** A `user` has a `subscription_tier`. For `free_byok` users, encrypted API keys are stored in `user_api_keys` table.
*   **Story Processing:** Background workers process stories arc-by-arc, updating `story_arcs` and generating `article_snapshots`
*   **Wiki Composition:** `wiki_pages` link to appropriate `article_snapshots` based on `safe_through_chapter` thresholds
*   **Article Evolution:** `article_snapshots` track content changes through `parent_snapshot_id` relationships
*   **Cross-Story Sharing:** `articles` can be referenced across multiple stories via `article_story_associations`
*   **Enhanced Reading:** `enhanced_chapters` provide wiki-linked reading experience per arc

#### 8.2 Local Deployment (In-Memory)
*   **No User Accounts:** Direct API usage without user registration or authentication
*   **Temporary Keys:** API keys managed in memory only during processing session
*   **Arc-Based Processing:** Same arc and snapshot logic applied to in-memory data structures
*   **File Export:** Wiki pages and article snapshots can be exported to file system for persistence
*   **Optional Sharing:** Generated articles can be shared across local story processing sessions

### 8. Configuration and Switching

The storage backend is controlled by the `SKIP_DATABASE` configuration setting:

```python
# .env configuration
SKIP_DATABASE=false  # Use Supabase (default for web deployment)
SKIP_DATABASE=true   # Use in-memory storage (for local/CLI usage)
```

The application automatically selects the appropriate repositories based on this setting, allowing the same codebase to work in both modes without modification.

### 9. Migration and Development

#### 9.1 Supabase Migrations
For web deployment, database schema changes are managed through Supabase migration files:
- Schema changes defined in SQL migration files
- Applied through Supabase CLI or dashboard
- Version controlled for consistent deployments

#### 9.2 In-Memory Schema Evolution
For local mode, schema changes are handled through code updates:
- Data models updated in Python schemas
- No migration scripts needed
- Backward compatibility maintained through versioned export formats

### 10. Performance and Indexing (Supabase)

The indexing strategy for Supabase deployment includes:

**Core Tables:**
*   **`users`:** Primary key on `id`, unique index on `email`
*   **`user_api_keys`:** Composite primary key on `(user_id, provider)`
*   **`stories`:** Primary key on `id`, index on `owner_id`, index on `status`
*   **`chapters`:** Primary key on `id`, composite index on `(story_id, chapter_number)`
*   **`story_arcs`:** Primary key on `id`, index on `story_id`, composite index on `(story_id, arc_number)`

**Wiki Tables:**
*   **`articles`:** Primary key on `id`, unique index on `slug`, index on `article_type`, index on `creator_id`
*   **`article_snapshots`:** Primary key on `id`, index on `article_id`, composite index on `(source_story_id, last_safe_chapter)`, GIN index on `embedding` for vector search
*   **`wiki_pages`:** Primary key on `id`, index on `story_id`, index on `creator_id`, composite index on `(story_id, safe_through_chapter)`
*   **`wiki_page_article_links`:** Primary key on `id`, index on `wiki_page_id`, index on `article_snapshot_id`, composite index on `(wiki_page_id, display_order)`
*   **`article_story_associations`:** Primary key on `id`, composite index on `(article_id, story_id)`, index on `story_id`

**Enhanced Content:**
*   **`enhanced_chapters`:** Primary key on `id`, index on `chapter_id`, index on `arc_id`, composite index on `(chapter_id, arc_id)`

In-memory storage achieves optimal performance through direct dictionary lookups and relationship indexes without requiring explicit database indexing.