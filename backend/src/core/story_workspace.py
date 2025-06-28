"""
Story Workspace Management
Manages complete user workspaces including stories, wiki pages, and writing materials
"""
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Iterator
from uuid import UUID, uuid4

from src.core.story_loading import StoryLoaderFactory, StoryLoadingError
from src.database.repositories import get_story_repository
from src.database.repositories.wikipage import get_wikipage_repository
from src.database.repositories.writing import get_writing_repository
from src.schemas.story import InputStory, Story, Chapter, RawChapter, RawStoryMetadata
from src.schemas.wiki import WikiPage, WikiPageCreate


class LazyChapter:
    """Lazy-loaded chapter that reads content from file on demand"""
    
    def __init__(self, chapter_number: int, title: str, file_path: Path, ref: Optional[str] = None):
        self.chapter_number = chapter_number
        self.title = title
        self.file_path = file_path
        self.ref = ref
        self._content: Optional[str] = None
    
    @property
    def content(self) -> str:
        """Load content from file on first access"""
        if self._content is None:
            try:
                self._content = self.file_path.read_text(encoding='utf-8')
            except (FileNotFoundError, IOError) as e:
                raise StoryLoadingError(f"Could not read chapter file {self.file_path}: {e}")
        return self._content
    
    def to_raw_chapter(self) -> RawChapter:
        """Convert to RawChapter schema"""
        return RawChapter(
            chapter_number=self.chapter_number,
            title=self.title,
            content=self.content,  # This triggers lazy loading
            ref=self.ref
        )


class ChapterRange:
    """Represents a range of chapters with lazy loading support"""
    
    def __init__(self, lazy_chapters: List[LazyChapter]):
        self._lazy_chapters = {ch.chapter_number: ch for ch in lazy_chapters}
    
    def __len__(self) -> int:
        return len(self._lazy_chapters)
    
    def __iter__(self) -> Iterator[LazyChapter]:
        """Iterate chapters in order"""
        for chapter_num in sorted(self._lazy_chapters.keys()):
            yield self._lazy_chapters[chapter_num]
    
    def __getitem__(self, key: Union[int, slice]) -> Union[LazyChapter, List[LazyChapter]]:
        """Get chapter(s) by number or slice"""
        if isinstance(key, int):
            return self._lazy_chapters[key]
        elif isinstance(key, slice):
            chapter_numbers = sorted(self._lazy_chapters.keys())
            selected_numbers = chapter_numbers[key]
            return [self._lazy_chapters[num] for num in selected_numbers]
        else:
            raise TypeError("Chapter key must be int or slice")
    
    def get_range(self, start: int, end: int) -> List[LazyChapter]:
        """Get chapters in a specific range (inclusive)"""
        return [self._lazy_chapters[num] for num in range(start, end + 1) if num in self._lazy_chapters]
    
    def get_chunk(self, start: int, count: int) -> List[LazyChapter]:
        """Get a chunk of chapters starting from a specific number"""
        chapter_numbers = sorted(self._lazy_chapters.keys())
        start_idx = next((i for i, num in enumerate(chapter_numbers) if num >= start), 0)
        selected_numbers = chapter_numbers[start_idx:start_idx + count]
        return [self._lazy_chapters[num] for num in selected_numbers]
    
    def to_raw_chapters(self, chapter_numbers: Optional[List[int]] = None) -> List[RawChapter]:
        """Convert to RawChapter schemas, optionally filtering by chapter numbers"""
        if chapter_numbers is None:
            return [ch.to_raw_chapter() for ch in self]
        else:
            return [self._lazy_chapters[num].to_raw_chapter() for num in chapter_numbers if num in self._lazy_chapters]


class StoryWorkspace:
    """
    Manages a complete user workspace including stories, wiki pages, and writing materials
    
    Expected directory structure:
    workspace_root/
    ├── _meta.xml          # Story metadata
    ├── 1.xml              # Chapter files (lazy loaded)
    ├── 2.xml
    └── ...
    wikipage/
    ├── main.md
    ├── characters/
    ├──── character1.md
    └── ...
    writing/               # Future: author-only content
    ├── drafts/
    ├── worldbuilding/
    └── ...
    """
    
    def __init__(self, workspace_root: Path, owner_id: UUID):
        self.workspace_root = workspace_root
        self.owner_id = owner_id
        
        # Repository connections
        self._story_repo = get_story_repository()
        self._wikipage_repo = get_wikipage_repository()
        self._writing_repo = get_writing_repository()
        
        # Workspace state
        self._story_metadata = None
        self._lazy_chapters: Optional[ChapterRange] = None
        self._story_id: Optional[UUID] = None
        self._wiki_page_id: Optional[UUID] = None
        
        # Directory paths
        self.story_directory = workspace_root
        self.wiki_directory = workspace_root / "wikipage"
        self.writing_directory = workspace_root / "writing"

    @property
    def story_metadata(self) -> 'RawStoryMetadata':
        """Get story metadata (lazy loaded) - always returns valid metadata"""
        if self._story_metadata is None:
            self._load_story_metadata()
        # Always return valid metadata, even if loading failed
        return self._story_metadata or RawStoryMetadata.create_empty()

    @property
    def chapters(self) -> ChapterRange:
        """Get lazy-loaded chapters"""
        if self._lazy_chapters is None:
            self._load_chapters()
        if self._lazy_chapters is None:
            raise StoryLoadingError("Failed to load chapters")
        return self._lazy_chapters

    def _load_story_metadata(self):
        """Load story metadata from directory"""
        try:
            loader = StoryLoaderFactory.create_loader(self.story_directory)
            input_story = loader.load_story()
            self._story_metadata = input_story.metadata
        except Exception as e:
            raise StoryLoadingError(f"Failed to load story metadata: {e}")

    def _load_chapters(self):
        """Load chapter file references (lazy loading)"""
        try:
            loader = StoryLoaderFactory.create_loader(self.story_directory)
            input_story = loader.load_story()
            
            # Create lazy chapters
            lazy_chapters = []
            for raw_chapter in input_story.chapters:
                if raw_chapter.ref:
                    chapter_file = self.story_directory / raw_chapter.ref
                else:
                    # Fallback to chapter number if no ref
                    chapter_file = self.story_directory / f"{raw_chapter.chapter_number}.xml"
                
                lazy_chapter = LazyChapter(
                    chapter_number=raw_chapter.chapter_number,
                    title=raw_chapter.title,
                    file_path=chapter_file,
                    ref=raw_chapter.ref
                )
                lazy_chapters.append(lazy_chapter)
            
            self._lazy_chapters = ChapterRange(lazy_chapters)
            
        except Exception as e:
            raise StoryLoadingError(f"Failed to load chapter references: {e}")

    # Story Operations
    async def create_story_in_repository(self) -> Story:
        """Create the story in the repository if it doesn't exist"""
        if self._story_id is None:
            # Load all chapters and create InputStory
            input_story = self.get_input_story()
            story = await self._story_repo.store_input_story(input_story, self.owner_id)
            self._story_id = story.id
            return story
        else:
            return await self._story_repo.get_story(self._story_id)

    async def load_chapters_range(self, start: int, count: int) -> List[Chapter]:
        """Load a range of chapters into the repository"""
        if self._story_id is None:
            await self.create_story_in_repository()
        
        if self._story_id is None:
            raise StoryLoadingError("Failed to create story in repository")
        
        # Get the requested chapter range
        lazy_chapters = self.chapters.get_chunk(start, count)
        raw_chapters = [ch.to_raw_chapter() for ch in lazy_chapters]
        
        # Check if chapters already exist in repository
        existing_chapters = await self._story_repo.get_chapters(self._story_id)
        existing_numbers = {ch.chapter_number for ch in existing_chapters}
        
        # Only load chapters that don't exist
        new_raw_chapters = [ch for ch in raw_chapters if ch.chapter_number not in existing_numbers]
        
        if new_raw_chapters:
            from src.schemas.story import ChapterCreate
            chapters_create = [
                ChapterCreate(
                    story_id=self._story_id,
                    chapter_number=ch.chapter_number,
                    title=ch.title,
                    raw_content=ch.content
                )
                for ch in new_raw_chapters
            ]
            await self._story_repo.create_chapters_bulk(chapters_create)
        
        # Return all requested chapters
        all_chapters = await self._story_repo.get_chapters(self._story_id)
        requested_numbers = {ch.chapter_number for ch in lazy_chapters}
        return [ch for ch in all_chapters if ch.chapter_number in requested_numbers]

    def get_input_story(self, chapter_numbers: Optional[List[int]] = None) -> InputStory:
        """Get InputStory with specified chapters (or all if None)"""
        raw_chapters = self.chapters.to_raw_chapters(chapter_numbers)
        
        return InputStory(
            metadata=self.story_metadata,
            chapters=raw_chapters,
            source_path=str(self.workspace_root)
        )

    def get_chapter_content_chunked(self, start: int, count: int) -> str:
        """Get concatenated content for a chunk of chapters"""
        lazy_chapters = self.chapters.get_chunk(start, count)
        return "\n\n".join([f"# Chapter {ch.chapter_number}: {ch.title}\n\n{ch.content}" for ch in lazy_chapters])

    # Wiki Operations
    async def create_wiki_page_in_repository(self) -> WikiPage:
        """Create the wiki page in the repository if it doesn't exist"""
        if self._wiki_page_id is None:
            wiki_page_create = WikiPageCreate(
                title=f"{self.story_metadata.title} Wiki",
                description=f"Wiki for {self.story_metadata.title} by {self.story_metadata.author}",
                is_public=False,
                safe_through_chapter=0,
                creator_id=self.owner_id
            )
            wiki_page = await self._wikipage_repo.create_wiki_page(wiki_page_create)
            self._wiki_page_id = wiki_page.id
            return wiki_page
        else:
            # Repository always returns a valid WikiPage now
            return await self._wikipage_repo.get_wiki_page(self._wiki_page_id)

    async def load_wiki_from_directory(self) -> bool:
        """Load wiki articles from the wiki directory into the repository"""
        if not self.wiki_directory.exists():
            return False
            
        if self._wiki_page_id is None:
            await self.create_wiki_page_in_repository()
            
        # At this point _wiki_page_id should be set, but add safety check
        if self._wiki_page_id is None:
            return False
            
        return await self._wikipage_repo.load_from_directory(str(self.wiki_directory), self._wiki_page_id)

    async def save_wiki_to_directory(self, max_chapter: Optional[int] = None) -> bool:
        """Save wiki articles to the wiki directory"""
        if self._wiki_page_id is None:
            return False
            
        return await self._wikipage_repo.save_to_directory(self._wiki_page_id, str(self.wiki_directory), max_chapter)

    # Writing Operations (Stub for future)
    async def get_writing_status(self) -> Dict[str, Any]:
        """Get status of writing materials (STUB)"""
        return {
            "writing_directory_exists": self.writing_directory.exists(),
            "note": "Writing functionality not yet implemented"
        }

    # Workspace Management
    def validate_workspace(self) -> Dict[str, bool]:
        """Validate workspace directory structure"""
        return {
            "workspace_exists": self.workspace_root.exists(),
            "has_meta_file": (self.workspace_root / "_meta.xml").exists(),
            "has_chapters": any(self.workspace_root.glob("*.xml")),
            "wiki_directory_exists": self.wiki_directory.exists(),
            "writing_directory_exists": self.writing_directory.exists(),
        }

    @classmethod
    def create_workspace(cls, workspace_root: Path, owner_id: UUID) -> 'StoryWorkspace':
        """
        Create a new workspace instance
        
        Args:
            workspace_root: Path to the workspace directory
            owner_id: UUID of the user who owns this workspace
            
        Returns:
            StoryWorkspace instance
        """
        workspace_root = Path(workspace_root)
        if not workspace_root.exists():
            raise StoryLoadingError(f"Workspace directory does not exist: {workspace_root}")
            
        return cls(workspace_root, owner_id)

    @classmethod 
    def discover_workspaces(cls, root_directory: Path) -> List[Path]:
        """
        Discover potential story workspaces in a directory
        
        Args:
            root_directory: Directory to search for workspaces
            
        Returns:
            List of paths that appear to be story workspaces
        """
        workspaces = []
        
        if not root_directory.exists():
            return workspaces
            
        # Look for directories with _meta.xml files
        for path in root_directory.iterdir():
            if path.is_dir() and (path / "_meta.xml").exists():
                workspaces.append(path)
        
        return workspaces 