"""
Repository Interface Definitions

Abstract interfaces that define contracts for all storage backends.
Following the Interface Segregation Principle - each domain gets its own interface.
"""

from src.database.interfaces.user import IUserRepository
from src.database.interfaces.workspace import IWorkspaceRepository  
from src.database.interfaces.story import IStoryRepository
from src.database.interfaces.wiki import IWikiRepository

__all__ = [
    "IUserRepository",
    "IWorkspaceRepository", 
    "IStoryRepository",
    "IWikiRepository",
] 