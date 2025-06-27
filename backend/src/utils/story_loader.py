# backend/src/utils/story_loader.py

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any

class StoryLoader:
    """
    A utility class to load and manage story metadata and chapters
    from a specified directory containing _meta.xml and chapter files.
    """

    def __init__(self, story_folder: Path):
        """
        Initializes the StoryLoader with the path to the story directory.

        Args:
            story_folder: The pathlib.Path object pointing to the story's root directory.
                          This directory is expected to contain '_meta.xml' and chapter files.
        """
        if not story_folder.is_dir():
            raise FileNotFoundError(f"Story folder not found: {story_folder}")

        self.story_folder: Path = story_folder
        self.metadata: Optional[Dict[str, Any]] = None
        self.chapters: List[Dict[str, str]] = []
        self._load_metadata()

    def _load_metadata(self):
        """
        Loads and parses the _meta.xml file to populate story metadata and chapter list.
        """
        meta_file_path = self.story_folder / "_meta.xml"
        if not meta_file_path.is_file():
            raise FileNotFoundError(f"Metadata file '_meta.xml' not found in {self.story_folder}")

        try:
            tree = ET.parse(meta_file_path)
            root = tree.getroot()

            self.metadata = {
                "title": root.findtext("Title", "").strip(),
                "author": root.findtext("Author", "").strip(),
                "synopsis": root.findtext("Synopsis", "").strip(),
                "status": root.findtext("Status", "").strip(),
                "date_created": root.findtext("DateCreated", "").strip(),
                "last_updated": root.findtext("LastUpdated", "").strip(),
                "copyright": root.findtext("Copyright", "").strip(),
            }

            # Extract Genres
            genres_element = root.find("Genres")
            if genres_element is not None:
                self.metadata["genres"] = [
                    genre.get("name", "").strip()
                    for genre in genres_element.findall("Genre")
                    if genre.get("name")
                ]
            else:
                self.metadata["genres"] = []

            # Extract Tags
            tags_element = root.find("Tags")
            if tags_element is not None:
                self.metadata["tags"] = [
                    tag.get("name", "").strip()
                    for tag in tags_element.findall("Tag")
                    if tag.get("name")
                ]
            else:
                self.metadata["tags"] = []

            # Extract Chapters
            chapters_element = root.find("Chapters")
            if chapters_element is not None:
                self.chapters = [
                    {"ref": chapter.get("ref", "").strip(), "title": chapter.get("title", "").strip()}
                    for chapter in chapters_element.findall("Chapter")
                    if chapter.get("ref") and chapter.get("title")
                ]
            else:
                self.chapters = []

        except ET.ParseError as e:
            raise ValueError(f"Error parsing '_meta.xml': {e}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred while loading metadata: {e}")

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Returns the loaded story metadata.

        Returns:
            A dictionary containing story metadata, or None if not loaded.
        """
        return self.metadata

    def get_chapters_list(self) -> List[Dict[str, str]]:
        """
        Returns a list of dictionaries, each containing chapter 'ref' and 'title'.

        Returns:
            A list of chapter dictionaries.
        """
        return self.chapters

    def load_chapter(self, chapter_ref: str, strip_xml_wrapper: bool = False) -> str:
        """
        Loads the content of a specific chapter.

        Args:
            chapter_ref: The 'ref' attribute of the chapter (e.g., "1.xml").
            strip_xml_wrapper: If True, attempts to strip a top-level <Chapter> XML tag.

        Returns:
            The content of the chapter file as a string.

        Raises:
            FileNotFoundError: If the chapter file does not exist.
            ValueError: If the chapter_ref is invalid or empty.
        """
        if not chapter_ref:
            raise ValueError("Chapter reference cannot be empty.")

        chapter_file_path = self.story_folder / chapter_ref
        if not chapter_file_path.is_file():
            raise FileNotFoundError(f"Chapter file not found: {chapter_file_path}")

        content = chapter_file_path.read_text(encoding="utf-8").strip()

        if strip_xml_wrapper:
            # Attempt to parse as XML and strip top-level <Chapter> tag if present
            try:
                root = ET.fromstring(content)
                if root.tag == "Chapter":
                    # Extract all text content directly under the Chapter tag
                    # and also from its sub-elements, preserving structure within the chapter.
                    # This handles cases where content might be mixed with child XML tags.
                    return "".join(root.itertext()).strip()
                else:
                    return content
            except ET.ParseError:
                # Not valid XML, or not a top-level <Chapter> tag, return original content
                return content
        else:
            return content

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the StoryLoader object.
        """
        return f"StoryLoader(story_folder=Path('{self.story_folder.as_posix()}'))"

    def __str__(self) -> str:
        """
        Returns a user-friendly string representation of the StoryLoader object,
        summarizing the loaded story.
        """
        if self.metadata:
            title = self.metadata.get("title", "Unknown Title")
            author = self.metadata.get("author", "Unknown Author")
            num_chapters = len(self.chapters)
            return (
                f"Story: \"{title}\" by {author}\n"
                f"Located at: {self.story_folder.name}/\n"
                f"Chapters: {num_chapters}"
            )
        return f"StoryLoader for {self.story_folder.name}/ (Metadata not loaded)"
