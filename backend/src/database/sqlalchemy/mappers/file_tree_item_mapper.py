# backend/src/database/sqlalchemy/mappers/file_tree_item_mapper.py
"""
Mapper for converting between domain FileTreeItem and SQLAlchemy FileTreeItem models
"""
from typing import Dict, Any

from src.database.interfaces.models import FileTreeItem as DomainFileTreeItem
from ..models import FileTreeItem as SQLAlchemyFileTreeItem


class FileTreeItemMapper:
    """Handles conversion between domain and SQLAlchemy FileTreeItem models"""
    
    @staticmethod
    def to_domain(sqlalchemy_item: SQLAlchemyFileTreeItem) -> DomainFileTreeItem:
        """Convert SQLAlchemy FileTreeItem to domain FileTreeItem"""
        # Convert SQLAlchemy Tag objects to tag names for domain model
        tag_names = [tag.name for tag in sqlalchemy_item.tags] if sqlalchemy_item.tags else []
        
        return DomainFileTreeItem(
            id=sqlalchemy_item.id,
            project_id=sqlalchemy_item.project_id,
            name=sqlalchemy_item.name,
            type=sqlalchemy_item.type,
            path=sqlalchemy_item.path,
            parent_id=sqlalchemy_item.parent_id,
            document_id=sqlalchemy_item.document_id,
            word_count=sqlalchemy_item.word_count,
            icon=sqlalchemy_item.icon,
            tags=tag_names,
            created_at=sqlalchemy_item.created_at,
            updated_at=sqlalchemy_item.updated_at,
        )
    
    @staticmethod
    def to_sqlalchemy(domain_item: DomainFileTreeItem) -> SQLAlchemyFileTreeItem:
        """Convert domain FileTreeItem to SQLAlchemy FileTreeItem (tags handled separately)"""
        return SQLAlchemyFileTreeItem(
            id=domain_item.id,
            project_id=domain_item.project_id,
            name=domain_item.name,
            type=domain_item.type,
            path=domain_item.path,
            parent_id=domain_item.parent_id,
            document_id=domain_item.document_id,
            word_count=domain_item.word_count,
            icon=domain_item.icon,
            created_at=domain_item.created_at,
            updated_at=domain_item.updated_at,
            # tags handled separately in repository layer to avoid SQLAlchemy session conflicts
        )
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> DomainFileTreeItem:
        """Create domain FileTreeItem from dictionary data"""
        return DomainFileTreeItem(
            id=data["id"],
            project_id=data["project_id"],
            name=data["name"],
            type=data["type"],
            path=data["path"],
            parent_id=data.get("parent_id"),
            document_id=data.get("document_id"),
            word_count=data.get("word_count"),
            icon=data.get("icon"),
            tags=data.get("tags", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
    
    @staticmethod
    def to_dict(domain_item: DomainFileTreeItem) -> Dict[str, Any]:
        """Convert domain FileTreeItem to dictionary"""
        return {
            "id": domain_item.id,
            "project_id": domain_item.project_id,
            "name": domain_item.name,
            "type": domain_item.type,
            "path": domain_item.path,
            "parent_id": domain_item.parent_id,
            "document_id": domain_item.document_id,
            "word_count": domain_item.word_count,
            "icon": domain_item.icon,
            "tags": domain_item.tags,
            "created_at": domain_item.created_at,
            "updated_at": domain_item.updated_at,
        }