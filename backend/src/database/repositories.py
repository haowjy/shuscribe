# backend/src/database/repositories.py
"""
Repository implementations for database and memory backends
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Project, Document, FileTreeItem, Tag
from src.database.connection import get_session_context
from src.database.interfaces import ProjectRepository, DocumentRepository, FileTreeRepository
from src.database.interfaces.tag_repository import TagRepository

logger = logging.getLogger(__name__)


# ============================================================================
# Database Repository Implementations
# ============================================================================

class DatabaseProjectRepository(ProjectRepository):
    """Database-backed project repository using SQLAlchemy"""
    
    async def get_by_id(self, project_id: str) -> Optional[Project]:
        async with get_session_context() as session:
            result = await session.execute(
                select(Project).where(Project.id == project_id)
                .options(selectinload(Project.tags))
            )
            return result.scalar_one_or_none()
    
    async def create(self, project_data: Dict[str, Any]) -> Project:
        async with get_session_context() as session:
            project = Project(
                id=project_data.get("id", str(uuid.uuid4())),
                title=project_data["title"],
                description=project_data.get("description", ""),
                word_count=project_data.get("word_count", 0),
                document_count=project_data.get("document_count", 0),
                collaborators=project_data.get("collaborators", []),
                settings=project_data.get("settings", {}),
            )
            session.add(project)
            await session.flush()  # Get the ID - no need to refresh for seeding
            return project
    
    async def update(self, project_id: str, updates: Dict[str, Any]) -> Optional[Project]:
        async with get_session_context() as session:
            # Add updated_at timestamp
            updates["updated_at"] = datetime.now(UTC).replace(tzinfo=None)
            
            result = await session.execute(
                update(Project).where(Project.id == project_id).values(**updates)
            )
            
            if result.rowcount == 0:
                return None
            
            # Return updated project
            return await self.get_by_id(project_id)
    
    async def delete(self, project_id: str) -> bool:
        async with get_session_context() as session:
            result = await session.execute(
                delete(Project).where(Project.id == project_id)
            )
            return result.rowcount > 0
    
    async def list_all(self) -> List[Project]:
        async with get_session_context() as session:
            result = await session.execute(
                select(Project).order_by(Project.updated_at.desc())
                .options(selectinload(Project.tags))
            )
            return list(result.scalars().all())


class DatabaseDocumentRepository(DocumentRepository):
    """Database-backed document repository using SQLAlchemy"""
    
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        async with get_session_context() as session:
            result = await session.execute(
                select(Document).where(Document.id == document_id)
                .options(selectinload(Document.tags))
            )
            return result.scalar_one_or_none()
    
    async def get_by_project_id(self, project_id: str) -> List[Document]:
        async with get_session_context() as session:
            result = await session.execute(
                select(Document).where(Document.project_id == project_id)
                .options(selectinload(Document.tags))
            )
            return list(result.scalars().all())
    
    async def create(self, document_data: Dict[str, Any]) -> Document:
        async with get_session_context() as session:
            document = Document(
                id=document_data.get("id", str(uuid.uuid4())),
                project_id=document_data["project_id"],
                title=document_data["title"],
                path=document_data["path"],
                content=document_data.get("content", {"type": "doc", "content": []}),
                word_count=document_data.get("word_count", 0),
                version=document_data.get("version", "1.0.0"),
                is_locked=document_data.get("is_locked", False),
                locked_by=document_data.get("locked_by"),
                file_tree_id=document_data.get("file_tree_id"),
            )
            session.add(document)
            await session.flush()
            return document
    
    async def update(self, document_id: str, updates: Dict[str, Any]) -> Optional[Document]:
        async with get_session_context() as session:
            # Add updated_at timestamp
            updates["updated_at"] = datetime.now(UTC).replace(tzinfo=None)
            
            result = await session.execute(
                update(Document).where(Document.id == document_id).values(**updates)
            )
            
            if result.rowcount == 0:
                return None
            
            return await self.get_by_id(document_id)
    
    async def delete(self, document_id: str) -> bool:
        async with get_session_context() as session:
            result = await session.execute(
                delete(Document).where(Document.id == document_id)
            )
            return result.rowcount > 0


class DatabaseFileTreeRepository(FileTreeRepository):
    """Database-backed file tree repository using SQLAlchemy"""
    
    async def _validate_file_tree_constraints(self, session: AsyncSession, item_data: Dict[str, Any], item_id: str = None) -> None:
        """Validate file tree business rules"""
        item_type = item_data.get("type")
        document_id = item_data.get("document_id")
        parent_id = item_data.get("parent_id")
        
        # Validate type-document_id consistency
        if item_type == "file" and not document_id:
            raise ValueError("Files must have a document_id")
        if item_type == "folder" and document_id:
            raise ValueError("Folders cannot have a document_id")
        
        # Validate that parent is not a file (files cannot have children)
        if parent_id:
            parent_result = await session.execute(
                select(FileTreeItem.type).where(FileTreeItem.id == parent_id)
            )
            parent_type = parent_result.scalar_one_or_none()
            if parent_type == "file":
                raise ValueError("Files cannot have children")
        
        # For updates, validate that if changing to file type, item has no children
        if item_id and item_type == "file":
            children_result = await session.execute(
                select(FileTreeItem.id).where(FileTreeItem.parent_id == item_id).limit(1)
            )
            if children_result.scalar_one_or_none():
                raise ValueError("Cannot change item to file type when it has children")
    
    async def get_by_project_id(self, project_id: str) -> List[FileTreeItem]:
        async with get_session_context() as session:
            result = await session.execute(
                select(FileTreeItem)
                .where(FileTreeItem.project_id == project_id)
                .options(selectinload(FileTreeItem.children), selectinload(FileTreeItem.tags))
                .order_by(FileTreeItem.path)
            )
            return list(result.scalars().all())
    
    async def create(self, item_data: Dict[str, Any]) -> FileTreeItem:
        async with get_session_context() as session:
            # Validate constraints before creating
            await self._validate_file_tree_constraints(session, item_data)
            
            item = FileTreeItem(
                id=item_data.get("id", str(uuid.uuid4())),
                project_id=item_data["project_id"],
                name=item_data["name"],
                type=item_data["type"],
                path=item_data["path"],
                parent_id=item_data.get("parent_id"),
                document_id=item_data.get("document_id"),
                icon=item_data.get("icon"),
                word_count=item_data.get("word_count"),
            )
            session.add(item)
            await session.flush()
            return item
    
    async def update(self, item_id: str, updates: Dict[str, Any]) -> Optional[FileTreeItem]:
        async with get_session_context() as session:
            # Validate constraints before updating
            await self._validate_file_tree_constraints(session, updates, item_id)
            
            updates["updated_at"] = datetime.now(UTC).replace(tzinfo=None)
            
            result = await session.execute(
                update(FileTreeItem).where(FileTreeItem.id == item_id).values(**updates)
            )
            
            if result.rowcount == 0:
                return None
            
            # Return updated item
            result = await session.execute(
                select(FileTreeItem).where(FileTreeItem.id == item_id)
            )
            return result.scalar_one_or_none()
    
    async def delete(self, item_id: str) -> bool:
        async with get_session_context() as session:
            result = await session.execute(
                delete(FileTreeItem).where(FileTreeItem.id == item_id)
            )
            return result.rowcount > 0
    
    async def get_by_id(self, item_id: str) -> Optional[FileTreeItem]:
        async with get_session_context() as session:
            result = await session.execute(
                select(FileTreeItem).where(FileTreeItem.id == item_id)
            )
            return result.scalar_one_or_none()
    
    async def assign_tag(self, item_id: str, tag_id: str) -> bool:
        """Assign tag to file tree item using many-to-many relationship"""
        async with get_session_context() as session:
            # Get the file tree item with its current tags
            item = await session.get(FileTreeItem, item_id)
            if not item:
                return False
            
            # Get the tag
            tag = await session.get(Tag, tag_id)
            if not tag:
                return False
            
            # Check if tag is already assigned
            if tag not in item.tags:
                item.tags.append(tag)
                await session.flush()
                return True
            return False
    
    async def unassign_tag(self, item_id: str, tag_id: str) -> bool:
        """Unassign tag from file tree item using many-to-many relationship"""
        async with get_session_context() as session:
            # Get the file tree item with its current tags
            item = await session.get(FileTreeItem, item_id)
            if not item:
                return False
            
            # Get the tag
            tag = await session.get(Tag, tag_id)
            if not tag:
                return False
            
            # Check if tag is assigned and remove it
            if tag in item.tags:
                item.tags.remove(tag)
                await session.flush()
                return True
            return False


# ============================================================================
# Memory Repository Implementations (for testing)
# ============================================================================

class MemoryProjectRepository(ProjectRepository):
    """In-memory project repository for testing"""
    
    def __init__(self):
        self._projects: Dict[str, Project] = {}
    
    async def get_by_id(self, project_id: str) -> Optional[Project]:
        return self._projects.get(project_id)
    
    async def create(self, project_data: Dict[str, Any]) -> Project:
        project_id = project_data.get("id", str(uuid.uuid4()))
        project = Project(
            id=project_id,
            title=project_data["title"],
            description=project_data.get("description", ""),
            word_count=project_data.get("word_count", 0),
            document_count=project_data.get("document_count", 0),
            collaborators=project_data.get("collaborators", []),
            settings=project_data.get("settings", {}),
            created_at=datetime.now(UTC).replace(tzinfo=None),
            updated_at=datetime.now(UTC).replace(tzinfo=None),
        )
        self._projects[project_id] = project
        return project
    
    async def update(self, project_id: str, updates: Dict[str, Any]) -> Optional[Project]:
        project = self._projects.get(project_id)
        if not project:
            return None
        
        for key, value in updates.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        project.updated_at = datetime.now(UTC).replace(tzinfo=None)
        return project
    
    async def delete(self, project_id: str) -> bool:
        if project_id in self._projects:
            del self._projects[project_id]
            return True
        return False
    
    async def list_all(self) -> List[Project]:
        # Return sorted by updated_at descending
        projects = list(self._projects.values())
        return sorted(projects, key=lambda p: p.updated_at, reverse=True)


class MemoryDocumentRepository(DocumentRepository):
    """In-memory document repository for testing"""
    
    def __init__(self):
        self._documents: Dict[str, Document] = {}
    
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        return self._documents.get(document_id)
    
    async def get_by_project_id(self, project_id: str) -> List[Document]:
        return [doc for doc in self._documents.values() if doc.project_id == project_id]
    
    async def create(self, document_data: Dict[str, Any]) -> Document:
        document_id = document_data.get("id", str(uuid.uuid4()))
        document = Document(
            id=document_id,
            project_id=document_data["project_id"],
            title=document_data["title"],
            path=document_data["path"],
            content=document_data.get("content", {"type": "doc", "content": []}),
            word_count=document_data.get("word_count", 0),
            version=document_data.get("version", "1.0.0"),
            is_locked=document_data.get("is_locked", False),
            locked_by=document_data.get("locked_by"),
            file_tree_id=document_data.get("file_tree_id"),
            created_at=datetime.now(UTC).replace(tzinfo=None),
            updated_at=datetime.now(UTC).replace(tzinfo=None),
        )
        self._documents[document_id] = document
        return document
    
    async def update(self, document_id: str, updates: Dict[str, Any]) -> Optional[Document]:
        document = self._documents.get(document_id)
        if not document:
            return None
        
        for key, value in updates.items():
            if hasattr(document, key):
                setattr(document, key, value)
        
        document.updated_at = datetime.now(UTC).replace(tzinfo=None)
        return document
    
    async def delete(self, document_id: str) -> bool:
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False


class MemoryFileTreeRepository(FileTreeRepository):
    """In-memory file tree repository for testing"""
    
    def __init__(self):
        self._items: Dict[str, FileTreeItem] = {}
    
    def _validate_file_tree_constraints(self, item_data: Dict[str, Any], item_id: str = None) -> None:
        """Validate file tree business rules for memory repository"""
        item_type = item_data.get("type")
        document_id = item_data.get("document_id")
        parent_id = item_data.get("parent_id")
        
        # Validate type-document_id consistency
        if item_type == "file" and not document_id:
            raise ValueError("Files must have a document_id")
        if item_type == "folder" and document_id:
            raise ValueError("Folders cannot have a document_id")
        
        # Validate that parent is not a file (files cannot have children)
        if parent_id and parent_id in self._items:
            parent = self._items[parent_id]
            if parent.type == "file":
                raise ValueError("Files cannot have children")
        
        # For updates, validate that if changing to file type, item has no children
        if item_id and item_type == "file":
            has_children = any(item.parent_id == item_id for item in self._items.values())
            if has_children:
                raise ValueError("Cannot change item to file type when it has children")
    
    async def get_by_project_id(self, project_id: str) -> List[FileTreeItem]:
        return [item for item in self._items.values() if item.project_id == project_id]
    
    async def create(self, item_data: Dict[str, Any]) -> FileTreeItem:
        # Validate constraints before creating
        self._validate_file_tree_constraints(item_data)
        
        item_id = item_data.get("id", str(uuid.uuid4()))
        item = FileTreeItem(
            id=item_id,
            project_id=item_data["project_id"],
            name=item_data["name"],
            type=item_data["type"],
            path=item_data["path"],
            parent_id=item_data.get("parent_id"),
            document_id=item_data.get("document_id"),
            icon=item_data.get("icon"),
            word_count=item_data.get("word_count"),
            created_at=datetime.now(UTC).replace(tzinfo=None),
            updated_at=datetime.now(UTC).replace(tzinfo=None),
        )
        self._items[item_id] = item
        return item
    
    async def update(self, item_id: str, updates: Dict[str, Any]) -> Optional[FileTreeItem]:
        item = self._items.get(item_id)
        if not item:
            return None
        
        # Validate constraints before updating
        self._validate_file_tree_constraints(updates, item_id)
        
        for key, value in updates.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        item.updated_at = datetime.now(UTC).replace(tzinfo=None)
        return item
    
    async def delete(self, item_id: str) -> bool:
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False
    
    async def get_by_id(self, item_id: str) -> Optional[FileTreeItem]:
        return self._items.get(item_id)
    
    async def assign_tag(self, item_id: str, tag_id: str) -> bool:
        """Assign tag to file tree item (simplified for memory repository)"""
        # For memory implementation, we simulate the relationship
        # In a real system with relationships, this would be handled by SQLAlchemy
        item = self._items.get(item_id)
        if item:
            # Simulate assignment - in real implementation this would use relationships
            # For now, we'll just return True to indicate successful assignment
            return True
        return False
    
    async def unassign_tag(self, item_id: str, tag_id: str) -> bool:
        """Unassign tag from file tree item (simplified for memory repository)"""
        item = self._items.get(item_id)
        if item:
            # Simulate unassignment - in real implementation this would use relationships
            # For now, we'll just return True to indicate successful unassignment
            return True
        return False


class DatabaseTagRepository(TagRepository):
    """Database-backed tag repository using SQLAlchemy"""
    
    async def get_by_id(self, tag_id: str) -> Optional[Tag]:
        async with get_session_context() as session:
            result = await session.execute(
                select(Tag).where(Tag.id == tag_id)
            )
            return result.scalar_one_or_none()
    
    async def get_global_tags(self, include_archived: bool = False) -> List[Tag]:
        async with get_session_context() as session:
            query = select(Tag).where(Tag.is_global == True)
            if not include_archived:
                query = query.where(Tag.is_archived == False)
            result = await session.execute(query.order_by(Tag.name))
            return list(result.scalars().all())
    
    async def get_user_tags(self, user_id: str, include_archived: bool = False) -> List[Tag]:
        async with get_session_context() as session:
            query = select(Tag).where(Tag.user_id == user_id)
            if not include_archived:
                query = query.where(Tag.is_archived == False)
            result = await session.execute(query.order_by(Tag.name))
            return list(result.scalars().all())
    
    async def get_by_project_id(self, project_id: str, include_archived: bool = False) -> List[Tag]:
        async with get_session_context() as session:
            query = select(Tag).where(Tag.project_id == project_id)
            if not include_archived:
                query = query.where(Tag.is_archived == False)
            result = await session.execute(query.order_by(Tag.name))
            return list(result.scalars().all())
    
    async def get_by_name(self, name: str, user_id: Optional[str] = None) -> Optional[Tag]:
        async with get_session_context() as session:
            if user_id is None:
                # Search global tags
                result = await session.execute(
                    select(Tag).where(Tag.name == name, Tag.is_global == True)
                )
            else:
                # Search user's private tags
                result = await session.execute(
                    select(Tag).where(Tag.name == name, Tag.user_id == user_id)
                )
            return result.scalar_one_or_none()
    
    async def create(self, tag_data: Dict[str, Any]) -> Tag:
        async with get_session_context() as session:
            tag = Tag(
                id=tag_data.get("id", str(uuid.uuid4())),
                name=tag_data["name"],
                icon=tag_data.get("icon"),
                color=tag_data.get("color"),
                description=tag_data.get("description"),
                category=tag_data.get("category"),
                is_global=tag_data.get("is_global", False),
                user_id=tag_data.get("user_id"),
                project_id=tag_data.get("project_id"),
                usage_count=tag_data.get("usage_count", 0),
                is_system=tag_data.get("is_system", False),
                is_archived=tag_data.get("is_archived", False),
            )
            session.add(tag)
            await session.flush()
            return tag
    
    async def update(self, tag_id: str, updates: Dict[str, Any]) -> Optional[Tag]:
        async with get_session_context() as session:
            # Update using SQL for better performance
            updates["updated_at"] = datetime.now(UTC).replace(tzinfo=None)
            result = await session.execute(
                update(Tag)
                .where(Tag.id == tag_id)
                .values(**updates)
                .returning(Tag)
            )
            updated_tag = result.scalar_one_or_none()
            if updated_tag:
                await session.refresh(updated_tag)
            return updated_tag
    
    async def delete(self, tag_id: str) -> bool:
        async with get_session_context() as session:
            result = await session.execute(
                delete(Tag).where(Tag.id == tag_id)
            )
            return result.rowcount > 0
    
    async def archive(self, tag_id: str) -> Optional[Tag]:
        return await self.update(tag_id, {"is_archived": True})
    
    async def unarchive(self, tag_id: str) -> Optional[Tag]:
        return await self.update(tag_id, {"is_archived": False})
    
    async def increment_usage(self, tag_id: str) -> Optional[Tag]:
        async with get_session_context() as session:
            result = await session.execute(
                update(Tag)
                .where(Tag.id == tag_id)
                .values(
                    usage_count=Tag.usage_count + 1,
                    updated_at=datetime.now(UTC).replace(tzinfo=None)
                )
                .returning(Tag)
            )
            updated_tag = result.scalar_one_or_none()
            if updated_tag:
                await session.refresh(updated_tag)
            return updated_tag
    
    async def decrement_usage(self, tag_id: str) -> Optional[Tag]:
        async with get_session_context() as session:
            result = await session.execute(
                update(Tag)
                .where(Tag.id == tag_id)
                .values(
                    usage_count=Tag.usage_count - 1,
                    updated_at=datetime.now(UTC).replace(tzinfo=None)
                )
                .returning(Tag)
            )
            updated_tag = result.scalar_one_or_none()
            if updated_tag:
                await session.refresh(updated_tag)
            return updated_tag
    
    async def get_by_category(self, category: str, user_id: Optional[str] = None) -> List[Tag]:
        async with get_session_context() as session:
            if user_id is None:
                # Get global tags by category
                result = await session.execute(
                    select(Tag)
                    .where(Tag.is_global == True, Tag.category == category, Tag.is_archived == False)
                    .order_by(Tag.name)
                )
            else:
                # Get global and user's private tags by category
                result = await session.execute(
                    select(Tag)
                    .where(
                        Tag.category == category, 
                        Tag.is_archived == False,
                        (Tag.is_global == True) | (Tag.user_id == user_id)
                    )
                    .order_by(Tag.name)
                )
            return list(result.scalars().all())
    
    async def get_system_tags(self) -> List[Tag]:
        async with get_session_context() as session:
            result = await session.execute(
                select(Tag)
                .where(Tag.is_system == True, Tag.is_global == True, Tag.is_archived == False)
                .order_by(Tag.name)
            )
            return list(result.scalars().all())
    
    async def search_tags(self, query: str, user_id: Optional[str] = None, limit: int = 20) -> List[Tag]:
        async with get_session_context() as session:
            if user_id is None:
                # Search only global tags
                result = await session.execute(
                    select(Tag)
                    .where(
                        Tag.is_global == True,
                        Tag.name.ilike(f"%{query}%"),
                        Tag.is_archived == False
                    )
                    .order_by(Tag.usage_count.desc(), Tag.name)
                    .limit(limit)
                )
            else:
                # Search global and user's private tags
                result = await session.execute(
                    select(Tag)
                    .where(
                        Tag.name.ilike(f"%{query}%"),
                        Tag.is_archived == False,
                        (Tag.is_global == True) | (Tag.user_id == user_id)
                    )
                    .order_by(Tag.usage_count.desc(), Tag.name)
                    .limit(limit)
                )
            return list(result.scalars().all())


class MemoryTagRepository(TagRepository):
    """In-memory tag repository for testing"""
    
    def __init__(self):
        self._tags: Dict[str, Tag] = {}
    
    async def get_by_id(self, tag_id: str) -> Optional[Tag]:
        return self._tags.get(tag_id)
    
    async def get_global_tags(self, include_archived: bool = False) -> List[Tag]:
        tags = [tag for tag in self._tags.values() if tag.is_global]
        if not include_archived:
            tags = [tag for tag in tags if not tag.is_archived]
        return sorted(tags, key=lambda t: t.name)
    
    async def get_user_tags(self, user_id: str, include_archived: bool = False) -> List[Tag]:
        tags = [tag for tag in self._tags.values() if tag.user_id == user_id]
        if not include_archived:
            tags = [tag for tag in tags if not tag.is_archived]
        return sorted(tags, key=lambda t: t.name)
    
    async def get_by_project_id(self, project_id: str, include_archived: bool = False) -> List[Tag]:
        tags = [tag for tag in self._tags.values() if tag.project_id == project_id]
        if not include_archived:
            tags = [tag for tag in tags if not tag.is_archived]
        return sorted(tags, key=lambda t: t.name)
    
    async def get_by_name(self, name: str, user_id: Optional[str] = None) -> Optional[Tag]:
        for tag in self._tags.values():
            if user_id is None:
                # Search global tags
                if tag.name == name and tag.is_global:
                    return tag
            else:
                # Search user's private tags
                if tag.name == name and tag.user_id == user_id:
                    return tag
        return None
    
    async def create(self, tag_data: Dict[str, Any]) -> Tag:
        tag_id = tag_data.get("id", str(uuid.uuid4()))
        tag = Tag(
            id=tag_id,
            name=tag_data["name"],
            icon=tag_data.get("icon"),
            color=tag_data.get("color"),
            description=tag_data.get("description"),
            category=tag_data.get("category"),
            is_global=tag_data.get("is_global", False),
            user_id=tag_data.get("user_id"),
            usage_count=tag_data.get("usage_count", 0),
            is_system=tag_data.get("is_system", False),
            is_archived=tag_data.get("is_archived", False),
            created_at=datetime.now(UTC).replace(tzinfo=None),
            updated_at=datetime.now(UTC).replace(tzinfo=None),
        )
        self._tags[tag_id] = tag
        return tag
    
    async def update(self, tag_id: str, updates: Dict[str, Any]) -> Optional[Tag]:
        if tag_id not in self._tags:
            return None
        
        tag = self._tags[tag_id]
        for key, value in updates.items():
            if hasattr(tag, key):
                setattr(tag, key, value)
        
        tag.updated_at = datetime.now(UTC).replace(tzinfo=None)
        return tag
    
    async def delete(self, tag_id: str) -> bool:
        if tag_id in self._tags:
            del self._tags[tag_id]
            return True
        return False
    
    async def archive(self, tag_id: str) -> Optional[Tag]:
        return await self.update(tag_id, {"is_archived": True})
    
    async def unarchive(self, tag_id: str) -> Optional[Tag]:
        return await self.update(tag_id, {"is_archived": False})
    
    async def increment_usage(self, tag_id: str) -> Optional[Tag]:
        if tag_id in self._tags:
            tag = self._tags[tag_id]
            tag.usage_count += 1
            tag.updated_at = datetime.now(UTC).replace(tzinfo=None)
            return tag
        return None
    
    async def decrement_usage(self, tag_id: str) -> Optional[Tag]:
        if tag_id in self._tags:
            tag = self._tags[tag_id]
            tag.usage_count = max(0, tag.usage_count - 1)
            tag.updated_at = datetime.now(UTC).replace(tzinfo=None)
            return tag
        return None
    
    async def get_by_category(self, category: str, user_id: Optional[str] = None) -> List[Tag]:
        if user_id is None:
            # Get global tags by category
            tags = [
                tag for tag in self._tags.values()
                if tag.is_global and tag.category == category and not tag.is_archived
            ]
        else:
            # Get global and user's private tags by category
            tags = [
                tag for tag in self._tags.values()
                if tag.category == category and not tag.is_archived
                and (tag.is_global or tag.user_id == user_id)
            ]
        return sorted(tags, key=lambda t: t.name)
    
    async def get_system_tags(self) -> List[Tag]:
        tags = [
            tag for tag in self._tags.values()
            if tag.is_system and tag.is_global and not tag.is_archived
        ]
        return sorted(tags, key=lambda t: t.name)
    
    async def search_tags(self, query: str, user_id: Optional[str] = None, limit: int = 20) -> List[Tag]:
        if user_id is None:
            # Search only global tags
            tags = [
                tag for tag in self._tags.values()
                if tag.is_global
                and query.lower() in tag.name.lower()
                and not tag.is_archived
            ]
        else:
            # Search global and user's private tags
            tags = [
                tag for tag in self._tags.values()
                if query.lower() in tag.name.lower()
                and not tag.is_archived
                and (tag.is_global or tag.user_id == user_id)
            ]
        # Sort by usage count desc, then name
        tags.sort(key=lambda t: (-t.usage_count, t.name))
        return tags[:limit]