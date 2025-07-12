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

from src.database.models import Project, Document, FileTreeItem
from src.database.connection import get_session_context
from src.database.interfaces import ProjectRepository, DocumentRepository, FileTreeRepository

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
                tags=project_data.get("tags", []),
                collaborators=project_data.get("collaborators", []),
                settings=project_data.get("settings", {}),
            )
            session.add(project)
            await session.flush()  # Get the ID
            await session.refresh(project)
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
            )
            return list(result.scalars().all())


class DatabaseDocumentRepository(DocumentRepository):
    """Database-backed document repository using SQLAlchemy"""
    
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        async with get_session_context() as session:
            result = await session.execute(
                select(Document).where(Document.id == document_id)
            )
            return result.scalar_one_or_none()
    
    async def get_by_project_id(self, project_id: str) -> List[Document]:
        async with get_session_context() as session:
            result = await session.execute(
                select(Document).where(Document.project_id == project_id)
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
                tags=document_data.get("tags", []),
                word_count=document_data.get("word_count", 0),
                version=document_data.get("version", "1.0.0"),
                is_locked=document_data.get("is_locked", False),
                locked_by=document_data.get("locked_by"),
                file_tree_id=document_data.get("file_tree_id"),
            )
            session.add(document)
            await session.flush()
            await session.refresh(document)
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
    
    async def get_by_project_id(self, project_id: str) -> List[FileTreeItem]:
        async with get_session_context() as session:
            result = await session.execute(
                select(FileTreeItem)
                .where(FileTreeItem.project_id == project_id)
                .options(selectinload(FileTreeItem.children))
                .order_by(FileTreeItem.path)
            )
            return list(result.scalars().all())
    
    async def create(self, item_data: Dict[str, Any]) -> FileTreeItem:
        async with get_session_context() as session:
            item = FileTreeItem(
                id=item_data.get("id", str(uuid.uuid4())),
                project_id=item_data["project_id"],
                name=item_data["name"],
                type=item_data["type"],
                path=item_data["path"],
                parent_id=item_data.get("parent_id"),
                document_id=item_data.get("document_id"),
                icon=item_data.get("icon"),
                tags=item_data.get("tags", []),
                word_count=item_data.get("word_count"),
            )
            session.add(item)
            await session.flush()
            await session.refresh(item)
            return item
    
    async def update(self, item_id: str, updates: Dict[str, Any]) -> Optional[FileTreeItem]:
        async with get_session_context() as session:
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
            tags=project_data.get("tags", []),
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
            tags=document_data.get("tags", []),
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
    
    async def get_by_project_id(self, project_id: str) -> List[FileTreeItem]:
        return [item for item in self._items.values() if item.project_id == project_id]
    
    async def create(self, item_data: Dict[str, Any]) -> FileTreeItem:
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
            tags=item_data.get("tags", []),
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