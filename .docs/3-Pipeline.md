# Main Chapter Processing and Wiki Generation Pipeline

## ⚠️ Implementation Status

**Current Status:** The pipeline described below represents the **planned architecture** for ShuScribe's story processing and wiki generation. The current implementation includes the foundational infrastructure with core processing logic in active development.

**What's Currently Available:**
- ✅ Pipeline service structure and interfaces
- ✅ LLM integration framework with provider support
- ✅ Repository pattern supporting both web and local deployments
- ✅ Story and chapter data models
- 🔄 Entity extraction and wiki generation logic (in development)
- 🔄 Background task processing (planned for web deployment)
- ❌ Complete end-to-end pipeline execution

**Deployment Modes:** The pipeline is designed to work in both **web deployment** (with background processing) and **local deployment** (with synchronous processing) modes.

---

### 1. Overview

This document outlines the end-to-end automated pipeline for processing a narrative work and generating a structured, interlinked wiki. The pipeline is designed to be flexible, supporting both asynchronous processing for web deployment and synchronous processing for local/CLI usage.

The pipeline's primary goal is to transform unstructured narrative text (chapters) into a structured set of database records representing wiki articles, complete with metadata and cross-referenced links.

The process can be visualized in four main phases:
1.  **Ingestion & Planning:** The system receives the story and creates a high-level plan for analysis.
2.  **Iterative Arc Processing:** The system analyzes the story in logical "arcs," extracting and consolidating narrative elements.
3.  **Article Generation & Linking:** For each element, the system drafts, refines, and cross-references a Markdown-based wiki article.
4.  **Storage & Persistence:** The final articles are stored in the appropriate backend (Supabase or in-memory), ready to be served.

#### Web Deployment Flow:
```
[User Upload] → [API Endpoint] → [Background Queue] → [1. Ingestion & Planning] → [2. Arc Processing] → [3. Article Generation] → [4. Supabase Storage]
                                                           ↑      ↓
                                                           (Iterative Loop)
```

#### Local Deployment Flow:
```
[CLI/API Call] → [Direct Processing] → [1. Ingestion & Planning] → [2. Arc Processing] → [3. Article Generation] → [4. In-Memory Storage/Export]
                                                                        ↑      ↓
                                                                        (Iterative Loop)
```

---

### 2. Phase 1: Ingestion and High-Level Planning

This phase begins immediately after a user uploads a new story via API or CLI.

**Step 1.1: Content Ingestion and Structuring**

*Web Deployment:*
*   The FastAPI backend receives the uploaded content via REST API endpoints.
*   A primary `Story` record is created in Supabase, generating a unique `story_id`. Its initial status is set to `PENDING`.
*   The content is parsed into individual chapters, stored in the `chapters` table with proper relationships.

*Local Deployment:*
*   The CLI/API receives content directly (file upload or text input).
*   A `Story` object is created in memory with a generated UUID.
*   Chapters are parsed and stored in the in-memory repository.

**Step 1.2: Processing Task Initiation**

*Web Deployment:*
*   The backend enqueues a "master processing task" into the background task queue.
*   The API immediately returns a `202 Accepted` response with the `story_id`.
*   Processing continues asynchronously without blocking the user.

*Local Deployment:*
*   Processing begins immediately and synchronously.
*   The user receives real-time feedback during processing.
*   Results are available immediately upon completion.

**Step 1.3: The Planner Agent**

*   **Input:** The full text of all chapters for the given `story_id`. For extremely large works, it may use chapter titles and summaries to conserve context.
*   **LLM Integration:** Uses the user's provided API key (retrieved from storage or memory) to call a cost-effective LLM (e.g., Gemini Flash, GPT-3.5-Turbo).
*   **LLM Prompt:** A specialized prompt asks the LLM to perform two tasks:
    1.  **Identify Narrative Arcs:** "Analyze the provided chapters and divide the story into logical arcs or sagas. Provide a start and end chapter for each arc."
    2.  **Identify Key Article Types:** "Based on the story's genre and content, list the most important categories of wiki articles to generate (e.g., Characters, Locations, Factions, Terminology, Magic System, Key Events)."
*   **Output:** A structured JSON object containing the list of arcs and the list of key entity types.
*   **Storage:** 
    - *Web:* Plan saved to the `Story` record's metadata field in Supabase. Status updated to `PROCESSING`.
    - *Local:* Plan stored in the in-memory story object.

---

### 3. Phase 2: Iterative Arc Processing (The Core Loop)

The system iterates through the arcs defined in the plan, processing them sequentially to build up the wiki progressively. This approach ensures information from later chapters doesn't leak into articles about earlier events.

For each arc in the plan:

**Step 2.1: Entity Extraction**
*   **Processing Context:**
    - *Web:* Background worker picks up arc processing task
    - *Local:* Direct processing in main thread with progress feedback
*   **Input:** The full text of all chapters *within that arc*.
*   **LLM Call:** Using the user's API key to call the LLM service:
    - "From the provided text, extract all named entities that fall under the following categories: [List of types from Planner Agent]. For each entity, provide its name, any aliases used, and the context of its first appearance in this arc."
*   **Output:** A raw list of all potential entities mentioned in the arc.

**Step 2.2: Entity Resolution and Consolidation**
*   This is a critical non-LLM step performed by the application logic.
*   For each extracted entity (e.g., "the doctor"):
    1.  Query the appropriate repository (Supabase or in-memory) for existing articles with matching names or aliases.
    2.  **If a match is found:** Use the existing article ID and mark it for update with new information from the current arc.
    3.  **If no match is found:** Create a new article record with `title`, `slug`, and basic metadata. Content is initially empty.

---

### 4. Phase 3: Article Generation and Cross-Linking

After all entities for an arc have been identified and resolved, the system generates or updates the content for their wiki articles.

**Step 3.1: Article Content Drafting**
*   **Processing:** For each entity identified for creation or update:
*   **Input Data:**
    *   The entity's `title` and `type`.
    *   All contextual snippets where the entity was mentioned *in the current arc*.
    *   **For updates:** The previous version of the Markdown `content` from the repository.
*   **LLM Integration:** Using the user's API key to call the LLM:
    - **Prompt:** "You are a wiki author. [Update/Write] the wiki article for the character '[Entity Title]'. The article should be a comprehensive summary of their knowledge and actions *up to the end of Chapter X*. Here is the existing article content to update: [Previous Markdown]. Here is all the new information from the latest story arc: [Contextual Snippets]. Integrate the new information seamlessly, expanding the biography and relationships sections as needed. The output must be in Markdown."
*   **Output:** A block of Markdown text representing the new, complete article.

**Step 3.2: Automated Wikilinking**
*   **Post-processing:** The generated Markdown undergoes automated link generation.
*   **Process:**
    1.  Fetch all `title`s and known `aliases` for every wiki article in the current story.
    2.  Scan the newly drafted Markdown text for matches.
    3.  Replace matched terms with Wikilink syntax: `[[Entity Title]]`.
*   **Result:** Densely and accurately interlinked wiki content without requiring the LLM to manage link formatting.

---

### 5. Phase 4: Storage & Persistence

The final step where generated content is committed to storage.

**Web Deployment:**
*   Execute `UPDATE` commands on the Supabase `wiki_articles` table.
*   Update the `content` field with the new Wikilinked Markdown.
*   Refresh `updated_at` timestamps.
*   Mark arc as complete and proceed to next arc.
*   When all arcs are processed, set the master `Story` status to `COMPLETED`.

**Local Deployment:**
*   Update the in-memory repository with new article content.
*   Optionally export the generated wiki to files (JSON, Markdown, HTML).
*   Return the complete wiki data structure to the user.
*   Provide immediate access to all generated articles.

### 6. Current Implementation Architecture

#### 6.1 Service Layer Structure

```python
# Service interfaces (implemented)
class PipelineService:
    async def process_story(self, story_id: UUID) -> ProcessingResult
    
class WikiService:
    async def generate_article(self, entity: Entity, context: str) -> WikiArticle
    
class StoryService:
    async def create_story(self, story_data: dict) -> Story
```

#### 6.2 LLM Integration Framework

```python
# LLM provider abstraction (implemented)
class LLMProvider:
    async def complete(self, prompt: str, **kwargs) -> str
    
# Supported providers
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Google (Gemini)
- Others via Portkey Gateway
```

#### 6.3 Repository Pattern Support

```python
# Abstract repositories (implemented)
class AbstractStoryRepository:
    async def create_story(self, data: dict) -> Story
    async def get_story(self, story_id: UUID) -> Story
    
# Dual implementations
- SupabaseStoryRepository (web deployment)
- InMemoryStoryRepository (local deployment)
```

### 7. Deployment-Specific Characteristics

#### 7.1 Web Deployment Features
*   **Asynchronous Processing:** Heavy lifting done by background workers
*   **Scalable:** Horizontally scalable worker pools
*   **Persistent:** All data stored in Supabase for long-term access
*   **Multi-user:** Supports multiple concurrent users and stories
*   **Real-time Updates:** Progress tracking and status updates via WebSocket (planned)

#### 7.2 Local Deployment Features
*   **Immediate Results:** Synchronous processing with real-time feedback
*   **No Dependencies:** No database or queue setup required
*   **Portable:** Complete processing in a single executable
*   **Privacy:** All data remains local during processing
*   **Exportable:** Results can be saved to various formats

### 8. Error Handling and Resilience

*   **Graceful Degradation:** If LLM calls fail, the system can retry with backoff or skip problematic content
*   **Atomic Operations:** Each arc and article is processed independently
*   **Recovery:** Failed processing can be resumed from the last successful arc
*   **Validation:** Generated content is validated before storage
*   **Logging:** Comprehensive logging for debugging and monitoring

### 9. Future Enhancements

*   **Incremental Processing:** Support for adding new chapters to existing stories
*   **Quality Metrics:** Automated assessment of generated wiki quality
*   **Custom Templates:** User-defined article templates for different entity types
*   **Collaborative Editing:** Manual refinement of auto-generated content (web mode)
*   **Advanced Linking:** Semantic similarity-based linking beyond exact text matches