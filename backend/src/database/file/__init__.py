"""
File-Based Repository Implementations

Desktop-optimized file storage with workspace-centric organization.
All data is stored in structured directories with JSON/Markdown files.
"""

from pathlib import Path

from src.database.models.repositories import FileRepositories


def create_file_repositories(workspace_path: Path) -> FileRepositories:
    """Factory function to create all file-based repositories"""
    from .user import FileUserRepository
    from .workspace import FileWorkspaceRepository
    from .story import FileStoryRepository
    from .wiki import FileWikiRepository
    
    return FileRepositories(
        user=FileUserRepository(workspace_path),
        workspace=FileWorkspaceRepository(workspace_path),
        story=FileStoryRepository(workspace_path),
        wiki=FileWikiRepository(workspace_path),
    )


__all__ = [
    "create_file_repositories",
] 