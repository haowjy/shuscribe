"""
File-Based Repository Implementations

Desktop-optimized file storage with workspace-centric organization.
All data is stored in structured directories with JSON/Markdown files.
"""

from pathlib import Path

from src.database.repositories import FileRepositories
from src.database.file.user import FileUserRepository
from src.database.file.workspace import FileWorkspaceRepository
from src.database.file.story import FileStoryRepository
from src.database.file.wiki import FileWikiRepository

def create_file_repositories(workspace_path: Path) -> FileRepositories:
    """Factory function to create all file-based repositories"""

    
    return FileRepositories(
        user=FileUserRepository(workspace_path),
        workspace=FileWorkspaceRepository(workspace_path),
        story=FileStoryRepository(workspace_path),
        wiki=FileWikiRepository(workspace_path),
    )


__all__ = [
    "create_file_repositories",
] 