"""
Repository interfaces for the ShuScribe database layer.

These abstract interfaces define the contract that all repository
implementations must follow, enabling easy swapping between different
storage backends (memory, file, database).
"""

from src.database.interfaces.user_repository import IUserRepository
from src.database.interfaces.agent_repository import IAgentRepository
from src.database.interfaces.workspace_repository import IWorkspaceRepository
from src.database.interfaces.story_repository import IStoryRepository
from src.database.interfaces.wiki_repository import IWikiRepository
from src.database.interfaces.writing_repository import IWritingRepository

__all__ = [
    "IUserRepository",
    "IAgentRepository",
    "IWorkspaceRepository",
    "IStoryRepository", 
    "IWikiRepository",
    "IWritingRepository",
]