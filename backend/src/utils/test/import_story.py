"""
Story Import Script for ShuScribe

Imports stories from XML directory format into the file-based database structure.
Converts from the legacy XML format to the new database models and file structure.
"""

import asyncio
import sys
from pathlib import Path
from typing import cast
from uuid import UUID, uuid4
from datetime import datetime

from src.database.models.repositories import FileRepositories
from src.database.models.story import Chapter, ChapterCreate, ChapterStatus, StoryMetadata, StoryMetadataCreate
from src.database.factory import get_repositories
from src.database.models.workspace import Workspace, WorkspaceCreate
from src.database.models.user import User, UserCreate, SubscriptionTier


class StoryImporter:
    """Imports stories from XML directory format into ShuScribe database"""
    
    def __init__(self, workspace_path: Path):
        """Initialize importer with target workspace path"""
        self.workspace_path = workspace_path
        self.repos: FileRepositories = cast(FileRepositories, get_repositories(backend="file", workspace_path=workspace_path))
        
    async def import_story_from_directory(self, story_directory: Path, strip_xml_wrapper: bool = True) -> dict:
        """
        Import a story from XML directory format
        
        Args:
            story_directory: Path to directory containing _meta.xml and chapter files
            strip_xml_wrapper: Whether to strip XML wrapper tags from chapter content
            
        Returns:
            Dict with imported story information
        """
        print(f"Importing story from: {story_directory}")
        
        # Load the story using the existing loader
        story_data = self._load_story_from_xml(story_directory, strip_xml_wrapper)
        
        # Create or get user
        user = await self._get_or_create_user()
        
        # Create or get workspace 
        workspace = await self._get_or_create_workspace(user.id, story_data)
        
        # Create story metadata
        story_metadata = await self._create_story_metadata(workspace.id, story_data)
        
        # Import chapters
        imported_chapters = await self._import_chapters(workspace.id, story_data["chapters"])
        
        # Refresh stats
        await self.repos.story.refresh_chapter_stats(workspace.id)
        
        result = {
            "workspace_id": str(workspace.id),
            "story_title": story_metadata.title,
            "chapters_imported": len(imported_chapters),
            "workspace_path": str(self.workspace_path)
        }
        
        print(f"✅ Successfully imported '{story_metadata.title}' with {len(imported_chapters)} chapters")
        return result
    
    def _load_story_from_xml(self, story_directory: Path, strip_xml_wrapper: bool) -> dict:
        """Load story data from XML directory using the existing loader logic"""
        import xml.etree.ElementTree as ET
        
        # Load metadata
        meta_file = story_directory / "_meta.xml"
        if not meta_file.exists():
            raise ValueError(f"No _meta.xml found in {story_directory}")
        
        tree = ET.parse(meta_file)
        root = tree.getroot()
        
        # Handle StoryMetadata wrapper if present
        if root.tag == "StoryMetadata":
            metadata_root = root
        else:
            metadata_root = root.find("StoryMetadata")
            if metadata_root is None:
                metadata_root = root  # Fallback to root if no wrapper
        
        # Extract metadata
        metadata = {
            "title": metadata_root.findtext("Title", "").strip(),
            "author": metadata_root.findtext("Author", "").strip(),
            "synopsis": metadata_root.findtext("Synopsis", "").strip(),
            "status": metadata_root.findtext("Status", "").strip(),
            "date_created": metadata_root.findtext("DateCreated", "").strip() or None,
            "last_updated": metadata_root.findtext("LastUpdated", "").strip() or None,
            "copyright": metadata_root.findtext("Copyright", "").strip() or None,
        }
        
        # Extract genres
        genres_element = metadata_root.find("Genres")
        genres = []
        if genres_element is not None:
            genres = [
                genre.get("name", "").strip()
                for genre in genres_element.findall("Genre")
                if genre.get("name")
            ]
        
        # Extract tags  
        tags_element = metadata_root.find("Tags")
        tags = []
        if tags_element is not None:
            tags = [
                tag.get("name", "").strip()
                for tag in tags_element.findall("Tag")
                if tag.get("name")
            ]
        
        # Load chapters - pass metadata_root to use chapter list
        chapters = self._load_chapters_from_xml(story_directory, strip_xml_wrapper, metadata_root)
        
        return {
            "title": metadata["title"],
            "author": metadata["author"],
            "synopsis": metadata["synopsis"],
            "status": metadata["status"],
            "genres": genres,
            "tags": tags,
            "date_created": metadata["date_created"],
            "last_updated": metadata["last_updated"],
            "copyright": metadata["copyright"],
            "chapters": chapters
        }
    
    def _load_chapters_from_xml(self, story_directory: Path, strip_xml_wrapper: bool, metadata_root=None) -> list:
        """Load chapters using chapter list from _meta.xml if available, otherwise scan directory"""
        import xml.etree.ElementTree as ET
        
        chapters = []
        
        # First try to use chapter list from metadata
        if metadata_root is not None:
            print(f"🔍 Checking metadata_root for chapters...")
            chapters_element = metadata_root.find("Chapters")
            if chapters_element is not None:
                print(f"✅ Found Chapters element in metadata")
                chapter_elements = chapters_element.findall("Chapter")
                print(f"📋 Found {len(chapter_elements)} chapter elements (including any in comments)")
                if chapter_elements:
                    
                    for i, chapter_elem in enumerate(chapter_elements, 1):
                        ref = chapter_elem.get("ref", "")
                        title = chapter_elem.get("title", f"Chapter {i}")
                        
                        if ref:
                            xml_file = story_directory / ref
                            if xml_file.exists():
                                content = xml_file.read_text(encoding="utf-8").strip()
                                
                                if strip_xml_wrapper:
                                    content = self._strip_xml_wrapper(content)
                                
                                chapters.append({
                                    "chapter_number": i,
                                    "title": title,
                                    "content": content,
                                    "ref": ref
                                })
                            else:
                                print(f"⚠️  Chapter file not found: {ref} (skipping)")
                    
                    if chapters:
                        print(f"✅ Successfully loaded {len(chapters)} chapters from metadata")
                        return chapters
                    else:
                        print("⚠️  No valid chapter files found from metadata, falling back to directory scan")
        
        # Fallback: scan directory for numbered XML files (original behavior)
        print("📁 Scanning directory for numbered XML files...")
        xml_files = sorted([
            f for f in story_directory.glob("*.xml") 
            if f.name != "_meta.xml" and f.name.replace(".xml", "").isdigit()
        ], key=lambda x: int(x.name.replace(".xml", "")))
        
        for xml_file in xml_files:
            chapter_number = int(xml_file.name.replace(".xml", ""))
            content = xml_file.read_text(encoding="utf-8").strip()
            
            # Extract title and content
            title = self._extract_chapter_title(content) or f"Chapter {chapter_number}"
            
            if strip_xml_wrapper:
                content = self._strip_xml_wrapper(content)
            
            chapters.append({
                "chapter_number": chapter_number,
                "title": title,
                "content": content,
                "ref": xml_file.name
            })
        
        return chapters
    
    def _extract_chapter_title(self, content: str) -> str:
        """Extract chapter title from content"""
        import xml.etree.ElementTree as ET
        
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
    
    def _strip_xml_wrapper(self, content: str) -> str:
        """Strip XML wrapper tags from content"""
        import xml.etree.ElementTree as ET
        
        try:
            root = ET.fromstring(content)
            if root.tag == "Chapter":
                return "".join(root.itertext()).strip()
        except ET.ParseError:
            pass
        
        return content
    
    async def _get_or_create_user(self) -> User:
        """Get or create the local user"""
        try:
            user = await self.repos.user.get_current_user()
            return user
        except:
            # Create default user
            user_data = UserCreate(
                email="author@local.dev",
                display_name="Story Author",
                subscription_tier=SubscriptionTier.LOCAL,
                preferences={}
            )
            return await self.repos.user.create(user_data)
    
    async def _get_or_create_workspace(self, user_id: UUID, story_data: dict) -> Workspace:
        """Get or create workspace for the story"""
        workspace_data = WorkspaceCreate(
            name=story_data["title"] or "Imported Story",
            description=story_data["synopsis"] or "",
            owner_id=user_id,
            arcs=[],  # We'll create arcs later if needed
            settings={
                "import_source": "xml_directory",
                "import_date": datetime.now().isoformat(),
                "original_author": story_data["author"],
                "original_status": story_data["status"]
            }
        )
        
        return await self.repos.workspace.create(workspace_data)
    
    async def _create_story_metadata(self, workspace_id: UUID, story_data: dict) -> StoryMetadata:
        """Create story metadata"""
        # Map status to publication_status
        status_mapping = {
            "Complete": "completed",
            "In Progress": "in_progress", 
            "On Hiatus": "on_hiatus",
            "Discontinued": "discontinued",
            "Draft": "draft"
        }
        
        publication_status = status_mapping.get(story_data.get("status", ""), "draft")
        total_chapters = len(story_data.get("chapters", []))
        
        return await self.repos.story.create_story_metadata(
            workspace_id=workspace_id,
            title=story_data["title"] or "Untitled Story",
            author=story_data["author"] or "Unknown Author",
            synopsis=story_data.get("synopsis", ""),
            genres=story_data.get("genres", []),
            tags=story_data.get("tags", []),
            total_chapters=total_chapters,
            publication_status=publication_status,
            settings={
                "import_source": "xml_directory",
                "import_date": datetime.now().isoformat(),
                "original_status": story_data.get("status", ""),
                "date_created": story_data.get("date_created"),
                "last_updated": story_data.get("last_updated"),
                "copyright": story_data.get("copyright")
            }
        )
    
    async def _import_chapters(self, workspace_id: UUID, chapters_data: list) -> list[Chapter]:
        """Import all chapters"""
        imported_chapters = []
        
        for chapter_data in chapters_data:
            chapter_create = ChapterCreate(
                workspace_id=workspace_id,
                title=chapter_data["title"],
                content=chapter_data["content"],
                chapter_number=chapter_data["chapter_number"],
                status=ChapterStatus.PUBLISHED,  # Assume imported chapters are published
                summary=None,
                tags=[],
                metadata={
                    "imported_from": chapter_data.get("ref", ""),
                    "import_date": datetime.now().isoformat()
                }
            )
            
            chapter = await self.repos.story.create_chapter(chapter_create)
            imported_chapters.append(chapter)
            print(f"  📄 Imported: {chapter.title}")
        
        return imported_chapters


def _create_temp_workspace_path(base_name: str) -> Path:
    """Create a unique temporary workspace path"""
    # Navigate from src/utils/test to backend root
    backend_root = Path(__file__).parent.parent.parent.parent
    temp_dir = backend_root / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    # Create unique temp workspace name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_workspace_path = temp_dir / f"{base_name}_{timestamp}"
    
    return temp_workspace_path


def move_workspace_from_temp(temp_path: Path, final_path: Path) -> bool:
    """Move workspace from temp to final location"""
    try:
        if final_path.exists():
            print(f"⚠️  Final workspace already exists: {final_path}")
            print("   You can either:")
            print(f"   1. Remove existing: rm -rf {final_path}")
            print(f"   2. Use temp workspace: {temp_path}")
            return False
        
        # Move from temp to final location
        temp_path.rename(final_path)
        print(f"📦 Moved workspace from temp to: {final_path}")
        return True
    except Exception as e:
        print(f"❌ Error moving workspace: {e}")
        return False


async def import_pokemon_amber():
    """Import the Pokemon Amber story specifically"""
    
    # Paths - navigate from src/utils/test to backend root
    backend_root = Path(__file__).parent.parent.parent.parent
    pokemon_amber_dir = backend_root / "tests" / "resources" / "pokemon_amber" / "story"
    temp_workspace_path = _create_temp_workspace_path("workspace_pokemon_amber")
    final_workspace_path = backend_root / "workspace_pokemon_amber"
    
    if not pokemon_amber_dir.exists():
        print(f"❌ Pokemon Amber directory not found: {pokemon_amber_dir}")
        return
    
    print(f"📁 Creating temporary workspace: {temp_workspace_path}")
    
    # Create temp workspace directory
    temp_workspace_path.mkdir(parents=True, exist_ok=True)
    
    # Import the story to temp location
    importer = StoryImporter(temp_workspace_path)
    result = await importer.import_story_from_directory(pokemon_amber_dir)
    
    print(f"\n🎉 Import completed in temp directory!")
    print(f"📁 Temp Workspace: {result['workspace_path']}")
    print(f"📚 Story: {result['story_title']}")
    print(f"📄 Chapters: {result['chapters_imported']}")
    print(f"🔧 Workspace ID: {result['workspace_id']}")
    
    # Offer to move to final location
    print(f"\n📦 Moving to final location...")
    if move_workspace_from_temp(temp_workspace_path, final_workspace_path):
        print(f"✅ Workspace ready at: {final_workspace_path}")
    else:
        print(f"⚠️  Workspace remains in temp: {temp_workspace_path}")


async def import_custom_story(story_dir: str, workspace_dir: str):
    """Import a custom story from directory"""
    
    story_path = Path(story_dir)
    final_workspace_path = Path(workspace_dir)
    
    # Create temp workspace path based on final name
    base_name = final_workspace_path.name
    temp_workspace_path = _create_temp_workspace_path(base_name)
    
    if not story_path.exists():
        print(f"❌ Story directory not found: {story_path}")
        return
    
    print(f"📁 Creating temporary workspace: {temp_workspace_path}")
    
    # Create temp workspace directory
    temp_workspace_path.mkdir(parents=True, exist_ok=True)
    
    # Import the story to temp location
    importer = StoryImporter(temp_workspace_path)
    result = await importer.import_story_from_directory(story_path)
    
    print(f"\n🎉 Import completed in temp directory!")
    print(f"📁 Temp Workspace: {result['workspace_path']}")
    print(f"📚 Story: {result['story_title']}")
    print(f"📄 Chapters: {result['chapters_imported']}")
    print(f"🔧 Workspace ID: {result['workspace_id']}")
    
    # Offer to move to final location
    print(f"\n📦 Moving to final location...")
    if move_workspace_from_temp(temp_workspace_path, final_workspace_path):
        print(f"✅ Workspace ready at: {final_workspace_path}")
    else:
        print(f"⚠️  Workspace remains in temp: {temp_workspace_path}")


def cleanup_temp_workspaces():
    """Clean up old temporary workspaces"""
    backend_root = Path(__file__).parent.parent.parent.parent
    temp_dir = backend_root / "temp"
    
    if not temp_dir.exists():
        print("📁 No temp directory found.")
        return
    
    temp_workspaces = [d for d in temp_dir.iterdir() if d.is_dir()]
    
    if not temp_workspaces:
        print("📁 No temp workspaces found.")
        return
    
    print(f"🗑️  Found {len(temp_workspaces)} temp workspaces:")
    for workspace in temp_workspaces:
        print(f"   - {workspace.name}")
    
    response = input("\nDelete all temp workspaces? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        import shutil
        for workspace in temp_workspaces:
            try:
                shutil.rmtree(workspace)
                print(f"✅ Deleted: {workspace.name}")
            except Exception as e:
                print(f"❌ Error deleting {workspace.name}: {e}")
        print("🗑️  Cleanup completed!")
    else:
        print("🚫 Cleanup cancelled.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Import stories into ShuScribe database")
    parser.add_argument("--pokemon-amber", action="store_true", help="Import Pokemon Amber story")
    parser.add_argument("--story-dir", type=str, help="Directory containing story XML files")
    parser.add_argument("--workspace-dir", type=str, help="Target workspace directory")
    parser.add_argument("--cleanup-temp", action="store_true", help="Clean up temporary workspaces")
    parser.add_argument("--list-temp", action="store_true", help="List temporary workspaces")
    
    args = parser.parse_args()
    
    if args.cleanup_temp:
        cleanup_temp_workspaces()
    elif args.list_temp:
        backend_root = Path(__file__).parent.parent.parent.parent
        temp_dir = backend_root / "temp"
        if temp_dir.exists():
            temp_workspaces = [d for d in temp_dir.iterdir() if d.is_dir()]
            if temp_workspaces:
                print(f"📁 Found {len(temp_workspaces)} temp workspaces:")
                for workspace in temp_workspaces:
                    print(f"   - {workspace}")
            else:
                print("📁 No temp workspaces found.")
        else:
            print("📁 No temp directory found.")
    elif args.pokemon_amber:
        asyncio.run(import_pokemon_amber())
    elif args.story_dir and args.workspace_dir:
        asyncio.run(import_custom_story(args.story_dir, args.workspace_dir))
    else:
        print("Usage:")
        print("  python import_story.py --pokemon-amber")
        print("  python import_story.py --story-dir /path/to/story --workspace-dir /path/to/workspace")
        print("  python import_story.py --list-temp")
        print("  python import_story.py --cleanup-temp") 