# backend/src/database/sqlalchemy/repositories/project_repository.py
"""
SQLAlchemy Project repository implementation
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
import uuid

from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload

from src.database.interfaces import ProjectRepository
from src.database.interfaces.models import Project as DomainProject
from src.database.connection import get_session_context
from src.database.sqlalchemy.models import Project as SQLAlchemyProject, Document as SQLAlchemyDocument
from src.database.sqlalchemy.mappers import ProjectMapper
from src.database.utils import TagResolver

logger = logging.getLogger(__name__)


class DatabaseProjectRepository(ProjectRepository):
    """Database-backed project repository using SQLAlchemy"""
    
    def _user_has_access_to_project(self, project: SQLAlchemyProject, user_id: str) -> bool:
        """Check if user has access to project (owner or collaborator)"""
        if project.owner_id == user_id:
            return True
        
        # Check collaborators JSON field
        if project.collaborators:
            for collaborator in project.collaborators:
                if collaborator.get("user_id") == user_id:
                    return True
        
        return False
    
    async def get_by_id(self, project_id: str) -> Optional[DomainProject]:
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyProject).where(SQLAlchemyProject.id == project_id)
                .options(selectinload(SQLAlchemyProject.tags))
            )
            sqlalchemy_project = result.scalar_one_or_none()
            
            if sqlalchemy_project:
                return ProjectMapper.to_domain(sqlalchemy_project)
            return None
    
    async def create(self, project_data: Dict[str, Any]) -> DomainProject:
        async with get_session_context() as session:
            # Generate timestamps
            now = datetime.now(UTC).replace(tzinfo=None)
            
            # Create domain project first to validate data
            domain_project = ProjectMapper.from_dict({
                "id": project_data.get("id", str(uuid.uuid4())),
                "title": project_data["title"],
                "description": project_data.get("description", ""),
                "word_count": project_data.get("word_count", 0),
                "document_count": project_data.get("document_count", 0),
                "collaborators": project_data.get("collaborators", []),
                "settings": project_data.get("settings", {}),
                "tags": project_data.get("tags", []),  # Include tags
                "owner_id": project_data.get("owner_id"),
                "created_by": project_data.get("created_by"),
                "updated_by": project_data.get("updated_by"),
                "created_at": now,
                "updated_at": now,
            })
            
            # Convert to SQLAlchemy model (without tags first)
            sqlalchemy_project = ProjectMapper.to_sqlalchemy(domain_project)
            
            # Handle tag relationships if provided
            if project_data.get("tags"):
                # Resolve tag names to SQLAlchemy Tag objects
                resolved_tags = await TagResolver.resolve_tags(
                    session,
                    project_data["tags"],
                    project_id=domain_project.id,
                    user_id=project_data.get("created_by") or project_data.get("owner_id")
                )
                # Assign the resolved tags to the project
                sqlalchemy_project.tags = resolved_tags
            
            # Add to session and flush to get the project saved
            session.add(sqlalchemy_project)
            await session.flush()
            
            # Re-fetch with tags eagerly loaded to avoid lazy loading issues
            result = await session.execute(
                select(SQLAlchemyProject)
                .where(SQLAlchemyProject.id == sqlalchemy_project.id)
                .options(selectinload(SQLAlchemyProject.tags))
            )
            refreshed_project = result.scalar_one()
            
            # Return domain project with proper tag relationships
            return ProjectMapper.to_domain(refreshed_project)
    
    async def update(self, project_id: str, updates: Dict[str, Any]) -> Optional[DomainProject]:
        async with get_session_context() as session:
            # Add updated_at timestamp
            updates_copy = updates.copy()
            updates_copy["updated_at"] = datetime.now(UTC).replace(tzinfo=None)
            
            # Remove tags from updates as they are handled as relationships, not direct columns
            tags_update = updates_copy.pop("tags", None)
            
            result = await session.execute(
                update(SQLAlchemyProject).where(SQLAlchemyProject.id == project_id).values(**updates_copy)
            )
            
            if result.rowcount == 0:
                return None
            
            # Handle tag updates separately if provided
            if tags_update is not None:
                # Get the project to update its tags
                project_result = await session.execute(
                    select(SQLAlchemyProject)
                    .where(SQLAlchemyProject.id == project_id)
                    .options(selectinload(SQLAlchemyProject.tags))
                )
                project = project_result.scalar_one_or_none()
                
                if not project:
                    return None
                
                # Resolve new tags
                resolved_tags = await TagResolver.resolve_tags(
                    session,
                    tags_update,
                    project_id=project_id,
                    user_id=project.owner_id or project.created_by
                )
                
                # Update the tags relationship
                project.tags = resolved_tags
                await session.flush()
            
            # Return updated project
            return await self.get_by_id(project_id)
    
    async def delete(self, project_id: str) -> bool:
        async with get_session_context() as session:
            result = await session.execute(
                delete(SQLAlchemyProject).where(SQLAlchemyProject.id == project_id)
            )
            return result.rowcount > 0
    
    async def list_all(self) -> List[DomainProject]:
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyProject).order_by(SQLAlchemyProject.updated_at.desc())
                .options(selectinload(SQLAlchemyProject.tags))
            )
            sqlalchemy_projects = result.scalars().all()
            
            return [ProjectMapper.to_domain(project) for project in sqlalchemy_projects]
    
    async def list_by_user(self, user_id: str) -> List[DomainProject]:
        async with get_session_context() as session:
            # First get all projects - we need to check JSON collaborators field
            result = await session.execute(
                select(SQLAlchemyProject).order_by(SQLAlchemyProject.updated_at.desc())
                .options(selectinload(SQLAlchemyProject.tags))
            )
            all_projects = result.scalars().all()
            
            # Filter by access (owner or collaborator) and convert to domain
            accessible_projects = [
                ProjectMapper.to_domain(project) for project in all_projects 
                if self._user_has_access_to_project(project, user_id)
            ]
            
            return accessible_projects
    
    async def get_by_user_and_id(self, user_id: str, project_id: str) -> Optional[DomainProject]:
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyProject).where(SQLAlchemyProject.id == project_id)
                .options(selectinload(SQLAlchemyProject.tags))
            )
            sqlalchemy_project = result.scalar_one_or_none()
            
            # Check if user has access to this project
            if sqlalchemy_project and self._user_has_access_to_project(sqlalchemy_project, user_id):
                return ProjectMapper.to_domain(sqlalchemy_project)
            
            return None
    
    async def recalculate_statistics(self, project_id: str) -> Optional[DomainProject]:
        """Recalculate and update project statistics (word count, document count)"""
        async with get_session_context() as session:
            # Get current project
            project_result = await session.execute(
                select(SQLAlchemyProject).where(SQLAlchemyProject.id == project_id)
                .options(selectinload(SQLAlchemyProject.tags))
            )
            sqlalchemy_project = project_result.scalar_one_or_none()
            
            if not sqlalchemy_project:
                return None
            
            # Calculate statistics from documents
            stats_result = await session.execute(
                select(
                    func.count(SQLAlchemyDocument.id).label('document_count'),
                    func.coalesce(func.sum(SQLAlchemyDocument.word_count), 0).label('total_word_count')
                ).where(SQLAlchemyDocument.project_id == project_id)
            )
            stats = stats_result.first()
            
            # Update project with new statistics
            await session.execute(
                update(SQLAlchemyProject)
                .where(SQLAlchemyProject.id == project_id)
                .values(
                    document_count=stats.document_count if stats else 0,
                    word_count=stats.total_word_count if stats else 0,
                    updated_at=datetime.now(UTC).replace(tzinfo=None)
                )
            )
            
            # Get the updated project in the same session to see the changes
            updated_result = await session.execute(
                select(SQLAlchemyProject).where(SQLAlchemyProject.id == project_id)
                .options(selectinload(SQLAlchemyProject.tags))
            )
            updated_project = updated_result.scalar_one_or_none()
            
            if updated_project:
                return ProjectMapper.to_domain(updated_project)
            return None
