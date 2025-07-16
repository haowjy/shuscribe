# Publication System - Future Implementation Plan

## Overview

This document outlines the future implementation plan for ShuScribe's publication system, which will enable writers to manage document workflows from draft to published state, create wiki collections, and maintain proper version control.

## Core Architecture Principles

### System State vs User Tags Separation

**System Fields (Protected):**
- `publication_status` - Controlled workflow state
- `is_wiki_page` - System-managed collection membership
- `approval_status` - Workflow validation state
- `published_at` / `published_by` - Audit trail

**User Tags (Flexible):**
- `tags: string[]` - User-defined organizational labels
- No business logic dependencies
- No validation constraints
- Flexible and subjective categorization

This separation ensures:
- ✅ **System reliability** - Business logic can depend on validated system fields
- ✅ **User flexibility** - Tags remain unconstrained for personal organization
- ✅ **Clear permissions** - Different edit permissions for system vs user metadata
- ✅ **Query performance** - System fields use indexed columns, user tags use JSON

## Database Schema Design

### Extended FileTreeItem Model

```python
class FileTreeItem(Base):
    """Extended file tree item with publication system support"""
    __tablename__ = f"{settings.table_prefix}file_tree_items"
    
    # ... existing fields (id, project_id, name, type, path, parent_id, document_id) ...
    
    # ============================================================================
    # USER METADATA (Flexible, unvalidated)
    # ============================================================================
    tag_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)  # References to ProjectTag.id
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # hex color
    
    # ============================================================================
    # SYSTEM STATE (Controlled, validated)
    # ============================================================================
    publication_status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="draft"
    )  # draft, review, published, archived
    
    approval_status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="pending"
    )  # pending, approved, rejected
    
    # Wiki and Collection Management
    is_wiki_page: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    wiki_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    collection_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    
    # Workflow Metadata
    priority: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # low, medium, high
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # character, location, plot, etc.
    
    # ============================================================================
    # AUDIT TRAIL (Read-only)
    # ============================================================================
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    published_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_reviewed_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Analytics
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # ... existing timestamp fields (created_at, updated_at) ...
    
    # ============================================================================
    # DATABASE CONSTRAINTS
    # ============================================================================
    __table_args__ = (
        # Existing constraints
        CheckConstraint(
            "(type = 'file' AND document_id IS NOT NULL) OR (type = 'folder' AND document_id IS NULL)",
            name=f"ck_{settings.table_prefix}file_tree_items_type_document_consistency"
        ),
        CheckConstraint(
            "type IN ('file', 'folder')",
            name=f"ck_{settings.table_prefix}file_tree_items_valid_type"
        ),
        
        # Publication system constraints
        CheckConstraint(
            "publication_status IN ('draft', 'review', 'published', 'archived')",
            name=f"ck_{settings.table_prefix}file_tree_items_valid_publication_status"
        ),
        CheckConstraint(
            "approval_status IN ('pending', 'approved', 'rejected')",
            name=f"ck_{settings.table_prefix}file_tree_items_valid_approval_status"
        ),
        CheckConstraint(
            "priority IS NULL OR priority IN ('low', 'medium', 'high')",
            name=f"ck_{settings.table_prefix}file_tree_items_valid_priority"
        ),
        
        # Business rules
        CheckConstraint(
            "(publication_status != 'published') OR (approval_status = 'approved')",
            name=f"ck_{settings.table_prefix}file_tree_items_published_must_be_approved"
        ),
        CheckConstraint(
            "(published_at IS NULL) = (publication_status != 'published')",
            name=f"ck_{settings.table_prefix}file_tree_items_published_timestamp_consistency"
        ),
        
        # Performance indexes
        Index(f"ix_{settings.table_prefix}file_tree_items_publication_status", "project_id", "publication_status"),
        Index(f"ix_{settings.table_prefix}file_tree_items_wiki_pages", "project_id", "is_wiki_page"),
        Index(f"ix_{settings.table_prefix}file_tree_items_approval", "project_id", "approval_status"),
    )
```

### Supporting Tables

```python
class ProjectTag(Base):
    """Project-wide tag management with rich metadata"""
    __tablename__ = f"{settings.table_prefix}project_tags"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey(...), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Rich tag metadata
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # emoji or icon name
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # hex color
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # character, location, plot, etc.
    
    # Usage analytics
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Settings
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # system vs user tags
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None), onupdate=lambda: datetime.now(UTC).replace(tzinfo=None))
    
    # Constraints
    __table_args__ = (
        Index(f"ix_{settings.table_prefix}project_tags_project_name", "project_id", "name", unique=True),
        Index(f"ix_{settings.table_prefix}project_tags_usage", "project_id", "usage_count"),
        Index(f"ix_{settings.table_prefix}project_tags_category", "project_id", "category"),
    )

class Wiki(Base):
    """Wiki collection management"""
    __tablename__ = f"{settings.table_prefix}wikis"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey(...))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Wiki metadata
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    access_level: Mapped[str] = mapped_column(String(20), nullable=False, default="project")  # project, public, private
    
    created_at: Mapped[datetime] = mapped_column(DateTime, ...)
    updated_at: Mapped[datetime] = mapped_column(DateTime, ...)

class PublicationHistory(Base):
    """Audit trail for publication events"""
    __tablename__ = f"{settings.table_prefix}publication_history"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    file_tree_item_id: Mapped[str] = mapped_column(String(36), ForeignKey(...))
    
    # Event details
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)  # published, unpublished, reviewed
    old_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Actor information
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, ...)
```

## API Design

### Request/Response Schemas

```python
# Publication management requests
class UpdatePublicationStatusRequest(BaseSchema):
    """Request to update publication status"""
    publication_status: str  # draft, review, published, archived
    notes: Optional[str] = None

class BulkPublicationRequest(BaseSchema):
    """Request for bulk publication operations"""
    file_ids: List[str]
    action: str  # publish, unpublish, move_to_review, archive
    notes: Optional[str] = None

class CreateWikiRequest(BaseSchema):
    """Request to create a new wiki collection"""
    name: str
    description: Optional[str] = None
    is_public: bool = False
    initial_pages: List[str] = Field(default_factory=list)

class WikiMembershipRequest(BaseSchema):
    """Request to add/remove files from wiki"""
    file_ids: List[str]
    wiki_id: str
    action: str  # add, remove

# Tag management schemas
class ProjectTagResponse(BaseModel):
    """Project tag with rich metadata"""
    id: str
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    usage_count: int = 0
    last_used: Optional[datetime] = None
    is_system: bool = False
    is_archived: bool = False
    created_at: datetime
    updated_at: datetime

class CreateTagRequest(BaseSchema):
    """Request to create a new project tag"""
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class UpdateTagRequest(BaseSchema):
    """Request to update an existing tag"""
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_archived: Optional[bool] = None

# Enhanced metadata responses
class FileTreeItemMetadata(BaseModel):
    """System metadata for file tree items"""
    publication_status: str
    approval_status: str
    is_wiki_page: bool
    wiki_id: Optional[str] = None
    collection_ids: List[str] = Field(default_factory=list)
    priority: Optional[str] = None
    category: Optional[str] = None
    
    # Audit trail
    published_at: Optional[datetime] = None
    published_by: Optional[str] = None
    last_reviewed_at: Optional[datetime] = None
    last_reviewed_by: Optional[str] = None
    
    # Analytics
    view_count: int = 0
    last_accessed_at: Optional[datetime] = None

class EnhancedFileTreeItem(BaseModel):
    """File tree item with publication metadata"""
    # Standard fields
    id: str
    name: str
    type: str
    tag_ids: List[str] = Field(default_factory=list)  # References to ProjectTag IDs
    tags: List[ProjectTagResponse] = Field(default_factory=list)  # Populated tag objects
    description: Optional[str] = None
    color: Optional[str] = None
    
    # System metadata
    metadata: FileTreeItemMetadata
    
    # Hierarchy
    parent_id: Optional[str] = None
    children: Optional[List["EnhancedFileTreeItem"]] = None
```

### API Endpoints

```python
# Tag management endpoints
GET /api/v1/projects/{project_id}/tags
POST /api/v1/projects/{project_id}/tags
GET /api/v1/projects/{project_id}/tags/{tag_id}
PUT /api/v1/projects/{project_id}/tags/{tag_id}
DELETE /api/v1/projects/{project_id}/tags/{tag_id}

# File tree tag assignment
PUT /api/v1/projects/{project_id}/files/{file_id}/tags
POST /api/v1/projects/{project_id}/files/{file_id}/tags/{tag_id}
DELETE /api/v1/projects/{project_id}/files/{file_id}/tags/{tag_id}

# Publication workflow endpoints
POST /api/v1/projects/{project_id}/files/{file_id}/publish
POST /api/v1/projects/{project_id}/files/{file_id}/unpublish
POST /api/v1/projects/{project_id}/files/{file_id}/review
POST /api/v1/projects/{project_id}/files/bulk-publish

# Wiki management
POST /api/v1/projects/{project_id}/wikis
GET /api/v1/projects/{project_id}/wikis
PUT /api/v1/projects/{project_id}/wikis/{wiki_id}
DELETE /api/v1/projects/{project_id}/wikis/{wiki_id}

POST /api/v1/projects/{project_id}/wikis/{wiki_id}/pages
DELETE /api/v1/projects/{project_id}/wikis/{wiki_id}/pages/{file_id}

# Analytics and reporting
GET /api/v1/projects/{project_id}/publication-stats
GET /api/v1/projects/{project_id}/files/{file_id}/publication-history
GET /api/v1/projects/{project_id}/files/published
GET /api/v1/projects/{project_id}/files/pending-review
GET /api/v1/projects/{project_id}/tags/analytics
```

## Frontend Integration

### UI Component Patterns

**File Explorer Integration:**
```typescript
// Enhanced file tree display with publication status
<FileTreeItem 
  item={item}
  showPublicationStatus={true}
  showWikiBadges={true}
  onPublicationAction={handlePublicationAction}
/>

// Status badges
[📊 Published] [✏️ Draft] [📖 Wiki] [🔄 Review]
```

**Metadata Editor Enhancements:**
```typescript
interface PublicationMetadata {
  // System fields (role-protected)
  publicationStatus: 'draft' | 'review' | 'published' | 'archived';
  approvalStatus: 'pending' | 'approved' | 'rejected';
  isWikiPage: boolean;
  wikiId?: string;
  priority?: 'low' | 'medium' | 'high';
  category?: string;
  
  // Audit trail (read-only)
  publishedAt?: string;
  publishedBy?: string;
  lastReviewedAt?: string;
  lastReviewedBy?: string;
}

// Permission-aware editing
const canEditPublication = user.role === 'editor' || user.role === 'admin';
const canApproveDrafts = user.role === 'admin';
```

**Publication Workflow UI:**
```typescript
// Publication action buttons
<PublicationActions
  currentStatus={item.metadata.publicationStatus}
  userPermissions={userPermissions}
  onPublish={handlePublish}
  onUnpublish={handleUnpublish}
  onRequestReview={handleRequestReview}
  onApprove={handleApprove}
  onReject={handleReject}
/>

// Bulk operations
<BulkPublicationPanel
  selectedFiles={selectedFiles}
  onBulkPublish={handleBulkPublish}
  onBulkArchive={handleBulkArchive}
  onBulkWikiAdd={handleBulkWikiAdd}
/>
```

### State Management

```typescript
// Enhanced query hooks
export function useFileTreeWithPublication(projectId: string) {
  return useQuery({
    queryKey: ['fileTree', projectId, 'withPublication'],
    queryFn: () => fileTreeService.getWithPublication(projectId),
  });
}

export function usePublicationMutation() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ fileId, action, notes }: PublicationActionRequest) =>
      publicationService.updateStatus(fileId, action, notes),
    onSuccess: (data, { fileId }) => {
      // Invalidate related queries
      queryClient.invalidateQueries(['fileTree']);
      queryClient.invalidateQueries(['publicationHistory', fileId]);
    },
  });
}

// Wiki management
export function useWikiMutation() {
  return useMutation({
    mutationFn: (request: WikiMembershipRequest) =>
      wikiService.updateMembership(request),
    onSuccess: () => {
      queryClient.invalidateQueries(['wikis']);
      queryClient.invalidateQueries(['fileTree']);
    },
  });
}
```

## Implementation Phases

### Phase 1: Database Foundation
- [ ] Extend FileTreeItem model with publication fields
- [ ] Create database migration scripts
- [ ] Add validation constraints and indexes
- [ ] Update existing seed data with default values

### Phase 2: Backend API
- [ ] Create publication service layer
- [ ] Implement publication workflow endpoints
- [ ] Add permission validation middleware
- [ ] Create audit trail logging
- [ ] Update existing file tree endpoints to include metadata

### Phase 3: Frontend Integration
- [ ] Update TypeScript interfaces for publication metadata
- [ ] Create publication status components and badges
- [ ] Implement metadata editor with role-based permissions
- [ ] Add publication action buttons and workflows
- [ ] Update file explorer to show publication status

### Phase 4: Wiki System
- [ ] Implement wiki collection management
- [ ] Create wiki-specific UI components
- [ ] Add wiki membership controls
- [ ] Implement wiki-based filtering and navigation

### Phase 5: Advanced Features
- [ ] Bulk publication operations
- [ ] Publication history and audit trails
- [ ] Analytics dashboard for publication metrics
- [ ] External publishing integrations (future)

## Technical Considerations

### Performance Optimization

**Query Patterns:**
```sql
-- Fast publication status queries with indexes
SELECT * FROM file_tree_items 
WHERE project_id = ? AND publication_status = 'published'
ORDER BY published_at DESC;

-- Wiki page queries
SELECT * FROM file_tree_items 
WHERE project_id = ? AND is_wiki_page = true;

-- Tag-based queries using the new ProjectTag table
SELECT f.* FROM file_tree_items f
JOIN project_tags t ON t.project_id = f.project_id
WHERE f.project_id = ? 
AND f.tag_ids @> ARRAY[t.id]::text[]
AND t.name = 'character';

-- File tree with populated tags (efficient join)
SELECT f.*, 
       array_agg(t.name) as tag_names,
       array_agg(to_jsonb(t)) as tag_objects
FROM file_tree_items f
LEFT JOIN project_tags t ON t.id = ANY(f.tag_ids::text[])
WHERE f.project_id = ?
GROUP BY f.id;

-- Most used tags in project
SELECT * FROM project_tags 
WHERE project_id = ? AND NOT is_archived
ORDER BY usage_count DESC, name ASC;

-- Combined system status and tag filtering
SELECT f.* FROM file_tree_items f
WHERE f.project_id = ? 
AND f.publication_status = 'published'
AND f.tag_ids && ARRAY[?, ?, ?]::text[];  -- ANY of these tag IDs
```

**Caching Strategy:**
- Cache publication status counts per project
- Cache wiki membership for navigation
- Invalidate on status changes and membership updates

### Security and Permissions

**Role-Based Access:**
- **Viewers**: Can see published content, no edit permissions
- **Writers**: Can create drafts, edit own content, request review
- **Editors**: Can publish content, manage wiki collections
- **Admins**: Full publication workflow control, audit access

**API Security:**
```python
@require_permission("publish_content")
async def publish_file(file_id: str, user: AuthenticatedUser):
    # Validate business rules
    # Log publication event
    # Update status with audit trail
```

### Migration Strategy

**Database Migration:**
```sql
-- Add new columns with safe defaults
ALTER TABLE file_tree_items 
ADD COLUMN publication_status VARCHAR(20) DEFAULT 'draft' NOT NULL,
ADD COLUMN approval_status VARCHAR(20) DEFAULT 'pending' NOT NULL,
ADD COLUMN is_wiki_page BOOLEAN DEFAULT false NOT NULL;

-- Add constraints after data population
ALTER TABLE file_tree_items 
ADD CONSTRAINT ck_valid_publication_status 
CHECK (publication_status IN ('draft', 'review', 'published', 'archived'));
```

**Data Migration:**
- Set all existing files to 'draft' status initially
- Preserve existing tags and user metadata
- Create migration script for any legacy publication indicators

## Future Enhancements

### External Publishing
- Export to static site generators (Hugo, Jekyll, Gatsby)
- WordPress integration for blog publishing
- Medium/Substack publishing workflows
- PDF/ePub generation for published collections

### Advanced Workflows
- Multi-stage review processes with reviewer assignments
- Scheduled publishing with future publish dates
- Content approval workflows with multiple stakeholders
- Integration with external review tools

### Analytics and Insights
- Publication performance metrics
- Reader engagement tracking (for public wikis)
- Content lifecycle analytics
- Collaboration activity monitoring

---

## Related Documentation

- **🏗️ Database Models**: See `backend/src/database/models.py` for current schema
- **🔗 API Contracts**: [`/_docs/api/contracts.md`](../api/contracts.md) - Frontend-backend interfaces
- **🎨 Frontend Components**: [`/frontend/CLAUDE-frontend.md`](../../frontend/CLAUDE-frontend.md) - UI patterns
- **⚙️ Backend Architecture**: [`/_docs/high-level/4-backend.md`](../high-level/4-backend.md) - System design

This publication system will provide a robust foundation for managing content workflows while maintaining the separation between system state and user-defined organization through tags.