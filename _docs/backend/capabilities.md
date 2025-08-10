# Backend Capabilities

**Current Backend Features for Fantasy Writing Applications**

## ✅ **IMPLEMENTED FEATURES**

### **Project Organization**
- **Hierarchical File Tree**: Full project structure with folders and documents
- **Path-Based Navigation**: `/characters/protagonists/aria_stormwind`
- **Document Linking**: Optional file tree ↔ document relationships
- **Word Count Tracking**: Automatic word count calculation and tracking

### **Document Management**
- **ProseMirror Content**: Rich text JSON format with formatting, headings, lists
- **Version Control**: Document versioning with timestamps
- **Content Types**: Character sheets, location descriptions, story chapters, magic systems
- **Auto-Save**: Persistent document storage with change tracking

### **Tag System**
- **Many-to-Many Tags**: Documents can have multiple tags, tags can apply to multiple documents
- **Tag Categories**: Organize tags by type (character-traits, locations, magic-types)
- **Tag Metadata**: Colors, icons, descriptions for visual organization
- **Usage Tracking**: Track tag usage across projects

### **Authentication & Security**
- **Supabase JWT**: Token validation and user context extraction
- **Project Isolation**: Users can only access their own projects
- **Role-Based Access**: Foundation for future collaboration features

### **LLM Integration**
- **Portkey Gateway**: Self-hosted gateway supporting multiple LLM providers
- **WikiGen Agent**: AI-powered wiki generation for worldbuilding
- **Context-Aware**: AI agents understand project structure and content
- **Spoiler Prevention**: AI avoids revealing future plot points

### **Database Architecture**
- **Repository Pattern**: Interface-based dependency injection
- **Multi-Backend Support**: Memory (testing), SQLite (legacy), PostgreSQL (production)
- **Async Operations**: Non-blocking database operations
- **Relationship Management**: Proper foreign key relationships and constraints

## ❌ **NOT IMPLEMENTED - Frontend Features**
- **@-Reference System**: Cross-document reference parsing (frontend-only)
- **Real-time Collaboration**: WebSocket support for live editing
- **File Uploads**: Image and attachment storage
- **Advanced Search**: Semantic search across project content
- **Publishing System**: Public story/wiki hosting

## **API Endpoints**
- **Projects**: CRUD operations for project management
- **Documents**: Create, read, update, delete with ProseMirror content
- **File Tree**: Hierarchical project navigation
- **Tags**: Tag management and assignment
- **LLM**: AI-powered content generation and assistance

## **Integration Points**
- **Frontend Contract**: Backend implements APIs matching `frontend/src/types/api.ts`
- **Response Format**: Consistent `ApiResponse<T>` wrapper
- **Field Naming**: Backend supports both camelCase and snake_case via Pydantic aliases
- **Error Handling**: Standardized error responses matching frontend expectations

## **Development Setup**
```bash
# Backend setup
cd backend
uv sync && source .venv/bin/activate
uv run hypercorn src.main:app --reload --bind "[::]:8000"

# Run tests
uv run pytest
uv run pytest --cov=src --cov-report=html
```

The backend provides a solid foundation for complex fantasy writing applications with comprehensive project management, rich document support, and AI integration capabilities.