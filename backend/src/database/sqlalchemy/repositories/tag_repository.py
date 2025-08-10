# backend/src/database/sqlalchemy/repositories/tag_repository.py
"""
SQLAlchemy Tag repository implementation
"""
import logging
from typing import List, Optional, Dict, Any
import uuid

from sqlalchemy import select, update, delete, text

from src.database.interfaces.tag_repository import TagRepository
from src.database.interfaces.models import Tag as DomainTag
from src.database.connection import get_session_context
from src.database.sqlalchemy.models import Tag as SQLAlchemyTag
from src.database.sqlalchemy.mappers import TagMapper

logger = logging.getLogger(__name__)


class DatabaseTagRepository(TagRepository):
    """Database-backed tag repository using SQLAlchemy"""
    
    async def get_by_id(self, tag_id: str) -> Optional[DomainTag]:
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyTag).where(SQLAlchemyTag.id == tag_id)
            )
            sqlalchemy_tag = result.scalar_one_or_none()
            
            if sqlalchemy_tag:
                return TagMapper.to_domain(sqlalchemy_tag)
            return None
    
    async def get_global_tags(self, include_archived: bool = False) -> List[DomainTag]:
        async with get_session_context() as session:
            query = select(SQLAlchemyTag).where(SQLAlchemyTag.is_global)
            if not include_archived:
                query = query.where(~SQLAlchemyTag.is_archived)
            
            result = await session.execute(query)
            sqlalchemy_tags = result.scalars().all()
            
            return [TagMapper.to_domain(tag) for tag in sqlalchemy_tags]
    
    async def get_user_tags(self, user_id: str, include_archived: bool = False) -> List[DomainTag]:
        async with get_session_context() as session:
            query = select(SQLAlchemyTag).where(SQLAlchemyTag.user_id == user_id)
            if not include_archived:
                query = query.where(~SQLAlchemyTag.is_archived)
            
            result = await session.execute(query)
            sqlalchemy_tags = result.scalars().all()
            
            return [TagMapper.to_domain(tag) for tag in sqlalchemy_tags]
    
    async def get_by_project_id(self, project_id: str, include_archived: bool = False) -> List[DomainTag]:
        async with get_session_context() as session:
            query = select(SQLAlchemyTag).where(SQLAlchemyTag.project_id == project_id)
            if not include_archived:
                query = query.where(~SQLAlchemyTag.is_archived)
            
            result = await session.execute(query)
            sqlalchemy_tags = result.scalars().all()
            
            return [TagMapper.to_domain(tag) for tag in sqlalchemy_tags]
    
    async def get_by_name(self, name: str, user_id: Optional[str] = None) -> Optional[DomainTag]:
        async with get_session_context() as session:
            if user_id:
                query = select(SQLAlchemyTag).where(SQLAlchemyTag.name == name, SQLAlchemyTag.user_id == user_id)
            else:
                query = select(SQLAlchemyTag).where(SQLAlchemyTag.name == name, SQLAlchemyTag.is_global)
            
            result = await session.execute(query)
            sqlalchemy_tag = result.scalar_one_or_none()
            
            if sqlalchemy_tag:
                return TagMapper.to_domain(sqlalchemy_tag)
            return None
    
    async def create(self, tag_data: Dict[str, Any]) -> DomainTag:
        async with get_session_context() as session:
            # Create domain tag first to validate data
            domain_tag = TagMapper.from_dict({
                "id": tag_data.get("id", str(uuid.uuid4())),
                **tag_data
            })
            
            # Convert to SQLAlchemy model and save
            sqlalchemy_tag = TagMapper.to_sqlalchemy(domain_tag)
            session.add(sqlalchemy_tag)
            await session.flush()
            
            # Return domain tag
            return TagMapper.to_domain(sqlalchemy_tag)
    
    async def update(self, tag_id: str, updates: Dict[str, Any]) -> Optional[DomainTag]:
        async with get_session_context() as session:
            result = await session.execute(
                update(SQLAlchemyTag).where(SQLAlchemyTag.id == tag_id).values(**updates)
            )
            
            if result.rowcount == 0:
                return None
            
            return await self.get_by_id(tag_id)
    
    async def delete(self, tag_id: str) -> bool:
        async with get_session_context() as session:
            result = await session.execute(
                delete(SQLAlchemyTag).where(SQLAlchemyTag.id == tag_id)
            )
            return result.rowcount > 0
    
    async def archive(self, tag_id: str) -> Optional[DomainTag]:
        return await self.update(tag_id, {"is_archived": True})
    
    async def unarchive(self, tag_id: str) -> Optional[DomainTag]:
        return await self.update(tag_id, {"is_archived": False})
    
    async def increment_usage(self, tag_id: str) -> Optional[DomainTag]:
        async with get_session_context() as session:
            result = await session.execute(
                update(SQLAlchemyTag)
                .where(SQLAlchemyTag.id == tag_id)
                .values(usage_count=SQLAlchemyTag.usage_count + 1)
            )
            
            if result.rowcount == 0:
                return None
            
            return await self.get_by_id(tag_id)
    
    async def decrement_usage(self, tag_id: str) -> Optional[DomainTag]:
        async with get_session_context() as session:
            result = await session.execute(
                update(SQLAlchemyTag)
                .where(SQLAlchemyTag.id == tag_id)
                .values(usage_count=SQLAlchemyTag.usage_count - 1)
            )
            
            if result.rowcount == 0:
                return None
            
            return await self.get_by_id(tag_id)
    
    async def get_by_category(self, category: str, user_id: Optional[str] = None) -> List[DomainTag]:
        async with get_session_context() as session:
            if user_id:
                query = select(SQLAlchemyTag).where(SQLAlchemyTag.category == category, SQLAlchemyTag.user_id == user_id)
            else:
                query = select(SQLAlchemyTag).where(SQLAlchemyTag.category == category, SQLAlchemyTag.is_global)
            
            result = await session.execute(query)
            sqlalchemy_tags = result.scalars().all()
            
            return [TagMapper.to_domain(tag) for tag in sqlalchemy_tags]
    
    async def get_system_tags(self) -> List[DomainTag]:
        async with get_session_context() as session:
            query = select(SQLAlchemyTag).where(SQLAlchemyTag.is_system)
            result = await session.execute(query)
            sqlalchemy_tags = result.scalars().all()
            
            return [TagMapper.to_domain(tag) for tag in sqlalchemy_tags]
    
    async def search_tags(self, query: str, user_id: Optional[str] = None, limit: int = 20) -> List[DomainTag]:
        async with get_session_context() as session:
            search_query = select(SQLAlchemyTag).where(SQLAlchemyTag.name.contains(query))
            
            if user_id:
                # Search both global and user's tags
                search_query = search_query.where(
                    (SQLAlchemyTag.is_global) | (SQLAlchemyTag.user_id == user_id)
                )
            else:
                search_query = search_query.where(SQLAlchemyTag.is_global)
            
            search_query = search_query.limit(limit)
            result = await session.execute(search_query)
            sqlalchemy_tags = result.scalars().all()
            
            return [TagMapper.to_domain(tag) for tag in sqlalchemy_tags]
    
    # Tag forking and precedence methods
    
    async def get_global_tag_by_name(self, name: str) -> Optional[DomainTag]:
        """Get global tag by name"""
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyTag)
                .where(SQLAlchemyTag.name == name)
                .where(SQLAlchemyTag.is_global == True)
                .where(SQLAlchemyTag.is_archived == False)
            )
            sqlalchemy_tag = result.scalar_one_or_none()
            
            if sqlalchemy_tag:
                return TagMapper.to_domain(sqlalchemy_tag)
            return None
    
    async def get_project_tag_by_name(self, project_id: str, name: str) -> Optional[DomainTag]:
        """Get project-specific tag by name"""
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyTag)
                .where(SQLAlchemyTag.name == name)
                .where(SQLAlchemyTag.project_id == project_id)
                .where(SQLAlchemyTag.is_archived == False)
            )
            sqlalchemy_tag = result.scalar_one_or_none()
            
            if sqlalchemy_tag:
                return TagMapper.to_domain(sqlalchemy_tag)
            return None
    
    async def get_tag_by_name_with_precedence(self, project_id: str, name: str) -> Optional[DomainTag]:
        """Get tag by name with project → global precedence"""
        # Try project-specific first
        project_tag = await self.get_project_tag_by_name(project_id, name)
        if project_tag:
            return project_tag
        
        # Fallback to global
        return await self.get_global_tag_by_name(name)
    
    async def get_all_usable_tags(self, project_id: str, include_archived: bool = False) -> List[DomainTag]:
        """Get all tags available to project (project-specific + global) with precedence deduplication"""
        async with get_session_context() as session:
            # Use window function to deduplicate by name with project precedence
            archive_filter = "" if include_archived else "AND is_archived = false"
            
            query = text(f"""
                SELECT id, name, icon, color, description, category, is_global, user_id, project_id,
                       usage_count, is_system, is_archived, created_at, updated_at
                FROM (
                    SELECT *, ROW_NUMBER() OVER (
                        PARTITION BY name 
                        ORDER BY CASE WHEN project_id = :project_id THEN 1 ELSE 2 END
                    ) as rn
                    FROM shuscribe_tags 
                    WHERE (project_id = :project_id OR is_global = true) {archive_filter}
                ) ranked
                WHERE rn = 1
                ORDER BY name
            """)
            
            result = await session.execute(query, {"project_id": project_id})
            rows = result.fetchall()
            
            # Convert rows to SQLAlchemy objects and then to domain models
            tags = []
            for row in rows:
                # Create SQLAlchemy tag object from row data
                sqlalchemy_tag = SQLAlchemyTag(
                    id=row.id,
                    name=row.name,
                    icon=row.icon,
                    color=row.color,
                    description=row.description,
                    category=row.category,
                    is_global=row.is_global,
                    user_id=row.user_id,
                    project_id=row.project_id,
                    usage_count=row.usage_count,
                    is_system=row.is_system,
                    is_archived=row.is_archived,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
                tags.append(TagMapper.to_domain(sqlalchemy_tag))
            
            return tags
    
    async def fork_global_tag(self, project_id: str, global_tag_id: str, customizations: Dict[str, Any]) -> DomainTag:
        """Create project-specific copy of global tag with customizations"""
        async with get_session_context() as session:
            # Get the global tag
            global_tag_result = await session.execute(
                select(SQLAlchemyTag).where(SQLAlchemyTag.id == global_tag_id)
            )
            global_tag = global_tag_result.scalar_one_or_none()
            
            if not global_tag:
                raise ValueError(f"Tag with ID {global_tag_id} not found")
            
            if not global_tag.is_global:
                raise ValueError("Can only fork global tags")
            
            # Check if project-specific tag with same name already exists
            existing_result = await session.execute(
                select(SQLAlchemyTag)
                .where(SQLAlchemyTag.name == global_tag.name)
                .where(SQLAlchemyTag.project_id == project_id)
            )
            existing_tag = existing_result.scalar_one_or_none()
            
            if existing_tag:
                raise ValueError(f"Project-specific tag '{global_tag.name}' already exists")
            
            # Create project-specific copy with customizations
            fork_data = {
                "name": global_tag.name,
                "description": global_tag.description,
                "category": global_tag.category,
                "project_id": project_id,
                "is_global": False,
                "is_system": False,  # Forked tags are never system tags
                "usage_count": 0,    # Start with zero usage
                # Apply customizations
                **customizations
            }
            
            # Use the existing create method
            return await self.create(fork_data)