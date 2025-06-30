from dataclasses import dataclass
from typing import Any

from src.database.file.user import FileUserRepository
from src.database.file.workspace import FileWorkspaceRepository
from src.database.file.story import FileStoryRepository
from src.database.file.wiki import FileWikiRepository

from src.database.interfaces.story import IStoryRepository
from src.database.interfaces.user import IUserRepository
from src.database.interfaces.wiki import IWikiRepository
from src.database.interfaces.workspace import IWorkspaceRepository

@dataclass
class Repositories:
    user: IUserRepository
    workspace: IWorkspaceRepository
    story: IStoryRepository
    wiki: IWikiRepository

@dataclass
class FileRepositories(Repositories):
    user: FileUserRepository
    workspace: FileWorkspaceRepository
    story: FileStoryRepository
    wiki: FileWikiRepository

@dataclass
class DatabaseRepositories(Repositories): # TODO: Implement database repositories
    pass