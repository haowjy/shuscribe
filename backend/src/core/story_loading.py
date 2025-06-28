"""
Story loading functionality for ShuScribe
Handles loading stories from various input sources (directories, files, etc.)
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any

from src.schemas.story import InputStory, RawStoryMetadata, RawChapter


class StoryLoadingError(Exception):
    """Raised when story loading fails"""
    pass


class DirectoryStoryLoader:
    """
    Loads stories from directory structure with _meta.xml and chapter files.
    
    Expected structure:
    story_directory/
    ├── _meta.xml          # Story metadata
    ├── 1.xml              # Chapter files
    ├── 2.xml
    └── ...
    """

    def __init__(self, story_directory: Path):
        """
        Initialize loader with story directory path.

        Args:
            story_directory: Path to directory containing story files
            
        Raises:
            StoryLoadingError: If directory doesn't exist or is invalid
        """
        if not story_directory.is_dir():
            raise StoryLoadingError(f"Story directory not found: {story_directory}")

        self.story_directory = story_directory

    def load_story(self, strip_xml_wrapper: bool = True) -> InputStory:
        """
        Load complete story with metadata and chapters.

        Args:
            strip_xml_wrapper: Whether to strip <Chapter> XML wrapper from content
            
        Returns:
            InputStory: Complete story data
            
        Raises:
            StoryLoadingError: If loading fails
        """
        try:
            # Load metadata
            metadata = self._load_metadata()
            
            # Load chapters
            chapters = self._load_chapters(metadata, strip_xml_wrapper)
            
            return InputStory(
                metadata=metadata,
                chapters=chapters,
                source_path=str(self.story_directory)
            )
            
        except Exception as e:
            raise StoryLoadingError(f"Failed to load story from {self.story_directory}: {e}")

    def _load_metadata(self) -> RawStoryMetadata:
        """Load and parse story metadata from _meta.xml"""
        meta_file_path = self.story_directory / "_meta.xml"
        if not meta_file_path.is_file():
            raise StoryLoadingError(f"Metadata file '_meta.xml' not found in {self.story_directory}")

        try:
            tree = ET.parse(meta_file_path)
            root = tree.getroot()

            # Extract basic metadata
            metadata_dict = {
                "title": root.findtext("Title", "").strip(),
                "author": root.findtext("Author", "").strip(),
                "synopsis": root.findtext("Synopsis", "").strip(),
                "status": root.findtext("Status", "").strip(),
                "date_created": root.findtext("DateCreated", "").strip() or None,
                "last_updated": root.findtext("LastUpdated", "").strip() or None,
                "copyright": root.findtext("Copyright", "").strip() or None,
            }

            # Extract genres
            genres_element = root.find("Genres")
            if genres_element is not None:
                metadata_dict["genres"] = [
                    genre.get("name", "").strip()
                    for genre in genres_element.findall("Genre")
                    if genre.get("name")
                ]
            else:
                metadata_dict["genres"] = []

            # Extract tags
            tags_element = root.find("Tags")
            if tags_element is not None:
                metadata_dict["tags"] = [
                    tag.get("name", "").strip()
                    for tag in tags_element.findall("Tag")
                    if tag.get("name")
                ]
            else:
                metadata_dict["tags"] = []

            return RawStoryMetadata(**metadata_dict)

        except ET.ParseError as e:
            raise StoryLoadingError(f"Error parsing '_meta.xml': {e}")

    def _load_chapters(self, metadata: RawStoryMetadata, strip_xml_wrapper: bool) -> List[RawChapter]:
        """Load chapters based on metadata chapter references"""
        chapters = []
        
        # First, try to get chapter list from metadata if it exists
        meta_file_path = self.story_directory / "_meta.xml"
        chapter_refs = self._extract_chapter_refs_from_meta(meta_file_path)
        
        if chapter_refs:
            # Use metadata chapter references
            for chapter_info in chapter_refs:
                content = self._load_chapter_content(chapter_info["ref"], strip_xml_wrapper)
                chapters.append(RawChapter(
                    chapter_number=len(chapters) + 1,  # Sequential numbering
                    title=chapter_info["title"],
                    content=content,
                    ref=chapter_info["ref"]
                ))
        else:
            # Fall back to scanning directory for XML files
            xml_files = sorted([f for f in self.story_directory.glob("*.xml") if f.name != "_meta.xml"])
            
            for i, xml_file in enumerate(xml_files, 1):
                content = self._load_chapter_content(xml_file.name, strip_xml_wrapper)
                # Try to extract title from content or use filename
                title = self._extract_title_from_content(content) or f"Chapter {i}"
                
                chapters.append(RawChapter(
                    chapter_number=i,
                    title=title,
                    content=content,
                    ref=xml_file.name
                ))
        
        if not chapters:
            raise StoryLoadingError(f"No chapters found in {self.story_directory}")
            
        return chapters

    def _extract_chapter_refs_from_meta(self, meta_file_path: Path) -> List[Dict[str, str]]:
        """Extract chapter references from metadata file"""
        try:
            tree = ET.parse(meta_file_path)
            root = tree.getroot()
            
            chapters_element = root.find("Chapters")
            if chapters_element is not None:
                return [
                    {"ref": chapter.get("ref", "").strip(), "title": chapter.get("title", "").strip()}
                    for chapter in chapters_element.findall("Chapter")
                    if chapter.get("ref") and chapter.get("title")
                ]
            return []
        except:
            return []

    def _load_chapter_content(self, chapter_ref: str, strip_xml_wrapper: bool) -> str:
        """Load content from a chapter file"""
        if not chapter_ref:
            raise StoryLoadingError("Chapter reference cannot be empty")

        chapter_file_path = self.story_directory / chapter_ref
        if not chapter_file_path.is_file():
            raise StoryLoadingError(f"Chapter file not found: {chapter_file_path}")

        content = chapter_file_path.read_text(encoding="utf-8").strip()

        if strip_xml_wrapper:
            # Attempt to parse as XML and strip top-level <Chapter> tag if present
            try:
                root = ET.fromstring(content)
                if root.tag == "Chapter":
                    # Extract all text content, preserving structure
                    return "".join(root.itertext()).strip()
            except ET.ParseError:
                # Not valid XML or not a <Chapter> tag, return original content
                pass

        return content

    def _extract_title_from_content(self, content: str) -> Optional[str]:
        """Try to extract chapter title from content (look for markdown headers, etc.)"""
        lines = content.split('\n')
        for line in lines[:5]:  # Check first few lines
            line = line.strip()
            if line.startswith('#'):
                return line.lstrip('#').strip()
            if line.startswith('[Chapter') and line.endswith(']'):
                return line.strip('[]')
        return None


class StoryLoaderFactory:
    """Factory for creating appropriate story loaders based on input source"""
    
    @staticmethod
    def create_loader(source_path: Path) -> DirectoryStoryLoader:
        """
        Create appropriate loader based on source path.
        
        Args:
            source_path: Path to story source (directory, file, etc.)
            
        Returns:
            Story loader instance
            
        Raises:
            StoryLoadingError: If source type is unsupported
        """
        if source_path.is_dir():
            return DirectoryStoryLoader(source_path)
        else:
            raise StoryLoadingError(f"Unsupported source type: {source_path}")
    
    @staticmethod
    def load_story(source_path: Path, **kwargs) -> InputStory:
        """
        Convenience method to load story from path.
        
        Args:
            source_path: Path to story source
            **kwargs: Additional arguments passed to loader
            
        Returns:
            InputStory: Loaded story data
        """
        loader = StoryLoaderFactory.create_loader(source_path)
        return loader.load_story(**kwargs)


# Backward compatibility - keeping the old StoryLoader interface
class StoryLoader:
    """
    Legacy StoryLoader interface for backward compatibility.
    Wraps the new DirectoryStoryLoader.
    """
    
    def __init__(self, story_folder: Path):
        self._loader = DirectoryStoryLoader(story_folder)
        self._story: Optional[InputStory] = None
        
    def _ensure_loaded(self):
        """Ensure story is loaded"""
        if self._story is None:
            self._story = self._loader.load_story()
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Get story metadata as dict (legacy interface)"""
        self._ensure_loaded()
        if self._story:
            return self._story.metadata.model_dump()
        return None
    
    def get_chapters_list(self) -> List[Dict[str, str]]:
        """Get chapters list (legacy interface)"""
        self._ensure_loaded()
        if self._story:
            return [
                {"ref": ch.ref or f"{ch.chapter_number}.xml", "title": ch.title}
                for ch in self._story.chapters
            ]
        return []
    
    def load_chapter(self, chapter_ref: str, strip_xml_wrapper: bool = False) -> str:
        """Load chapter content (legacy interface)"""
        return self._loader._load_chapter_content(chapter_ref, strip_xml_wrapper) 