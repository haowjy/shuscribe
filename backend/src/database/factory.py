# backend/src/database/factory.py
"""
Repository factory for dependency injection
Supports multiple backends: database, memory
"""
import logging
from typing import Optional

from src.database.interfaces import ProjectRepository, DocumentRepository, FileTreeRepository

logger = logging.getLogger(__name__)


class RepositoryContainer:
    """Container for all repositories"""
    
    def __init__(
        self,
        project: ProjectRepository,
        document: DocumentRepository,
        file_tree: FileTreeRepository,
    ):
        self.project = project
        self.document = document
        self.file_tree = file_tree


def create_repositories(backend: str = "database") -> RepositoryContainer:
    """
    Factory function to create repository instances
    
    Args:
        backend: "database" for SQLAlchemy/Supabase, "memory" for in-memory testing
    
    Returns:
        RepositoryContainer with all repositories
    """
    if backend == "memory":
        logger.info("Creating in-memory repositories for testing")
        from src.database.repositories import (
            MemoryProjectRepository,
            MemoryDocumentRepository, 
            MemoryFileTreeRepository
        )
        return RepositoryContainer(
            project=MemoryProjectRepository(),
            document=MemoryDocumentRepository(),
            file_tree=MemoryFileTreeRepository(),
        )
    elif backend == "database":
        logger.info("Creating database repositories")
        from src.database.repositories import (
            DatabaseProjectRepository,
            DatabaseDocumentRepository,
            DatabaseFileTreeRepository
        )
        return RepositoryContainer(
            project=DatabaseProjectRepository(),
            document=DatabaseDocumentRepository(),
            file_tree=DatabaseFileTreeRepository(),
        )
    else:
        raise ValueError(f"Unknown backend: {backend}")


# Global repository container (will be initialized in main.py)
_repositories: Optional[RepositoryContainer] = None


def get_repositories() -> RepositoryContainer:
    """Get the global repository container"""
    if _repositories is None:
        raise RuntimeError("Repositories not initialized. Call init_repositories() first.")
    return _repositories


def init_repositories(backend: str = "database") -> None:
    """Initialize the global repository container"""
    global _repositories
    _repositories = create_repositories(backend)
    logger.info(f"Repositories initialized with backend: {backend}")


def is_initialized() -> bool:
    """Check if repositories are initialized"""
    return _repositories is not None


def reset_repositories() -> None:
    """Reset repositories (useful for testing)"""
    global _repositories
    _repositories = None
    logger.info("Repositories reset")