"""
Repository factory for creating appropriate repository implementations
based on the configured backend (memory, file, or database).
"""

import os
from typing import Optional
from pathlib import Path
from dataclasses import dataclass

from src.config import settings
from src.database.interfaces import (
    IUserRepository,
    IAgentRepository,
    IWorkspaceRepository,
    IStoryRepository,
    IWikiRepository,
    IWritingRepository,
)


@dataclass(frozen=True)
class RepositoryContainer:
    """
    Typed container for all repository instances.
    
    Provides type-safe access to repositories with IDE autocompletion.
    Use repos.user, repos.wiki, etc. instead of repos["user"].
    """
    user: IUserRepository
    workspace: IWorkspaceRepository
    story: IStoryRepository
    wiki: IWikiRepository
    writing: IWritingRepository
    agent: IAgentRepository


class RepositoryFactory:
    """
    Factory class for creating repository instances based on backend type.
    
    This factory supports three backend types:
    - memory: In-memory storage for testing
    - file: File-based storage for local development
    - database: PostgreSQL/Supabase for production
    """
    
    @staticmethod
    def create_repositories(
        backend: Optional[str] = None,
        workspace_path: Optional[Path] = None,
        database_url: Optional[str] = None,
        **kwargs
    ) -> RepositoryContainer:
        """
        Create repository instances based on backend type.
        
        Args:
            backend: Backend type ('memory', 'file', 'database'). 
                    Defaults to settings.DATABASE_BACKEND
            workspace_path: Path for file-based storage. 
                           Defaults to Path("temp")
            database_url: Database connection URL. 
                         Defaults to settings.DATABASE_URL
            **kwargs: Additional backend-specific parameters
            
        Returns:
            RepositoryContainer with typed repository instances
        """
        # Use settings if not provided
        if backend is None:
            backend = settings.DATABASE_BACKEND
            
        if backend == "memory":
            return RepositoryFactory._create_memory_repositories(**kwargs)
            
        elif backend == "file":
            if workspace_path is None:
                workspace_path = Path("temp")
            return RepositoryFactory._create_file_repositories(workspace_path, **kwargs)
            
        elif backend == "database":
            if database_url is None:
                database_url = settings.DATABASE_URL
            return RepositoryFactory._create_database_repositories(database_url, **kwargs)
            
        else:
            raise ValueError(f"Unknown backend type: {backend}")
    
    @staticmethod
    def _create_memory_repositories(**kwargs) -> RepositoryContainer:
        """Create in-memory repository implementations"""
        # Import here to avoid circular dependencies
        from src.database.memory import (
            MemoryUserRepository,
            MemoryAgentRepository,
            MemoryWorkspaceRepository,
            MemoryStoryRepository,
            MemoryWikiRepository,
            MemoryWritingRepository,
        )
        
        return RepositoryContainer(
            user=MemoryUserRepository(),
            workspace=MemoryWorkspaceRepository(),
            story=MemoryStoryRepository(),
            wiki=MemoryWikiRepository(),
            writing=MemoryWritingRepository(),
            agent=MemoryAgentRepository(),
        )
    
    @staticmethod
    def _create_file_repositories(workspace_path: Path, **kwargs) -> RepositoryContainer:
        """Create file-based repository implementations"""
        # Ensure workspace directory exists
        # workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Import here to avoid circular dependencies
        # TODO: Update file implementations to use new interfaces
        # from src.database.file import (
        #     FileUserRepository,
        #     FileAgentRepository,
        #     FileWorkspaceRepository,
        #     FileStoryRepository,
        #     FileWikiRepository,
        #     FileWritingRepository,
        # )
        
        # return RepositoryContainer(
        #     user=FileUserRepository(workspace_path),
        #     workspace=FileWorkspaceRepository(workspace_path),
        #     story=FileStoryRepository(workspace_path),
        #     wiki=FileWikiRepository(workspace_path),
        #     writing=FileWritingRepository(workspace_path),
        #     agent=FileAgentRepository(workspace_path),
        # )
        
        raise NotImplementedError("File backend not implemented")
    
    @staticmethod
    def _create_database_repositories(database_url: str, **kwargs) -> RepositoryContainer:
        """Create database-backed repository implementations"""
        # Create database session
        # from src.database.postgres import create_session
        # session = create_session(database_url)
        
        # # Import here to avoid circular dependencies  
        # from src.database.postgres import (
        #     PostgresUserRepository,
        #     PostgresAgentRepository,
        #     PostgresWorkspaceRepository,
        #     PostgresStoryRepository,
        #     PostgresWikiRepository,
        #     PostgresWritingRepository,
        # )
        
        # return RepositoryContainer(
        #     user=PostgresUserRepository(session),
        #     workspace=PostgresWorkspaceRepository(session),
        #     story=PostgresStoryRepository(session),
        #     wiki=PostgresWikiRepository(session),
        #     writing=PostgresWritingRepository(session),
        #     agent=PostgresAgentRepository(session),
        # )
        raise NotImplementedError("Database backend not implemented")


def get_repositories(
    backend: Optional[str] = None,
    workspace_path: Optional[Path] = None,
    **kwargs
) -> RepositoryContainer:
    """
    Convenience function to get repository instances.
    
    This is the main entry point for the application to get repositories.
    
    Example:
        repos = get_repositories(backend="memory")
        user = await repos.user.get_user(user_id)
        articles = await repos.wiki.get_articles_by_workspace(workspace_id)
    """
    return RepositoryFactory.create_repositories(
        backend=backend,
        workspace_path=workspace_path,
        **kwargs
    )