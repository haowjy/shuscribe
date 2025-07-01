"""
File-Based Story Repository Implementation

Stores story content in the story/ directory with separate files for chapters and metadata.
Structure:
- story/metadata.json - Story metadata
- story/chapters/ - Published chapters as numbered files  
- story/drafts/ - Draft chapters
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from src.database.interfaces.story import IStoryRepository
from src.database.models.story import Chapter, ChapterCreate, ChapterUpdate, ChapterStatus, StoryMetadata, StoryMetadataCreate, StoryMetadataUpdate
from src.database.file.utils import FileManager, ensure_workspace_structure


class FileStoryRepository(IStoryRepository):
    """File-based story repository"""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.file_manager = FileManager(workspace_path)
        
        # Ensure workspace structure exists
        ensure_workspace_structure(workspace_path)
        
        # File paths
        structure = self.file_manager.get_workspace_structure()
        self.metadata_file = structure['story'] / "metadata.json"
        self.chapters_dir = structure['chapters']
        self.drafts_dir = structure['drafts']
        self.chapters_index_file = structure['system'] / "chapters_index.json"
    
    def _get_chapter_filename(self, chapter_number: int, status: ChapterStatus = ChapterStatus.PUBLISHED) -> str:
        """Get filename for chapter based on number and status"""
        if status == ChapterStatus.DRAFT:
            return f"chapter_{chapter_number:03d}_draft.md"
        else:
            return f"chapter_{chapter_number:03d}.md"
    
    def _get_chapter_file_path(self, chapter_number: int, status: ChapterStatus = ChapterStatus.PUBLISHED) -> Path:
        """Get full file path for chapter"""
        filename = self._get_chapter_filename(chapter_number, status)
        if status == ChapterStatus.DRAFT:
            return self.drafts_dir / filename
        else:
            return self.chapters_dir / filename
    
    def _load_chapters_index(self) -> Dict[str, dict]:
        """Load chapters index"""
        return self.file_manager.read_json_file(self.chapters_index_file, {})
    
    def _save_chapters_index(self, index: Dict[str, dict]) -> None:
        """Save chapters index"""
        self.file_manager.write_json_file(self.chapters_index_file, index)
    
    def _chapter_to_markdown(self, chapter: Chapter) -> str:
        """Convert chapter to markdown content with frontmatter"""
        frontmatter = f"""---
id: {chapter.id}
title: {chapter.title}
chapter_number: {chapter.chapter_number}
status: {chapter.status.value}
word_count: {chapter.word_count}
created_at: {chapter.created_at.isoformat()}
updated_at: {chapter.updated_at.isoformat() if chapter.updated_at else ""}
published_at: {chapter.published_at.isoformat() if chapter.published_at else ""}
---

# {chapter.title}

{chapter.content}
"""
        return frontmatter
    
    def _markdown_to_chapter(self, content: str, workspace_id: UUID) -> Chapter:
        """Parse markdown content to Chapter object"""
        lines = content.strip().split('\n')
        
        # Parse frontmatter
        if lines[0] == '---':
            frontmatter_end = lines.index('---', 1)
            frontmatter_lines = lines[1:frontmatter_end]
            content_lines = lines[frontmatter_end + 1:]
        else:
            raise ValueError("Chapter file missing frontmatter")
        
        # Parse frontmatter fields
        frontmatter = {}
        for line in frontmatter_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        
        # Extract content (skip title line)
        chapter_content = '\n'.join(content_lines)
        if chapter_content.startswith(f"# {frontmatter.get('title', '')}"):
            # Remove title line if present
            content_lines = chapter_content.split('\n')[2:]  # Skip title and empty line
            chapter_content = '\n'.join(content_lines)
        
        return Chapter(
            id=UUID(frontmatter['id']),
            workspace_id=workspace_id,
            title=frontmatter['title'],
            content=chapter_content.strip(),
            chapter_number=int(frontmatter['chapter_number']),
            status=ChapterStatus(frontmatter['status']),
            word_count=int(frontmatter.get('word_count', 0)),
            created_at=datetime.fromisoformat(frontmatter['created_at']),
            updated_at=datetime.fromisoformat(frontmatter['updated_at']) if frontmatter.get('updated_at') else None,
            published_at=datetime.fromisoformat(frontmatter['published_at']) if frontmatter.get('published_at') else None
        )

    # Chapter operations
    async def get_chapter(self, id: UUID) -> Optional[Chapter]:
        """Get chapter by ID"""
        index = self._load_chapters_index()
        
        for chapter_data in index.values():
            if chapter_data['id'] == str(id):
                chapter_number = chapter_data['chapter_number']
                status = ChapterStatus(chapter_data['status'])
                file_path = self._get_chapter_file_path(chapter_number, status)
                
                if file_path.exists():
                    content = self.file_manager.read_text_file(file_path)
                    return self._markdown_to_chapter(content, UUID(chapter_data['workspace_id']))
        
        return None

    async def get_chapter_by_number(self, workspace_id: UUID, chapter_number: int) -> Optional[Chapter]:
        """Get chapter by workspace and chapter number"""
        index = self._load_chapters_index()
        chapter_key = f"{workspace_id}_{chapter_number}"
        
        if chapter_key in index:
            chapter_data = index[chapter_key]
            status = ChapterStatus(chapter_data['status'])
            file_path = self._get_chapter_file_path(chapter_number, status)
            
            if file_path.exists():
                content = self.file_manager.read_text_file(file_path)
                return self._markdown_to_chapter(content, workspace_id)
        
        return None

    async def get_chapters_by_workspace(self, workspace_id: UUID) -> List[Chapter]:
        """Get all chapters for workspace"""
        index = self._load_chapters_index()
        chapters = []
        
        for chapter_data in index.values():
            if chapter_data['workspace_id'] == str(workspace_id):
                chapter_number = chapter_data['chapter_number']
                status = ChapterStatus(chapter_data['status'])
                file_path = self._get_chapter_file_path(chapter_number, status)
                
                if file_path.exists():
                    content = self.file_manager.read_text_file(file_path)
                    chapters.append(self._markdown_to_chapter(content, workspace_id))
        
        return sorted(chapters, key=lambda c: c.chapter_number)

    async def get_published_chapters(self, workspace_id: UUID) -> List[Chapter]:
        """Get only published chapters for workspace"""
        all_chapters = await self.get_chapters_by_workspace(workspace_id)
        return [chapter for chapter in all_chapters if chapter.status == ChapterStatus.PUBLISHED]

    async def create_chapter(self, chapter_data: ChapterCreate) -> Chapter:
        """Create new chapter"""
        chapter_id = uuid4()
        
        # Calculate word count
        word_count = len(chapter_data.content.split())
        
        chapter = Chapter(
            id=chapter_id,
            workspace_id=chapter_data.workspace_id,
            title=chapter_data.title,
            content=chapter_data.content,
            chapter_number=chapter_data.chapter_number,
            status=chapter_data.status,
            word_count=word_count,
            created_at=datetime.now(),
            updated_at=None,
            published_at=datetime.now() if chapter_data.status == ChapterStatus.PUBLISHED else None
        )
        
        # Save to file
        file_path = self._get_chapter_file_path(chapter.chapter_number, chapter.status)
        markdown_content = self._chapter_to_markdown(chapter)
        self.file_manager.write_text_file(file_path, markdown_content)
        
        # Update index
        index = self._load_chapters_index()
        chapter_key = f"{chapter.workspace_id}_{chapter.chapter_number}"
        index[chapter_key] = {
            "id": str(chapter.id),
            "workspace_id": str(chapter.workspace_id),
            "chapter_number": chapter.chapter_number,
            "status": chapter.status.value,
            "title": chapter.title
        }
        self._save_chapters_index(index)
        
        return chapter

    async def update_chapter(self, chapter_id: UUID, chapter_data: ChapterUpdate) -> Chapter:
        """Update chapter"""
        chapter = await self.get_chapter(chapter_id)
        if not chapter:
            raise ValueError("Chapter not found")
        
        old_file_path = self._get_chapter_file_path(chapter.chapter_number, chapter.status)
        
        # Update fields
        update_dict = chapter_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(chapter, field):
                setattr(chapter, field, value)
        
        # Recalculate word count if content changed
        if 'content' in update_dict:
            chapter.word_count = len(chapter.content.split())
        
        chapter.updated_at = datetime.now()
        
        # If status changed, need to move file
        new_file_path = self._get_chapter_file_path(chapter.chapter_number, chapter.status)
        if old_file_path != new_file_path:
            # Delete old file
            self.file_manager.delete_file(old_file_path)
        
        # Save to new/same file
        markdown_content = self._chapter_to_markdown(chapter)
        self.file_manager.write_text_file(new_file_path, markdown_content)
        
        # Update index
        index = self._load_chapters_index()
        chapter_key = f"{chapter.workspace_id}_{chapter.chapter_number}"
        index[chapter_key].update({
            "status": chapter.status.value,
            "title": chapter.title
        })
        self._save_chapters_index(index)
        
        return chapter

    async def delete_chapter(self, chapter_id: UUID) -> bool:
        """Delete chapter"""
        chapter = await self.get_chapter(chapter_id)
        if not chapter:
            return False
        
        # Delete file
        file_path = self._get_chapter_file_path(chapter.chapter_number, chapter.status)
        self.file_manager.delete_file(file_path)
        
        # Remove from index
        index = self._load_chapters_index()
        chapter_key = f"{chapter.workspace_id}_{chapter.chapter_number}"
        if chapter_key in index:
            del index[chapter_key]
            self._save_chapters_index(index)
        
        return True

    # Story metadata operations
    async def get_story_metadata(self, workspace_id: UUID) -> StoryMetadata:
        """Get story metadata"""
        metadata_data = self.file_manager.read_json_file(self.metadata_file)
        
        if not metadata_data or metadata_data.get('workspace_id') != str(workspace_id):
            raise ValueError("Story metadata not found")
        
        return StoryMetadata(
            id=UUID(metadata_data['id']),
            workspace_id=UUID(metadata_data['workspace_id']),
            title=metadata_data['title'],
            author=metadata_data['author'],
            synopsis=metadata_data.get('synopsis', ''),
            genres=metadata_data.get('genres', []),
            tags=metadata_data.get('tags', []),
            total_chapters=metadata_data.get('total_chapters', 0),
            published_chapters=metadata_data.get('published_chapters', 0),
            total_word_count=metadata_data.get('total_word_count', 0),
            publication_status=metadata_data.get('publication_status', 'draft'),
            first_published_at=datetime.fromisoformat(metadata_data['first_published_at']) if metadata_data.get('first_published_at') else None,
            last_updated_at=datetime.fromisoformat(metadata_data['last_updated_at']) if metadata_data.get('last_updated_at') else None,
            settings=metadata_data.get('settings', {}),
            created_at=datetime.fromisoformat(metadata_data['created_at']),
            updated_at=datetime.fromisoformat(metadata_data['updated_at']) if metadata_data.get('updated_at') else None
        )

    async def create_story_metadata(self, workspace_id: UUID, title: str, author: str, 
                                   synopsis: str = "", genres: Optional[List[str]] = None, tags: Optional[List[str]] = None,
                                   total_chapters: int = 0, publication_status: str = "draft",
                                   settings: Optional[Dict] = None) -> StoryMetadata:
        """Create story metadata"""
        metadata_id = uuid4()
        metadata = StoryMetadata(
            id=metadata_id,
            workspace_id=workspace_id,
            title=title,
            author=author,
            synopsis=synopsis,
            genres=genres or [],
            tags=tags or [],
            total_chapters=total_chapters,
            published_chapters=0,
            total_word_count=0,
            publication_status=publication_status,
            first_published_at=None,
            last_updated_at=None,
            settings=settings or {},
            created_at=datetime.now(),
            updated_at=None
        )
        
        metadata_data = {
            "id": str(metadata.id),
            "workspace_id": str(metadata.workspace_id),
            "title": metadata.title,
            "author": metadata.author,
            "synopsis": metadata.synopsis,
            "genres": metadata.genres,
            "tags": metadata.tags,
            "total_chapters": metadata.total_chapters,
            "published_chapters": metadata.published_chapters,
            "total_word_count": metadata.total_word_count,
            "publication_status": metadata.publication_status,
            "first_published_at": None,
            "last_updated_at": None,
            "settings": metadata.settings,
            "created_at": metadata.created_at.isoformat(),
            "updated_at": None
        }
        
        self.file_manager.write_json_file(self.metadata_file, metadata_data)
        return metadata

    async def update_story_metadata(self, workspace_id: UUID, **updates) -> StoryMetadata:
        """Update story metadata"""
        current_metadata = await self.get_story_metadata(workspace_id)
        if not current_metadata:
            raise ValueError("Story metadata not found")
        
        # Update fields
        for field, value in updates.items():
            if hasattr(current_metadata, field):
                setattr(current_metadata, field, value)
        
        current_metadata.updated_at = datetime.now()
        
        # Save updated metadata
        updated_data = {
            "id": str(current_metadata.id),
            "workspace_id": str(current_metadata.workspace_id),
            "title": current_metadata.title,
            "author": current_metadata.author,
            "synopsis": current_metadata.synopsis,
            "genres": current_metadata.genres,
            "tags": current_metadata.tags,
            "total_chapters": current_metadata.total_chapters,
            "published_chapters": current_metadata.published_chapters,
            "total_word_count": current_metadata.total_word_count,
            "publication_status": current_metadata.publication_status,
            "first_published_at": current_metadata.first_published_at.isoformat() if current_metadata.first_published_at else None,
            "last_updated_at": current_metadata.last_updated_at.isoformat() if current_metadata.last_updated_at else None,
            "settings": current_metadata.settings,
            "created_at": current_metadata.created_at.isoformat(),
            "updated_at": current_metadata.updated_at.isoformat()
        }
        
        self.file_manager.write_json_file(self.metadata_file, updated_data)
        return current_metadata

    async def refresh_chapter_stats(self, workspace_id: UUID) -> StoryMetadata:
        """Refresh chapter statistics in story metadata"""
        metadata = await self.get_story_metadata(workspace_id)
        if not metadata:
            raise ValueError("Story metadata not found")
        
        # Get all chapters and update stats
        chapters = await self.get_chapters_by_workspace(workspace_id)
        published_chapters = [c for c in chapters if c.status == ChapterStatus.PUBLISHED]
        
        # Update the metadata object
        metadata.published_chapters = len(published_chapters)
        metadata.total_word_count = sum(c.word_count for c in chapters)
        
        if published_chapters:
            # Get first published date from published chapters
            published_dates = [c.published_at for c in published_chapters if c.published_at]
            if published_dates:
                metadata.first_published_at = min(published_dates)
            
            # Get last updated date from all chapters
            updated_dates = [c.updated_at for c in chapters if c.updated_at]
            if updated_dates:
                metadata.last_updated_at = max(updated_dates)
            else:
                metadata.last_updated_at = datetime.now()
        
        metadata.updated_at = datetime.now()
        
        # Save updated metadata
        updated_data = {
            "id": str(metadata.id),
            "workspace_id": str(metadata.workspace_id),
            "title": metadata.title,
            "author": metadata.author,
            "synopsis": metadata.synopsis,
            "genres": metadata.genres,
            "tags": metadata.tags,
            "total_chapters": metadata.total_chapters,
            "published_chapters": metadata.published_chapters,
            "total_word_count": metadata.total_word_count,
            "publication_status": metadata.publication_status,
            "first_published_at": metadata.first_published_at.isoformat() if metadata.first_published_at else None,
            "last_updated_at": metadata.last_updated_at.isoformat() if metadata.last_updated_at else None,
            "settings": metadata.settings,
            "created_at": metadata.created_at.isoformat(),
            "updated_at": metadata.updated_at.isoformat()
        }
        
        self.file_manager.write_json_file(self.metadata_file, updated_data)
        return metadata 