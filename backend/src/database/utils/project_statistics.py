# backend/src/database/utils/project_statistics.py
"""
Project statistics utilities for calculating and updating project metrics
"""
import logging
from typing import Optional

from src.database.factory import RepositoryContainer
from src.database.interfaces.models import Project as DomainProject

logger = logging.getLogger(__name__)


class ProjectStatisticsService:
    """Service for calculating and updating project statistics"""
    
    def __init__(self, repositories: RepositoryContainer):
        self.repositories = repositories
    
    async def recalculate_project_statistics(self, project_id: str) -> Optional[DomainProject]:
        """
        Recalculate and update project statistics across all backends
        
        For database backends, this delegates to the repository's native implementation.
        For memory backends, this manually calculates and updates the statistics.
        """
        try:
            # Try the repository's native implementation first (works for database backends)
            return await self.repositories.project.recalculate_statistics(project_id)
        except (NotImplementedError, Exception) as e:
            # Fall back to manual calculation for memory backends or if native fails
            logger.debug(f"Repository recalculate_statistics failed, using manual calculation: {e}")
            return await self._manual_recalculate_statistics(project_id)
    
    async def _manual_recalculate_statistics(self, project_id: str) -> Optional[DomainProject]:
        """Manually calculate statistics by querying documents and updating project"""
        # Get the project
        project = await self.repositories.project.get_by_id(project_id)
        if not project:
            return None
        
        # Get all documents for this project
        documents = await self.repositories.document.get_by_project_id(project_id)
        
        # Calculate statistics
        document_count = len(documents)
        total_word_count = sum(doc.word_count for doc in documents)
        
        # Update project with new statistics
        updated_project = await self.repositories.project.update(project_id, {
            "document_count": document_count,
            "word_count": total_word_count
        })
        
        logger.info(f"Recalculated statistics for project {project_id}: "
                   f"{document_count} documents, {total_word_count} words")
        
        return updated_project
    
    async def refresh_all_project_statistics(self) -> dict:
        """Refresh statistics for all projects"""
        all_projects = await self.repositories.project.list_all()
        
        results = {
            "updated": 0,
            "errors": [],
            "total": len(all_projects)
        }
        
        for project in all_projects:
            try:
                await self.recalculate_project_statistics(project.id)
                results["updated"] += 1
            except Exception as e:
                error_msg = f"Failed to update statistics for project {project.id}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        return results