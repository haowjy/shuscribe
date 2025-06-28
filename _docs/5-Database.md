# Database Storage and Relationships

### 1. Design Philosophy

ShuScribe employs a **flexible data storage architecture** that supports both persistent database storage and in-memory storage, depending on the deployment mode. The design is built around a repository pattern that abstracts the underlying storage mechanism while maintaining data integrity and consistency.

The architecture is designed to support:

*   **Multi-tenancy:** Cleanly separating data for different users and stories (web deployment).
*   **Hybrid API Key Model (BYOK):** Securely storing user-provided API keys in persistent storage (web) or managing them in-memory (local).
*   **Content Versioning:** Storing raw chapter content allows for easy reprocessing.
*   **Structured Wiki Data:** Modeling the wiki as a collection of interlinked articles.
*   **Spoiler Prevention:** Tracking user progress is a first-class concern (web deployment).
*   **Local Development:** Supporting immediate local usage without requiring database setup.

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
└──────────────┘    │ └────────────────┘      └──────────┘     │└───────────┘
      ▲             │                           ▲            │
      │             │                           │            │
┌─────┴────────┐    │                      ┌────┴────────────┴──┐
│ user_progress│────┘                      │   wiki_articles    │
└──────────────┘                           └────────────────────┘
                                                 ▲      │
                                                 └──────┘ (Self-referencing via Wikilinks)
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

#### 5.5. `wiki_articles`
The core table for the generated wiki. Each row is a single, self-contained wiki page.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | **Primary Key.** |
| `story_id` | `UUID` | **Foreign Key** to `stories.id`. |
| `title` | `TEXT` | The human-readable title of the article (e.g., "Dr. Aris"). This is used for `[[Wikilinks]]`. |
| `slug` | `TEXT` | A unique, URL-friendly identifier (e.g., "dr-aris"). **Unique per `story_id`**. |
| `content` | `TEXT` | The full article body in **Markdown format**, containing `[[Wikilinks]]` to other articles. |
| `metadata` | `JSONB` | Structured data about the entity (e.g., `{"type": "Character", "significance": "Major", "aliases": ["The Doctor"]}`). |
| `embedding` | `vector(1536)` | **(Using `pgvector` extension)**. Vector embedding of the article's content for semantic search. |
| `created_at` | `TIMESTAMPTZ` | Timestamp of the article's first generation. |
| `updated_at` | `TIMESTAMPTZ` | Timestamp of the article's last update. |

#### 5.6. `user_progress`
Tracks how far each user has read in each story, enabling spoiler prevention.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `user_id` | `UUID` | **Composite Primary Key, Foreign Key** to `users.id`. |
| `story_id` | `UUID` | **Composite Primary Key, Foreign Key** to `stories.id`. |
| `last_read_chapter` | `INTEGER` | The number of the last chapter the user has completed. |
| `updated_at` | `TIMESTAMPTZ` | Timestamp of the last progress update. |

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

### 7. Key Relationships and Data Flow

#### 7.1 Web Deployment (Supabase)
*   **User and Keys:** A `user` has a `subscription_tier`. For `free_byok` users, encrypted API keys are stored in `user_api_keys` table.
*   **Processing Logic:** Background workers query Supabase for user keys, decrypt them in memory, and use them for LLM calls.
*   **Progress Tracking:** User reading progress is persistently tracked for spoiler prevention.

#### 7.2 Local Deployment (In-Memory)
*   **No User Accounts:** Direct API usage without user registration
*   **Temporary Keys:** API keys managed in memory only during processing
*   **Immediate Processing:** Stories processed synchronously without background tasks
*   **Optional Export:** Generated wikis can be exported to files

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

*   **`users`:** Primary key on `id`, unique index on `email`
*   **`user_api_keys`:** Composite primary key on `(user_id, provider)`
*   **`stories`:** Primary key on `id`, index on `owner_id`, index on `status`
*   **`chapters`:** Primary key on `id`, composite index on `(story_id, chapter_number)`
*   **`wiki_articles`:** Primary key on `id`, unique index on `(story_id, slug)`, index on `story_id`, GIN index on `embedding` for vector search
*   **`user_progress`:** Composite primary key on `(user_id, story_id)`

In-memory storage achieves optimal performance through direct dictionary lookups without requiring explicit indexing.