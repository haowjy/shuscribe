# backend/src/api/dependencies.py
"""
FastAPI dependencies
"""
from pathlib import Path
from uuid import UUID

from src.database.factory import get_repositories, RepositoryContainer
from src.database.interfaces.user_repository import IUserRepository
from src.database.interfaces.workspace_repository import IWorkspaceRepository
from src.database.interfaces.story_repository import IStoryRepository
from src.database.interfaces.wiki_repository import IWikiRepository
from src.database.interfaces.writing_repository import IWritingRepository
from src.database.interfaces.agent_repository import IAgentRepository

from src.services.user.user_service import UserService
from src.services.workspace.workspace_service import WorkspaceService
from src.services.story.story_service import StoryService
from src.services.wiki.wiki_service import WikiService
from src.services.writing.writing_service import WritingService
from src.services.agent.agent_service import AgentService


def get_repository_container() -> RepositoryContainer:
    """Get repository container based on configuration"""
    from src.config import settings

    if settings.DATABASE_BACKEND == "memory":
        # Use memory-based repository for local development
        return get_repositories(backend="memory", workspace_path=Path("temp"))
    else:
        # TODO: Use database repository when implemented
        # For now, fall back to memory-based even in database mode
        return get_repositories(backend="memory", workspace_path=Path("temp"))


def get_user_repository_dependency() -> IUserRepository:
    """Get user repository instance based on configuration"""
    return get_repository_container().user


def get_workspace_repository_dependency() -> IWorkspaceRepository:
    """Get workspace repository instance based on configuration"""
    return get_repository_container().workspace


def get_story_repository_dependency() -> IStoryRepository:
    """Get story repository instance based on configuration"""
    return get_repository_container().story


def get_wiki_repository_dependency() -> IWikiRepository:
    """Get wiki repository instance based on configuration"""
    return get_repository_container().wiki


def get_writing_repository_dependency() -> IWritingRepository:
    """Get writing repository instance based on configuration"""
    return get_repository_container().writing


def get_agent_repository_dependency() -> IAgentRepository:
    """Get agent repository instance based on configuration"""
    return get_repository_container().agent


# Service Dependencies
def get_user_service_dependency() -> UserService:
    """Get user service instance"""
    user_repo = get_user_repository_dependency()
    return UserService(user_repo)


def get_workspace_service_dependency() -> WorkspaceService:
    """Get workspace service instance"""
    workspace_repo = get_workspace_repository_dependency()
    return WorkspaceService(workspace_repo)


def get_story_service_dependency() -> StoryService:
    """Get story service instance"""
    story_repo = get_story_repository_dependency()
    workspace_repo = get_workspace_repository_dependency()
    return StoryService(story_repo, workspace_repo)


def get_wiki_service_dependency() -> WikiService:
    """Get wiki service instance"""
    wiki_repo = get_wiki_repository_dependency()
    workspace_repo = get_workspace_repository_dependency()
    return WikiService(wiki_repo, workspace_repo)


def get_writing_service_dependency() -> WritingService:
    """Get writing service instance"""
    writing_repo = get_writing_repository_dependency()
    workspace_repo = get_workspace_repository_dependency()
    return WritingService(writing_repo, workspace_repo)


def get_agent_service_dependency() -> AgentService:
    """Get agent service instance"""
    agent_repo = get_agent_repository_dependency()
    workspace_repo = get_workspace_repository_dependency()
    return AgentService(agent_repo, workspace_repo)


async def get_current_user_id_dependency() -> UUID:
    """Get current user ID based on repository type"""
    from src.config import settings

    if settings.DATABASE_BACKEND == "memory":
        # For development, use a consistent development user
        user_service = get_user_service_dependency()
        
        # Try to get existing development user first
        dev_email = "dev@localhost"
        existing_user = await user_service.get_user_by_email(dev_email)
        
        if existing_user:
            return existing_user.id
        
        # Create development user if it doesn't exist
        from src.schemas.db.user import UserCreate
        try:
            user_data = UserCreate(
                email=dev_email,
                display_name="Development User"
            )
            user = await user_service.create_user(user_data)
            return user.id
        except Exception:
            # If creation fails, return a consistent UUID for development
            # This handles the case where the user was created between our check and creation attempt
            retry_user = await user_service.get_user_by_email(dev_email)
            if retry_user:
                return retry_user.id
            
            # Fallback to consistent UUID if all else fails
            from uuid import UUID
            return UUID("00000000-0000-0000-0000-000000000001")
    else:
        # TODO: Implement proper auth when database is enabled
        # For now, return a mock UUID for testing
        from uuid import uuid4
        return uuid4()
