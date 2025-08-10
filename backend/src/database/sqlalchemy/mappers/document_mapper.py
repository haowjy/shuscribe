# backend/src/database/sqlalchemy/mappers/document_mapper.py
"""
Mapper for converting between domain Document and SQLAlchemy Document models
"""
from typing import Dict, Any, List

from src.database.interfaces.models import Document as DomainDocument
from ..models import Document as SQLAlchemyDocument


class DocumentMapper:
    """Handles conversion between domain and SQLAlchemy Document models"""
    
    @staticmethod
    def to_domain(sqlalchemy_document: SQLAlchemyDocument) -> DomainDocument:
        """Convert SQLAlchemy Document to domain Document"""
        # Convert SQLAlchemy Tag objects to tag names for domain model
        tag_names = [tag.name for tag in sqlalchemy_document.tags] if sqlalchemy_document.tags else []
        
        return DomainDocument(
            id=sqlalchemy_document.id,
            project_id=sqlalchemy_document.project_id,
            title=sqlalchemy_document.title,
            path=sqlalchemy_document.path,
            content=sqlalchemy_document.content or {},
            word_count=sqlalchemy_document.word_count,
            version=sqlalchemy_document.version,
            is_locked=sqlalchemy_document.is_locked,
            locked_by=sqlalchemy_document.locked_by,
            file_tree_id=sqlalchemy_document.file_tree_id,
            created_by=sqlalchemy_document.created_by,
            updated_by=sqlalchemy_document.updated_by,
            tags=tag_names,
            created_at=sqlalchemy_document.created_at,
            updated_at=sqlalchemy_document.updated_at,
        )
    
    @staticmethod
    def to_sqlalchemy(domain_document: DomainDocument) -> SQLAlchemyDocument:
        """Convert domain Document to SQLAlchemy Document
        
        Note: Tag relationships must be handled separately by the repository layer
        since tag resolution requires database access.
        """
        return SQLAlchemyDocument(
            id=domain_document.id,
            project_id=domain_document.project_id,
            title=domain_document.title,
            path=domain_document.path,
            content=domain_document.content or {},
            word_count=domain_document.word_count,
            version=domain_document.version,
            is_locked=domain_document.is_locked,
            locked_by=domain_document.locked_by,
            file_tree_id=domain_document.file_tree_id,
            created_by=domain_document.created_by,
            updated_by=domain_document.updated_by,
            created_at=domain_document.created_at,
            updated_at=domain_document.updated_at,
            # Note: tags handled separately via relationship assignment
        )
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> DomainDocument:
        """Create domain Document from dictionary data"""
        return DomainDocument(
            id=data["id"],
            project_id=data["project_id"],
            title=data["title"],
            path=data["path"],
            content=data.get("content", {}),
            word_count=data.get("word_count", 0),
            version=data.get("version", "1.0.0"),
            is_locked=data.get("is_locked", False),
            locked_by=data.get("locked_by"),
            file_tree_id=data.get("file_tree_id"),
            created_by=data.get("created_by"),
            updated_by=data.get("updated_by"),
            tags=data.get("tags", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
    
    @staticmethod
    def to_dict(domain_document: DomainDocument) -> Dict[str, Any]:
        """Convert domain Document to dictionary"""
        return {
            "id": domain_document.id,
            "project_id": domain_document.project_id,
            "title": domain_document.title,
            "path": domain_document.path,
            "content": domain_document.content,
            "word_count": domain_document.word_count,
            "version": domain_document.version,
            "is_locked": domain_document.is_locked,
            "locked_by": domain_document.locked_by,
            "file_tree_id": domain_document.file_tree_id,
            "created_by": domain_document.created_by,
            "updated_by": domain_document.updated_by,
            "tags": domain_document.tags,
            "created_at": domain_document.created_at,
            "updated_at": domain_document.updated_at,
        }