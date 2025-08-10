# backend/src/database/sqlalchemy/mappers/tag_mapper.py
"""
Mapper for converting between domain Tag and SQLAlchemy Tag models
"""
from typing import Dict, Any

from src.database.interfaces.models import Tag as DomainTag
from ..models import Tag as SQLAlchemyTag


class TagMapper:
    """Handles conversion between domain and SQLAlchemy Tag models"""
    
    @staticmethod
    def to_domain(sqlalchemy_tag: SQLAlchemyTag) -> DomainTag:
        """Convert SQLAlchemy Tag to domain Tag"""
        return DomainTag(
            id=sqlalchemy_tag.id,
            name=sqlalchemy_tag.name,
            icon=sqlalchemy_tag.icon,
            color=sqlalchemy_tag.color,
            description=sqlalchemy_tag.description,
            category=sqlalchemy_tag.category,
            project_id=sqlalchemy_tag.project_id,
            is_global=sqlalchemy_tag.is_global,
            user_id=sqlalchemy_tag.user_id,
            is_system=sqlalchemy_tag.is_system,
            is_archived=sqlalchemy_tag.is_archived,
            usage_count=sqlalchemy_tag.usage_count,
            created_at=sqlalchemy_tag.created_at,
            updated_at=sqlalchemy_tag.updated_at,
        )
    
    @staticmethod
    def to_sqlalchemy(domain_tag: DomainTag) -> SQLAlchemyTag:
        """Convert domain Tag to SQLAlchemy Tag"""
        return SQLAlchemyTag(
            id=domain_tag.id,
            name=domain_tag.name,
            icon=domain_tag.icon,
            color=domain_tag.color,
            description=domain_tag.description,
            category=domain_tag.category,
            project_id=domain_tag.project_id,
            is_global=domain_tag.is_global,
            user_id=domain_tag.user_id,
            is_system=domain_tag.is_system,
            is_archived=domain_tag.is_archived,
            usage_count=domain_tag.usage_count,
            created_at=domain_tag.created_at,
            updated_at=domain_tag.updated_at,
        )
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> DomainTag:
        """Create domain Tag from dictionary data"""
        return DomainTag(
            id=data["id"],
            name=data["name"],
            icon=data.get("icon"),
            color=data.get("color"),
            description=data.get("description"),
            category=data.get("category"),
            project_id=data.get("project_id"),
            is_global=data.get("is_global", False),
            user_id=data.get("user_id"),
            is_system=data.get("is_system", False),
            is_archived=data.get("is_archived", False),
            usage_count=data.get("usage_count", 0),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
    
    @staticmethod
    def to_dict(domain_tag: DomainTag) -> Dict[str, Any]:
        """Convert domain Tag to dictionary"""
        return {
            "id": domain_tag.id,
            "name": domain_tag.name,
            "icon": domain_tag.icon,
            "color": domain_tag.color,
            "description": domain_tag.description,
            "category": domain_tag.category,
            "project_id": domain_tag.project_id,
            "is_global": domain_tag.is_global,
            "user_id": domain_tag.user_id,
            "is_system": domain_tag.is_system,
            "is_archived": domain_tag.is_archived,
            "usage_count": domain_tag.usage_count,
            "created_at": domain_tag.created_at,
            "updated_at": domain_tag.updated_at,
        }