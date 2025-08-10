# backend/src/database/sqlalchemy/mappers/project_mapper.py
"""
Mapper for converting between domain Project and SQLAlchemy Project models
"""
from typing import Dict, Any

from src.database.interfaces.models import Project as DomainProject
from ..models import Project as SQLAlchemyProject


class ProjectMapper:
    """Handles conversion between domain and SQLAlchemy Project models"""
    
    @staticmethod
    def to_domain(sqlalchemy_project: SQLAlchemyProject) -> DomainProject:
        """Convert SQLAlchemy Project to domain Project"""
        return DomainProject(
            id=sqlalchemy_project.id,
            title=sqlalchemy_project.title,
            description=sqlalchemy_project.description,
            owner_id=sqlalchemy_project.owner_id,
            created_by=sqlalchemy_project.created_by,
            updated_by=sqlalchemy_project.updated_by,
            word_count=sqlalchemy_project.word_count,
            document_count=sqlalchemy_project.document_count,
            collaborators=sqlalchemy_project.collaborators or [],
            settings=sqlalchemy_project.settings or {},
            tags=[tag.name for tag in sqlalchemy_project.tags] if hasattr(sqlalchemy_project, 'tags') and sqlalchemy_project.tags is not None else [],
            created_at=sqlalchemy_project.created_at,
            updated_at=sqlalchemy_project.updated_at,
        )
    
    @staticmethod
    def to_sqlalchemy(domain_project: DomainProject) -> SQLAlchemyProject:
        """Convert domain Project to SQLAlchemy Project"""
        # Note: tags relationship is handled separately by repositories when needed
        return SQLAlchemyProject(
            id=domain_project.id,
            title=domain_project.title,
            description=domain_project.description,
            owner_id=domain_project.owner_id,
            created_by=domain_project.created_by,
            updated_by=domain_project.updated_by,
            word_count=domain_project.word_count,
            document_count=domain_project.document_count,
            collaborators=domain_project.collaborators or [],
            settings=domain_project.settings or {},
            created_at=domain_project.created_at,
            updated_at=domain_project.updated_at,
        )
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> DomainProject:
        """Create domain Project from dictionary data"""
        return DomainProject(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            owner_id=data.get("owner_id"),
            created_by=data.get("created_by"),
            updated_by=data.get("updated_by"),
            word_count=data.get("word_count", 0),
            document_count=data.get("document_count", 0),
            collaborators=data.get("collaborators", []),
            settings=data.get("settings", {}),
            tags=data.get("tags", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
    
    @staticmethod
    def to_dict(domain_project: DomainProject) -> Dict[str, Any]:
        """Convert domain Project to dictionary"""
        return {
            "id": domain_project.id,
            "title": domain_project.title,
            "description": domain_project.description,
            "owner_id": domain_project.owner_id,
            "created_by": domain_project.created_by,
            "updated_by": domain_project.updated_by,
            "word_count": domain_project.word_count,
            "document_count": domain_project.document_count,
            "collaborators": domain_project.collaborators,
            "settings": domain_project.settings,
            "tags": domain_project.tags,
            "created_at": domain_project.created_at,
            "updated_at": domain_project.updated_at,
        }