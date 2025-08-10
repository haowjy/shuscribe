# backend/src/database/sqlalchemy/repositories/file_tree_repository.py
"""
SQLAlchemy FileTreeRepository implementation
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.interfaces import FileTreeRepository
from src.database.interfaces.models import FileTreeItem as DomainFileTreeItem
from src.database.connection import get_session_context
from src.database.sqlalchemy.models import FileTreeItem as SQLAlchemyFileTreeItem, Tag as SQLAlchemyTag
from src.database.sqlalchemy.mappers import FileTreeItemMapper
from src.database.utils import TagResolver

logger = logging.getLogger(__name__)


class DatabaseFileTreeRepository(FileTreeRepository):
    """Database-backed file tree repository using SQLAlchemy"""
    
    async def _validate_file_tree_constraints(self, session: AsyncSession, item_data: Dict[str, Any], item_id: Optional[str] = None) -> None:
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
                select(SQLAlchemyFileTreeItem.type).where(SQLAlchemyFileTreeItem.id == parent_id)
            )
            parent_type = parent_result.scalar_one_or_none()
            if parent_type == "file":
                raise ValueError("Files cannot have children")
        
        # For updates, validate that if changing to file type, item has no children
        if item_id and item_type == "file":
            children_result = await session.execute(
                select(SQLAlchemyFileTreeItem.id).where(SQLAlchemyFileTreeItem.parent_id == item_id).limit(1)
            )
            if children_result.scalar_one_or_none():
                raise ValueError("Cannot change item to file type when it has children")
    
    async def get_by_project_id(self, project_id: str) -> List[DomainFileTreeItem]:
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyFileTreeItem)
                .where(SQLAlchemyFileTreeItem.project_id == project_id)
                .options(selectinload(SQLAlchemyFileTreeItem.children), selectinload(SQLAlchemyFileTreeItem.tags))
                .order_by(SQLAlchemyFileTreeItem.path)
            )
            sqlalchemy_items = result.scalars().all()
            
            return [FileTreeItemMapper.to_domain(item) for item in sqlalchemy_items]
    
    async def create(self, item_data: Dict[str, Any]) -> DomainFileTreeItem:
        async with get_session_context() as session:
            # Validate constraints before creating
            await self._validate_file_tree_constraints(session, item_data)
            
            # Create domain file tree item first to validate data
            domain_item = FileTreeItemMapper.from_dict({
                "id": item_data.get("id", str(uuid.uuid4())),
                "project_id": item_data["project_id"],
                "name": item_data["name"],
                "type": item_data["type"],
                "path": item_data["path"],
                "parent_id": item_data.get("parent_id"),
                "document_id": item_data.get("document_id"),
                "icon": item_data.get("icon"),
                "word_count": item_data.get("word_count"),
                "tags": item_data.get("tags", []),
            })
            
            # Convert to SQLAlchemy model (without tags first)
            sqlalchemy_item = FileTreeItemMapper.to_sqlalchemy(domain_item)
            
            # Handle tag relationships if provided
            if item_data.get("tags"):
                # Resolve tag names to SQLAlchemy Tag objects
                resolved_tags = await TagResolver.resolve_tags(
                    session,
                    item_data["tags"],
                    project_id=item_data["project_id"],
                    user_id=item_data.get("created_by")
                )
                # Assign the resolved tags to the item
                sqlalchemy_item.tags = resolved_tags
            
            # Add to session and flush to get the item saved
            session.add(sqlalchemy_item)
            await session.flush()
            
            # Re-fetch with tags eagerly loaded to avoid lazy loading issues
            result = await session.execute(
                select(SQLAlchemyFileTreeItem)
                .where(SQLAlchemyFileTreeItem.id == sqlalchemy_item.id)
                .options(selectinload(SQLAlchemyFileTreeItem.tags))
            )
            refreshed_item = result.scalar_one()
            
            # Return domain item with proper tag relationships
            return FileTreeItemMapper.to_domain(refreshed_item)
    
    async def update(self, item_id: str, updates: Dict[str, Any]) -> Optional[DomainFileTreeItem]:
        async with get_session_context() as session:
            # Validate constraints before updating
            await self._validate_file_tree_constraints(session, updates, item_id)
            
            # Separate tag updates from column updates
            tag_updates = updates.pop("tags", None)
            
            # Add updated_at timestamp
            updates["updated_at"] = datetime.now(UTC).replace(tzinfo=None)
            
            # Update columns (excluding tags)
            if updates:
                result = await session.execute(
                    update(SQLAlchemyFileTreeItem).where(SQLAlchemyFileTreeItem.id == item_id).values(**updates)
                )
                
                if result.rowcount == 0:
                    return None
            
            # Handle tag updates separately if provided
            if tag_updates is not None:
                # Get the item to update its tags
                item_result = await session.execute(
                    select(SQLAlchemyFileTreeItem)
                    .where(SQLAlchemyFileTreeItem.id == item_id)
                    .options(selectinload(SQLAlchemyFileTreeItem.tags))
                )
                item = item_result.scalar_one_or_none()
                
                if not item:
                    return None
                
                # Resolve new tags
                resolved_tags = await TagResolver.resolve_tags(
                    session,
                    tag_updates,
                    project_id=item.project_id,
                    user_id=None  # FileTreeItems don't have direct user ownership
                )
                
                # Update the tags relationship
                item.tags = resolved_tags
                await session.flush()
            
            return await self.get_by_id(item_id)
    
    async def delete(self, item_id: str) -> bool:
        async with get_session_context() as session:
            result = await session.execute(
                delete(SQLAlchemyFileTreeItem).where(SQLAlchemyFileTreeItem.id == item_id)
            )
            return result.rowcount > 0
    
    async def get_by_id(self, item_id: str) -> Optional[DomainFileTreeItem]:
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyFileTreeItem)
                .where(SQLAlchemyFileTreeItem.id == item_id)
                .options(selectinload(SQLAlchemyFileTreeItem.tags))
            )
            sqlalchemy_item = result.scalar_one_or_none()
            
            if sqlalchemy_item:
                return FileTreeItemMapper.to_domain(sqlalchemy_item)
            return None
    
    async def assign_tag(self, item_id: str, tag_id: str) -> bool:
        """Assign tag to file tree item using many-to-many relationship"""
        async with get_session_context() as session:
            # Get the file tree item with its current tags
            item = await session.get(SQLAlchemyFileTreeItem, item_id)
            if not item:
                return False
            
            # Get the tag
            tag = await session.get(SQLAlchemyTag, tag_id)
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
            item = await session.get(SQLAlchemyFileTreeItem, item_id)
            if not item:
                return False
            
            # Get the tag
            tag = await session.get(SQLAlchemyTag, tag_id)
            if not tag:
                return False
            
            # Check if tag is assigned and remove it
            if tag in item.tags:
                item.tags.remove(tag)
                await session.flush()
                return True
            return False
    
    async def get_by_path(self, project_id: str, path: str) -> Optional[DomainFileTreeItem]:
        """Get file tree item by project ID and path"""
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyFileTreeItem)
                .where(SQLAlchemyFileTreeItem.project_id == project_id)
                .where(SQLAlchemyFileTreeItem.path == path)
            )
            sqlalchemy_item = result.scalar_one_or_none()
            
            if sqlalchemy_item:
                return FileTreeItemMapper.to_domain(sqlalchemy_item)
            return None
    
    async def get_children(self, parent_id: str) -> List[DomainFileTreeItem]:
        """Get direct children of a file tree item"""
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyFileTreeItem)
                .where(SQLAlchemyFileTreeItem.parent_id == parent_id)
                .order_by(SQLAlchemyFileTreeItem.name)
            )
            sqlalchemy_items = result.scalars().all()
            
            return [FileTreeItemMapper.to_domain(item) for item in sqlalchemy_items]
    
    async def move_item(self, item_id: str, new_parent_id: Optional[str], new_path: str) -> Optional[DomainFileTreeItem]:
        """Move file tree item to new location"""
        return await self.update(item_id, {
            "parent_id": new_parent_id,
            "path": new_path
        })