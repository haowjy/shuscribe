"""
Notebook Story Loader - Clean dependency injection for story loading in notebooks

This module provides a simple interface for loading test stories into any repository
that implements IStoryRepository, for use in Jupyter notebooks and testing environments.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

from src.database.interfaces.story_repository import IStoryRepository
from src.database.interfaces.workspace_repository import IWorkspaceRepository
from src.database.interfaces.user_repository import IUserRepository
from src.schemas.db.workspace import WorkspaceCreate
from src.schemas.db.story import (
    StoryMetadataCreate, 
    ChapterCreate, 
    ChapterStatus,
    StoryMetadata,
    Chapter,
    FullStoryBase
)
from src.schemas.db.user import UserCreate, SubscriptionTier


@dataclass
class StoryLoadResult:
    """Result of story loading operation"""
    story: FullStoryBase
    workspace_id: UUID
    user_id: UUID
    story_repository: IStoryRepository
    workspace_repository: IWorkspaceRepository
    user_repository: IUserRepository
    chapters_count: int
    
    def summary(self) -> str:
        return (
            f"�� Story: {self.story.metadata.title}\n"
            f"✍️  Author: {self.story.metadata.author}\n" 
            f"�� Chapters: {self.chapters_count}\n"
            f"�� Words: {self.story.word_count:,}\n"
            f"📁 Workspace: {self.workspace_id}\n"
            f"👤 User: {self.user_id}"
        )


class NotebookStoryLoader:
    """
    Clean story loader for notebooks with full dependency injection
    
    Loads stories into any repository that implements IStoryRepository.
    Designed for testing and notebook environments with maximum flexibility.
    """
    
    def __init__(
        self,
        story_repository: IStoryRepository,
        workspace_repository: IWorkspaceRepository,
        user_repository: IUserRepository
    ):
        """Initialize with injected repositories"""
        self.story_repo = story_repository
        self.workspace_repo = workspace_repository
        self.user_repo = user_repository
    
    async def load_story_from_directory(
        self, 
        story_directory: Path,
        workspace_name: Optional[str] = None,
        user_email: Optional[str] = None,
        user_display_name: Optional[str] = None
    ) -> StoryLoadResult:
        """
        Load story from any directory that follows the _meta.xml format
        
        Args:
            story_directory: Path to directory containing _meta.xml and chapter files
            workspace_name: Optional custom workspace name
            user_email: Optional custom user email
            user_display_name: Optional custom user display name
            
        Returns:
            StoryLoadResult with loaded story data
        """
        
        # 1. Create user and workspace
        user = await self._get_or_create_user(user_email, user_display_name)
        workspace = await self._create_workspace(
            user.id, 
            workspace_name or f"{story_directory.name.title()} Workspace"
        )
        
        # 2. Parse XML metadata and chapters
        story_data = self._parse_xml_story(story_directory)
        
        # 3. Store in repository
        story_metadata = await self._store_story_in_repository(workspace.id, story_data)
        
        # 4. Create FullStoryBase object for agents
        full_story = FullStoryBase(
            metadata=story_metadata,
            chapters=story_data["chapters"]
        )
        
        return StoryLoadResult(
            story=full_story,
            workspace_id=workspace.id,
            user_id=user.id,
            story_repository=self.story_repo,
            workspace_repository=self.workspace_repo,
            user_repository=self.user_repo,
            chapters_count=len(story_data["chapters"])
        )
    
    async def create_minimal_test_story(
        self,
        workspace_name: Optional[str] = None,
        user_email: Optional[str] = None,
        user_display_name: Optional[str] = None
    ) -> StoryLoadResult:
        """Create a minimal test story for basic testing"""
        
        # Create user and workspace
        user = await self._get_or_create_user(user_email, user_display_name)
        workspace = await self._create_workspace(
            user.id, 
            workspace_name or "Test Story Workspace"
        )
        
        # Define test story data
        story_data = {
            "title": "Test Story",
            "author": "Test Author",
            "synopsis": "A simple test story for agent testing",
            "genres": ["Fantasy"],
            "chapters": [
                {
                    "chapter_number": 1,
                    "title": "The Beginning", 
                    "content": "This is the beginning of our test story. Our hero starts their journey into the unknown, filled with hope and determination."
                },
                {
                    "chapter_number": 2,
                    "title": "The Challenge", 
                    "content": "Here we develop the plot further. Challenges arise and our hero must adapt, learning new skills and facing their fears."
                },
                {
                    "chapter_number": 3,
                    "title": "The Resolution", 
                    "content": "And this is how our story concludes. The hero succeeds against all odds, having grown and changed through their journey."
                }
            ]
        }
        
        # Store in repository
        story_metadata = await self._store_story_in_repository(workspace.id, story_data)
        
        # Create FullStoryBase object
        full_story = FullStoryBase(
            metadata=story_metadata,
            chapters=story_data["chapters"]
        )
        
        return StoryLoadResult(
            story=full_story,
            workspace_id=workspace.id,
            user_id=user.id,
            story_repository=self.story_repo,
            workspace_repository=self.workspace_repo,
            user_repository=self.user_repo,
            chapters_count=len(story_data["chapters"])
        )
    
    def _parse_xml_story(self, story_directory: Path) -> Dict:
        """Parse story from XML directory format following _meta.xml structure"""
        
        # Load metadata
        meta_file = story_directory / "_meta.xml"
        if not meta_file.exists():
            raise ValueError(f"No _meta.xml found in {story_directory}")
        
        tree = ET.parse(meta_file)
        root = tree.getroot()
        
        # Extract metadata
        title = root.findtext(".//Title", "").strip() or "Untitled Story"
        author = root.findtext(".//Author", "").strip() or "Unknown Author"
        synopsis = root.findtext(".//Synopsis", "").strip() or ""
        
        # Extract genres
        genres_element = root.find(".//Genres")
        genres = []
        if genres_element is not None:
            genres = [
                genre.get("name", "").strip()
                for genre in genres_element.findall("Genre")
                if genre.get("name")
            ]
        
        # Load chapters using the chapter list from _meta.xml if available
        chapters = self._load_chapters_from_metadata(story_directory, root)
        
        return {
            "title": title,
            "author": author,
            "synopsis": synopsis,
            "genres": genres,
            "chapters": chapters
        }
    
    def _load_chapters_from_metadata(self, story_directory: Path, metadata_root) -> List[Chapter]:
        """Load chapters using the chapter list from _meta.xml"""
        
        chapters = []
        
        # First try to use chapter list from metadata
        chapters_element = metadata_root.find(".//Chapters")
        if chapters_element is not None:
            chapter_elements = chapters_element.findall("Chapter")
            
            for i, chapter_elem in enumerate(chapter_elements, 1):
                ref = chapter_elem.get("ref", "")
                title = chapter_elem.get("title", f"Chapter {i}")
                
                if ref:
                    xml_file = story_directory / ref
                    if xml_file.exists():
                        content = xml_file.read_text(encoding="utf-8").strip()
                        chapter_content = self._extract_chapter_content(content)
                        
                        # Create Chapter object
                        chapter = Chapter(
                            id=UUID('00000000-0000-0000-0000-000000000000'),  # Placeholder
                            workspace_id=UUID('00000000-0000-0000-0000-000000000000'),  # Will be set later
                            chapter_number=i,
                            title=title,
                            content=chapter_content,
                            status=ChapterStatus.PUBLISHED,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        chapters.append(chapter)
                    else:
                        print(f"⚠️  Chapter file not found: {ref} (skipping)")
            
            if chapters:
                return chapters
        
        # Fallback: scan directory for numbered XML files
        print("📁 Falling back to directory scan for numbered XML files...")
        xml_files = sorted([
            f for f in story_directory.glob("*.xml") 
            if f.name != "_meta.xml" and f.name.replace(".xml", "").isdigit()
        ], key=lambda x: int(x.name.replace(".xml", "")))
        
        for xml_file in xml_files:
            chapter_number = int(xml_file.name.replace(".xml", ""))
            content = xml_file.read_text(encoding="utf-8")
            
            # Extract title and clean content
            chapter_title = self._extract_chapter_title(content) or f"Chapter {chapter_number}"
            chapter_content = self._extract_chapter_content(content)
            
            # Create Chapter object
            chapter = Chapter(
                id=UUID('00000000-0000-0000-0000-000000000000'),  # Placeholder
                workspace_id=UUID('00000000-0000-0000-0000-000000000000'),  # Will be set later
                chapter_number=chapter_number,
                title=chapter_title,
                content=chapter_content,
                status=ChapterStatus.PUBLISHED,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            chapters.append(chapter)
        
        return chapters
    
    def _extract_chapter_title(self, content: str) -> str:
        """Extract chapter title from content"""
        try:
            # Try to parse as XML and look for title attribute first
            root = ET.fromstring(content)
            
            # Check for title attribute on root element
            if root.get('title'):
                return root.get('title', '').strip()
            
            # Then check for title element
            title_elem = root.find(".//title") or root.find(".//Title")
            if title_elem is not None and title_elem.text:
                return title_elem.text.strip()
            
            # Look for chapter title in text content
            text_content = "".join(root.itertext())
            lines = text_content.split('\n')[:5]
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    return line.lstrip('#').strip()
                if line.startswith('[Chapter') and line.endswith(']'):
                    return line  # Return the full title with brackets
                if len(line) < 100 and line and not line.lower().startswith('chapter'):
                    return line
                    
        except ET.ParseError:
            # Not valid XML, look for markdown-style titles
            lines = content.split('\n')[:5]
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    return line.lstrip('#').strip()
        
        return ""
    
    def _extract_chapter_content(self, content: str) -> str:
        """Extract clean chapter content, stripping XML wrapper if present"""
        try:
            root = ET.fromstring(content)
            if root.tag == "Chapter":
                return "".join(root.itertext()).strip()
            else:
                # Try to find chapter content in nested elements
                chapter_elem = root.find(".//Chapter")
                if chapter_elem is not None:
                    return "".join(chapter_elem.itertext()).strip()
                else:
                    # Return all text content
                    return "".join(root.itertext()).strip()
        except ET.ParseError:
            # Not valid XML, return as-is
            return content.strip()
    
    async def _get_or_create_user(self, email: Optional[str] = None, display_name: Optional[str] = None):
        """Get or create a test user"""
        user_email = email or "notebook@example.com"
        user_display_name = display_name or "Notebook User"
        
        # Try to get existing user first
        existing_user = await self.user_repo.get_user_by_email(user_email)
        if existing_user:
            return existing_user
        
        # Create new user
        return await self.user_repo.create_user(UserCreate(
            email=user_email,
            display_name=user_display_name,
            subscription_tier=SubscriptionTier.PREMIUM
        ))
    
    async def _create_workspace(self, user_id: UUID, name: str):
        """Create a workspace for the story"""
        return await self.workspace_repo.create_workspace(WorkspaceCreate(
            name=name,
            description=f"Test workspace for {name}",
            owner_id=user_id,
            arcs=[],
            settings={"source": "notebook_import"}
        ))
    
    async def _store_story_in_repository(self, workspace_id: UUID, story_data: Dict) -> StoryMetadata:
        """Store story data in the repository and return metadata"""
        
        # Create story metadata
        metadata_create = StoryMetadataCreate(
            workspace_id=workspace_id,
            title=story_data["title"],
            author=story_data["author"],
            synopsis=story_data.get("synopsis", ""),
            genres=story_data.get("genres", []),
            tags=[],
            total_chapters=len(story_data["chapters"]),
            publication_status="completed"
        )
        story_metadata = await self.story_repo.create_story_metadata(metadata_create)
        
        # Create chapters
        for chapter in story_data["chapters"]:
            await self.story_repo.create_chapter(ChapterCreate(
                workspace_id=workspace_id,
                title=chapter.title,
                content=chapter.content,
                chapter_number=chapter.chapter_number,
                status=ChapterStatus.PUBLISHED,
                summary=None,
                tags=[],
                metadata={"source": "notebook_import"}
            ))
        
        return story_metadata


# Convenience functions for notebooks with dependency injection
async def load_story_with_repositories(
    story_directory: Path,
    story_repository: IStoryRepository,
    workspace_repository: IWorkspaceRepository,
    user_repository: IUserRepository,
    workspace_name: Optional[str] = None,
    user_email: Optional[str] = None,
    user_display_name: Optional[str] = None
) -> StoryLoadResult:
    """Load story with injected repositories"""
    loader = NotebookStoryLoader(story_repository, workspace_repository, user_repository)
    return await loader.load_story_from_directory(
        story_directory, workspace_name, user_email, user_display_name
    )


async def load_pokemon_amber_with_repositories(
    story_repository: IStoryRepository,
    workspace_repository: IWorkspaceRepository,
    user_repository: IUserRepository
) -> StoryLoadResult:
    """Load Pokemon Amber story with injected repositories"""
    story_directory = Path("../tests/resources/pokemon_amber/story")
    
    if not story_directory.exists():
        # Try from current directory
        story_directory = Path("tests/resources/pokemon_amber/story")
        
    if not story_directory.exists():
        raise FileNotFoundError(
            f"Pokemon Amber story not found. Tried:\n"
            f"  - ../tests/resources/pokemon_amber/story\n"
            f"  - tests/resources/pokemon_amber/story"
        )
    
    return await load_story_with_repositories(
        story_directory,
        story_repository,
        workspace_repository,
        user_repository,
        workspace_name="Pokemon Ambertwo Workspace"
    )


async def create_test_story_with_repositories(
    story_repository: IStoryRepository,
    workspace_repository: IWorkspaceRepository,
    user_repository: IUserRepository,
    workspace_name: Optional[str] = None,
    user_email: Optional[str] = None,
    user_display_name: Optional[str] = None
) -> StoryLoadResult:
    """Create minimal test story with injected repositories"""
    loader = NotebookStoryLoader(story_repository, workspace_repository, user_repository)
    return await loader.create_minimal_test_story(workspace_name, user_email, user_display_name)


# Legacy convenience functions for backward compatibility (using memory repositories)
async def load_pokemon_amber_story() -> StoryLoadResult:
    """Quick function to load Pokemon Amber story with memory repositories"""
    from src.database.factory import get_repositories
    
    repos = get_repositories(backend="memory")
    return await load_pokemon_amber_with_repositories(
        repos.story, repos.workspace, repos.user
    )


async def load_test_story() -> StoryLoadResult:
    """Quick function to load minimal test story with memory repositories"""
    from src.database.factory import get_repositories
    
    repos = get_repositories(backend="memory")
    return await create_test_story_with_repositories(
        repos.story, repos.workspace, repos.user
    )


async def load_story_from_xml(story_directory: Path, workspace_name: Optional[str] = None) -> StoryLoadResult:
    """Quick function to load story from XML directory with memory repositories"""
    from src.database.factory import get_repositories
    
    repos = get_repositories(backend="memory")
    return await load_story_with_repositories(
        story_directory, repos.story, repos.workspace, repos.user, workspace_name
    )