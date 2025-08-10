"""
ProjectFactory for creating Project domain models in tests.
"""
import uuid
from datetime import datetime, UTC
from typing import Optional, Dict, Any, List

from src.database.interfaces.models import Project


class ProjectFactory:
    """Factory for creating Project domain models with realistic test data."""
    
    @staticmethod
    def create(
        id: Optional[str] = None,
        title: Optional[str] = None,
        description: str = "",
        owner_id: Optional[str] = None,
        created_by: Optional[str] = None,
        updated_by: Optional[str] = None,
        collaborators: Optional[List[Dict[str, Any]]] = None,
        word_count: int = 0,
        document_count: int = 0,
        settings: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs
    ) -> Project:
        """
        Create a Project domain model with sensible defaults.
        
        Args:
            id: Project ID (auto-generated UUID if not provided)
            title: Project title (auto-generated if not provided)
            description: Project description (empty by default)
            owner_id: Owner user ID (auto-generated UUID if not provided)
            created_by: User ID who created the project (uses owner_id if not provided)
            updated_by: User ID who last updated the project (uses owner_id if not provided)
            collaborators: List of collaborator dictionaries (default single owner)
            word_count: Total word count (0 by default)
            document_count: Total document count (0 by default)
            settings: Project settings dict (default empty)
            tags: List of tag names/IDs (default empty)
            created_at: Creation timestamp (current time if not provided)
            updated_at: Update timestamp (current time if not provided)
            **kwargs: Additional keyword arguments
            
        Returns:
            Properly constructed Project domain model
        """
        # Generate defaults
        project_id = id or str(uuid.uuid4())
        project_title = title or f"Test Project {project_id[:8]}"
        project_owner_id = owner_id or str(uuid.uuid4())
        now = datetime.now(UTC).replace(tzinfo=None)
        
        # Default collaborators - single owner
        if collaborators is None:
            collaborators = [
                {
                    "user_id": project_owner_id,
                    "role": "owner",
                    "name": f"Test Owner {project_owner_id[:8]}",
                    "avatar": None
                }
            ]
        
        # Default settings
        if settings is None:
            settings = {
                "auto_save_interval": 30000,
                "word_count_target": 50000,
                "backup_enabled": True
            }
        
        # Default tags
        if tags is None:
            tags = []
        
        return Project(
            id=project_id,
            title=project_title,
            description=description,
            owner_id=project_owner_id,
            created_by=created_by or project_owner_id,
            updated_by=updated_by or project_owner_id,
            collaborators=collaborators,
            word_count=word_count,
            document_count=document_count,
            settings=settings,
            tags=tags,
            created_at=created_at or now,
            updated_at=updated_at or now,
        )
    
    @staticmethod
    def create_fantasy_novel() -> Project:
        """Create a fantasy novel project with typical settings."""
        return ProjectFactory.create(
            title="The Chronicles of Aethermoor",
            description="An epic fantasy saga set in a world of magic and ancient mysteries.",
            word_count=15420,
            document_count=8,
            tags=["fantasy", "novel", "magic", "adventure"],
            settings={
                "auto_save_interval": 30000,
                "word_count_target": 100000,
                "backup_enabled": True,
                "backup_frequency": "daily",
                "export_formats": ["pdf", "epub", "docx"]
            },
            collaborators=[
                {
                    "user_id": "author_001",
                    "role": "owner",
                    "name": "Epic Fantasy Author",
                    "avatar": "https://example.com/author.jpg"
                },
                {
                    "user_id": "editor_002", 
                    "role": "editor",
                    "name": "Professional Editor",
                    "avatar": None
                }
            ]
        )
    
    @staticmethod
    def create_minimal() -> Project:
        """Create a project with minimal required data."""
        return ProjectFactory.create(
            title="Minimal Test Project",
            description="",
            word_count=0,
            document_count=0,
            tags=[],
            collaborators=[],
            settings={}
        )
    
    @staticmethod
    def create_with_custom_collaborators(collaborators: List[Dict[str, Any]]) -> Project:
        """Create a project with specific collaborators."""
        return ProjectFactory.create(
            title="Collaborative Project",
            description="A project with custom collaborators",
            collaborators=collaborators
        )
    
    @staticmethod
    def create_with_high_stats() -> Project:
        """Create a project with high word count and document count for testing statistics."""
        return ProjectFactory.create(
            title="Large Project",
            description="A large project for statistics testing",
            word_count=250000,
            document_count=45,
            tags=["large", "statistics", "test"]
        )