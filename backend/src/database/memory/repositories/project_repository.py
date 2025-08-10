# backend/src/database/memory/repositories/project_repository.py
"""
Memory Project repository implementation
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC

from src.database.interfaces.project_repository import ProjectRepository
from src.database.interfaces.models import Project as DomainProject


class MemoryProjectRepository(ProjectRepository):
    """In-memory project repository for testing"""
    
    def __init__(self):
        self._projects: Dict[str, DomainProject] = {}
    
    def _user_has_access_to_project(self, project: DomainProject, user_id: str) -> bool:
        """Check if user has access to project (owner or collaborator)"""
        if project.owner_id == user_id:
            return True
        
        # Check collaborators list
        if project.collaborators:
            for collaborator in project.collaborators:
                if collaborator.get("user_id") == user_id:
                    return True
        
        return False
    
    async def get_by_id(self, project_id: str) -> Optional[DomainProject]:
        return self._projects.get(project_id)
    
    async def create(self, project_data: Dict[str, Any]) -> DomainProject:
        project_id = project_data.get("id", str(uuid.uuid4()))
        now = datetime.now(UTC).replace(tzinfo=None)
        
        project = DomainProject(
            id=project_id,
            title=project_data["title"],
            description=project_data.get("description", ""),
            word_count=project_data.get("word_count", 0),
            document_count=project_data.get("document_count", 0),
            collaborators=project_data.get("collaborators", []),
            settings=project_data.get("settings", {}),
            tags=project_data.get("tags", []),
            owner_id=project_data.get("owner_id"),
            created_by=project_data.get("created_by"),
            updated_by=project_data.get("updated_by"),
            created_at=now,
            updated_at=now,
        )
        self._projects[project_id] = project
        return project
    
    async def update(self, project_id: str, updates: Dict[str, Any]) -> Optional[DomainProject]:
        project = self._projects.get(project_id)
        if not project:
            return None
        
        # Create updated project (dataclass is immutable)
        update_data = {
            "id": project.id,
            "title": updates.get("title", project.title),
            "description": updates.get("description", project.description),
            "word_count": updates.get("word_count", project.word_count),
            "document_count": updates.get("document_count", project.document_count),
            "collaborators": updates.get("collaborators", project.collaborators),
            "settings": updates.get("settings", project.settings),
            "tags": updates.get("tags", project.tags),
            "owner_id": updates.get("owner_id", project.owner_id),
            "created_by": project.created_by,
            "updated_by": updates.get("updated_by", project.updated_by),
            "created_at": project.created_at,
            "updated_at": datetime.now(UTC).replace(tzinfo=None),
        }
        
        updated_project = DomainProject(**update_data)
        self._projects[project_id] = updated_project
        return updated_project
    
    async def delete(self, project_id: str) -> bool:
        if project_id in self._projects:
            del self._projects[project_id]
            return True
        return False
    
    async def list_all(self) -> List[DomainProject]:
        # Return sorted by updated_at descending
        projects = list(self._projects.values())
        return sorted(projects, key=lambda p: p.updated_at, reverse=True)
    
    async def list_by_user(self, user_id: str) -> List[DomainProject]:
        # Filter by access (owner or collaborator) and return sorted by updated_at descending
        projects = [p for p in self._projects.values() if self._user_has_access_to_project(p, user_id)]
        return sorted(projects, key=lambda p: p.updated_at, reverse=True)
    
    async def get_by_user_and_id(self, user_id: str, project_id: str) -> Optional[DomainProject]:
        project = self._projects.get(project_id)
        if project and self._user_has_access_to_project(project, user_id):
            return project
        return None
    
    async def recalculate_statistics(self, project_id: str) -> Optional[DomainProject]:
        """Recalculate and update project statistics (word count, document count)"""
        # Memory repository doesn't implement this directly to avoid circular dependencies
        # Use ProjectStatisticsService.recalculate_project_statistics() instead
        raise NotImplementedError(
            "Memory repository requires ProjectStatisticsService for statistics calculation"
        )