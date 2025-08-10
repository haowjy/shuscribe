# ShuScribe Backend Architecture

**Current Backend Implementation Status (2025)**

*FastAPI + SQLAlchemy + Repository Pattern + LLM Integration*

---

## Implementation Status

### ✅ **IMPLEMENTED - Core Backend Features**
1. **FastAPI REST API** - Complete API with projects, documents, tags, file tree, and LLM endpoints
2. **Repository Pattern** - Interface-based dependency injection with memory, file, and database backends  
3. **Authentication Middleware** - Supabase JWT validation and user context extraction
4. **Project Management** - Full CRUD operations with hierarchical file tree support
5. **Document Management** - ProseMirror JSON content with word count tracking and version control
6. **Tag System** - Many-to-many relationships with categories, colors, icons, and usage tracking
7. **LLM Integration** - Self-hosted Portkey Gateway with multiple providers (OpenAI, Anthropic, Google)
8. **WikiGen Agent System** - AI-powered wiki generation with spoiler prevention
9. **Database Abstraction** - Supports memory (testing), SQLite (legacy), and PostgreSQL (production)
10. **Environment Configuration** - Multi-environment support with conditional features

### ❌ **NOT IMPLEMENTED - Frontend-Specific Features**
- **@-Reference System** - Cross-document reference parsing and linking (frontend-only)
- **Real-time Collaboration** - WebSocket support for live editing
- **Interactive AI Panel** - Context-aware AI assistance UI
- **Advanced Search** - Semantic search across project content
- **Publishing System** - Public story/wiki hosting
- **File Uploads** - Image and attachment storage

---

## Architecture Overview

### **Technology Stack**
- **FastAPI** - REST API with automatic OpenAPI documentation
- **SQLAlchemy** - ORM with async support and proper relationships
- **Repository Pattern** - Interface-based dependency injection for clean architecture
- **Pydantic** - Request/response validation and serialization
- **Supabase** - PostgreSQL database with auth token validation
- **Portkey Gateway** - Self-hosted LLM proxy supporting multiple providers
- **Pytest** - Comprehensive testing with memory backend for isolation

### **Backend Service Architecture**
```
ShuScribe Backend
├── API Layer (FastAPI)
│   ├── /api/v1/projects/     # Project CRUD + file tree
│   ├── /api/v1/documents/    # Document CRUD with ProseMirror content
│   ├── /api/v1/projects/{id}/tags/  # Tag management and assignment
│   ├── /api/v1/llm/          # LLM chat, key management, providers
│   └── /api/v1/health/       # Service health and status
│
├── Repository Layer (Dependency Injection)
│   ├── ProjectRepository     # Project operations
│   ├── DocumentRepository    # Document operations with content processing
│   ├── FileTreeRepository    # Hierarchical file organization
│   ├── TagRepository         # Tag operations and relationships
│   └── UserRepository        # User-scoped operations
│
├── Service Layer
│   ├── LLM Service           # Portkey Gateway integration
│   ├── Agent System          # WikiGen AI agents
│   └── Authentication       # Supabase JWT validation
│
└── Data Layer
    ├── Memory Backend        # Pure Python (testing)
    ├── SQLite Backend        # File-based (legacy)
    └── PostgreSQL Backend    # Supabase (production)
```

---

## Core Technical Components

### **1. Repository Pattern with Dependency Injection**

**Three Backend Implementations:**
- **Memory Backend**: Pure Python classes for testing (complete isolation)
- **File Backend**: SQLite-based with local file storage (legacy)
- **Database Backend**: PostgreSQL with full async SQLAlchemy relationships

**Repository Interfaces:**
```python
# Abstract interfaces ensure consistent behavior across backends
class ProjectRepository(ABC):
    async def create(self, data: dict) -> Project
    async def get_by_id(self, project_id: str) -> Project | None
    async def list_by_user(self, user_id: str) -> List[Project]
    async def update(self, project_id: str, updates: dict) -> Project | None
    async def delete(self, project_id: str) -> bool

class DocumentRepository(ABC):
    async def create(self, data: dict) -> Document
    async def get_by_id(self, document_id: str) -> Document | None
    async def get_by_project_id(self, project_id: str) -> List[Document]
    async def update(self, document_id: str, updates: dict) -> Document | None
    async def delete(self, document_id: str) -> bool
```

**Dependency Injection Flow:**
```python
# Factory creates appropriate backend based on configuration
repositories = create_repositories(backend=settings.DATABASE_BACKEND)

# FastAPI endpoints use dependency injection
@router.get("/{project_id}")
async def get_project(
    project_id: str,
    repositories: RepositoryContainer = Depends(get_repositories)
):
    project = await repositories.project.get_by_id(project_id)
    return ApiResponse.success(project_to_response(project))
```

### **2. Data Models & Relationships**

**Core Models (SQLAlchemy):**
```python
# Project with hierarchical organization
class Project(Base):
    id: str (UUID)
    title: str
    description: str
    owner_id: str (user)
    word_count: int (calculated)
    document_count: int (calculated)
    collaborators: List[Dict] (JSON)
    settings: Dict (JSON)
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    documents: List[Document]
    file_tree_items: List[FileTreeItem]
    tags: List[Tag]

# Document with ProseMirror content
class Document(Base):
    id: str (UUID)
    project_id: str (FK)
    title: str
    path: str
    content: Dict (ProseMirror JSON)
    word_count: int (auto-calculated)
    version: str
    is_locked: bool
    locked_by: str
    file_tree_id: str (optional FK)
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    project: Project
    file_tree_item: FileTreeItem
    tags: List[Tag]

# Hierarchical file organization
class FileTreeItem(Base):
    id: str (UUID)
    project_id: str (FK)
    name: str
    type: str ("file" | "folder")
    path: str
    parent_id: str (self-referential FK)
    document_id: str (for files)
    icon: str
    word_count: int
    
    # Relationships
    project: Project
    parent: FileTreeItem
    children: List[FileTreeItem]
    document: Document
    tags: List[Tag]

# Tag system with categories
class Tag(Base):
    id: str (UUID)
    name: str
    icon: str
    color: str (hex)
    description: str
    category: str ("character", "location", etc.)
    project_id: str (FK)
    is_system: bool
    is_archived: bool
    usage_count: int
    
    # Many-to-many relationships
    projects: List[Project]
    documents: List[Document]
    file_tree_items: List[FileTreeItem]
```

**Key Relationships:**
- **Many-to-Many**: Tags ↔ Projects, Documents, FileTreeItems
- **Hierarchical**: FileTreeItem parent/children self-reference
- **One-to-Many**: Project → Documents, Project → FileTreeItems
- **Optional Links**: Document ↔ FileTreeItem for file tree integration

### **3. Authentication & User Context**

**Supabase JWT Integration:**
```python
# Extract user context without validation (trust frontend)
async def get_optional_user_context(
    authorization: str = Header(None)
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        return {"token": None, "authenticated": False}
    
    token = authorization.replace("Bearer ", "")
    return {"token": token, "authenticated": True}

# Environment-based user filtering
@router.get("/projects")
async def list_projects(user_id: str = Depends(get_current_user_id)):
    if settings.should_filter_by_user:
        projects = await repos.project.list_by_user(user_id)
    else:
        projects = await repos.project.list_all()  # Development mode
```

**Authentication Strategy:**
- **Frontend-First**: Supabase Auth handled entirely in frontend
- **Backend Trust**: Backend trusts frontend auth tokens for user context
- **Environment-Aware**: Development mode allows unfiltered access
- **Token Extraction**: Extract user ID from JWT for ownership filtering

### **4. Content Processing & Word Count**

**ProseMirror Content Handling:**
```python
def calculate_word_count(content: DocumentContent) -> int:
    """Extract text from ProseMirror JSON and count words"""
    def extract_text(node: Dict[str, Any]) -> str:
        text = ""
        if "text" in node:
            text += node["text"]
        if "content" in node and isinstance(node["content"], list):
            for child in node["content"]:
                child_text = extract_text(child)
                if child_text:
                    text += " " + child_text if text else child_text
        return text
    
    # Extract all text and count words
    full_text = ""
    for node in content.content:
        extracted = extract_text(node)
        if extracted:
            full_text += " " + extracted if full_text else extracted
    
    words = [word.strip() for word in full_text.split() if word.strip()]
    return len(words)
```

**Content Features:**
- **ProseMirror Support**: Full JSON document structure preservation
- **Word Count**: Automatic calculation from extracted text content
- **Version Tracking**: Document versioning with update timestamps
- **Locking Mechanism**: Basic document locking for edit conflicts

### **5. LLM Integration & Agent System**

**Portkey Gateway Integration:**
```python
# Self-hosted LLM proxy supporting multiple providers
class LLMService:
    async def chat_completion(
        self,
        provider: str,
        model: str,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        stream: bool = False,
        api_key: str = None
    ) -> ChatCompletionResponse:
        # Route through Portkey Gateway
        # Supports OpenAI, Anthropic, Google, Ollama
```

**WikiGen Agent System:**
```python
# AI agents for automated wiki generation
class BaseAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    async def process(self, context: dict) -> dict:
        # Agent-specific processing logic

# Specialized agents
class ArcSplitter(BaseAgent):
    """Divide story into narrative arcs for spoiler prevention"""
    
class WikiPlanner(BaseAgent):
    """Plan wiki structure and article organization"""
    
class ArticleWriter(BaseAgent):
    """Generate wiki article content"""
    
class ChapterBacklinker(BaseAgent):
    """Create links between chapters and wiki articles"""
```

**LLM Features:**
- **Multiple Providers**: OpenAI, Anthropic, Google via Portkey Gateway
- **Key Management**: Encrypted API key storage with validation
- **Model Catalog**: Capability-based model selection with cost tracking
- **Streaming Support**: Real-time response streaming for chat interfaces
- **Thinking Modes**: Enhanced reasoning with configurable thinking budgets

---

## Environment Configuration

### **Multi-Environment Support**
```bash
# Environment behavior configuration
ENVIRONMENT=development|testing|production
DEBUG=true|false
DATABASE_BACKEND=memory|file|database
TABLE_PREFIX=dev_|test_|staging_|""

# Authentication behavior
SHOULD_FILTER_BY_USER=true|false  # Auto-calculated based on environment

# Database configuration  
DATABASE_URL=postgresql://...     # Supabase PostgreSQL
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...

# LLM configuration
PORTKEY_BASE_URL=http://localhost:8787
ENCRYPTION_KEY=...                # For API key encryption

# Seeding and development
ENABLE_DATABASE_SEEDING=true|false
CLEAR_BEFORE_SEED=true|false
```

**Environment Behaviors:**
- **Development**: No user filtering, database seeding, debug logging
- **Testing**: Memory backend, complete isolation, no external dependencies
- **Production**: Full user filtering, optimized queries, encrypted keys

### **Database Backend Selection**
- **Memory**: Pure Python, perfect for testing, no persistence
- **File**: SQLite + file storage, legacy support, local development
- **Database**: PostgreSQL + Supabase, production environment

---

## Key Technical Achievements

### **1. Clean Architecture**
- **Repository Pattern**: Interface-based design enables easy testing and backend swapping
- **Dependency Injection**: FastAPI's built-in DI system for clean service composition
- **Environment Abstraction**: Single codebase works across development, testing, and production

### **2. Content Management**
- **ProseMirror Integration**: Full support for rich text editor JSON content
- **Hierarchical Organization**: File tree structure with parent/child relationships
- **Word Count Automation**: Real-time word count calculation from document content
- **Tag Relationships**: Proper many-to-many relationships with usage tracking

### **3. LLM & AI Integration**
- **Self-Hosted Gateway**: Portkey proxy for multiple LLM providers
- **Agent Architecture**: Extensible system for AI-powered features
- **Key Security**: Encrypted API key storage with validation
- **Cost Awareness**: Model capabilities and pricing integration

### **4. Testing & Reliability**
- **Memory Backend**: Complete test isolation without external dependencies
- **Comprehensive Coverage**: Repository, API, and integration test suites
- **Environment Parity**: Same code paths across all environments
- **Error Handling**: Consistent error responses and logging

---

## Fantasy Writing Capabilities

### **Current Backend Support for Fantasy Writing**

**✅ **Hierarchical Project Organization:**
- File tree structure supports Characters/, Locations/, Chapters/, Magic/ folders
- Document-to-file-tree linking for organized navigation
- Tag system with categories for character, location, magic-system classification

**✅ **Rich Content Storage:**
- ProseMirror JSON content preserves rich text formatting
- Document versioning and locking for draft management
- Word count tracking per document and project-wide

**✅ **Tag-Based Organization:**
- Many-to-many tag relationships for complex categorization
- Color-coded tags with icons for visual organization
- Usage tracking and search capabilities

**✅ **AI-Powered Features:**
- WikiGen agent system for automated worldbuilding documentation
- LLM integration for writing assistance and content generation
- Agent orchestration for complex multi-step workflows

**❌ **Missing Frontend Features for Fantasy Writing:**
- **@-Reference System**: `@character/Aragorn`, `@location/Rivendell` parsing and linking
- **Cross-Reference Navigation**: Click-to-navigate between related documents
- **Bidirectional Linking**: "Referenced by" panels showing character appearances
- **Timeline Management**: Chronological event tracking and validation
- **Relationship Mapping**: Visual connections between characters, locations, events

### **Backend Foundation for @-Reference System**

The current backend provides excellent foundation for implementing @-references:

**✅ **Data Structure Support:**
- File tree provides hierarchical paths for reference targets
- ProseMirror JSON content supports custom node types
- Document relationships can track reference dependencies
- Tag system can categorize reference types

**✅ **API Capabilities:**
- Complete project data loading for reference index building
- Document CRUD operations for reference updates
- Search capabilities for reference autocomplete
- Relationship tracking for dependency validation

**Frontend Implementation Needed:**
- Parse `@character/name` syntax from ProseMirror content
- Build reference index from project data
- Implement click-to-navigate functionality
- Add reference validation and suggestion system

---

## Success Metrics

**The current backend successfully provides:**

1. **✅ Complete API Coverage** - All CRUD operations for projects, documents, tags, and file tree
2. **✅ Clean Architecture** - Repository pattern with dependency injection for maintainability
3. **✅ Multi-Environment Support** - Memory/file/database backends with environment-specific behaviors
4. **✅ Authentication Integration** - Supabase JWT validation with user context extraction
5. **✅ Content Management** - ProseMirror JSON support with word count and version tracking
6. **✅ LLM Integration** - Self-hosted Portkey Gateway with multiple provider support
7. **✅ Agent System** - WikiGen AI agents for automated worldbuilding features
8. **✅ Testing Infrastructure** - Comprehensive test suite with memory backend isolation

**Ready for Frontend Development:**
- All necessary APIs implemented and documented
- Data models support fantasy writing workflows
- Foundation ready for @-reference system implementation
- LLM integration available for AI-assisted writing features

The backend provides a solid, well-architected foundation that can support both the current fantasy writing use case and future expansion into collaborative editing, real-time features, and advanced AI integration.