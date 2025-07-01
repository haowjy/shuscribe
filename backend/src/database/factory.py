"""
Repository Factory

Simple factory for creating repository implementations.
Supports switching between different backends (file, database).
"""

from typing import Dict, Any, Optional
from pathlib import Path

from src.database.file import create_file_repositories
from src.database.repositories import FileRepositories, DatabaseRepositories, Repositories  

class RepositoryFactory:
    """Factory for creating repository implementations"""
    
    @staticmethod
    def create_file_repositories(workspace_path: Path) -> FileRepositories:
        """Create file-based repositories for local desktop usage"""
        return create_file_repositories(workspace_path)
    
    @staticmethod
    def create_database_repositories(database_url: str) -> DatabaseRepositories:
        """Create database repositories for production usage"""
        # TODO: Implement when we add database repositories  
        raise NotImplementedError("Database repositories not yet implemented")
    
    @staticmethod
    def create_repositories(
        backend: str = "memory",
        workspace_path: Optional[Path] = None,
        database_url: Optional[str] = None
    ) -> Repositories:
        """
        Create repositories based on backend type
        
        Args:
            backend: Type of backend ("memory", "file", "database")
            workspace_path: Path for file-based storage
            database_url: URL for database connection
            
        Returns:
            Dictionary with repository instances
        """
        if backend == "file":
            if not workspace_path:
                raise ValueError("workspace_path required for file backend")
            return RepositoryFactory.create_file_repositories(workspace_path)
        elif backend == "database":
            if not database_url:
                raise ValueError("database_url required for database backend")
            return RepositoryFactory.create_database_repositories(database_url)
        else:
            raise ValueError(f"Unknown backend type: {backend}")


# Convenience function for common use cases
def get_repositories(backend: str = "file", **kwargs) -> Repositories:
    """Convenience function to get repositories"""
    if backend == "file" and "workspace_path" not in kwargs:
        kwargs["workspace_path"] = Path(".")  # Default to current directory
    return RepositoryFactory.create_repositories(backend=backend, **kwargs) 