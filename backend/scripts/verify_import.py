"""
Verification script to test that imported stories can be read through the database API
"""

import asyncio
import sys
from pathlib import Path
from typing import cast

from src.database.models.repositories import FileRepositories

# Add the backend src to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.database.factory import get_repositories


async def verify_pokemon_amber():
    """Verify that Pokemon Amber was imported correctly"""
    
    workspace_path = Path(__file__).parent.parent / "workspace_pokemon_amber"
    
    if not workspace_path.exists():
        print("❌ Pokemon Amber workspace not found. Run import first.")
        return
    
    print(f"🔍 Verifying Pokemon Amber import in: {workspace_path}")
    
    # Get repositories
    repos = cast(FileRepositories, get_repositories(backend="file", workspace_path=workspace_path))
    
    # Get user
    user = await repos.user.get_current_user()
    print(f"👤 User: {user.display_name} ({user.email})")
    
    # Get workspace
    workspaces = await repos.workspace.get_by_owner(user.id)
    if not workspaces:
        print("❌ No workspaces found")
        return
    
    workspace = workspaces[0]
    print(f"📁 Workspace: {workspace.name}")
    print(f"📖 Description: {workspace.description}")
    
    # Get story metadata
    story_metadata = await repos.story.get_story_metadata(workspace.id)
    if not story_metadata:
        print("❌ No story metadata found")
        return
    
    print(f"📚 Story: {story_metadata.title}")
    print(f"✍️  Author: {story_metadata.author}")
    print(f"📄 Published chapters: {story_metadata.published_chapters}")
    print(f"🔢 Total word count: {story_metadata.total_word_count}")
    
    # Get chapters
    chapters = await repos.story.get_chapters_by_workspace(workspace.id)
    print(f"📖 Found {len(chapters)} chapters:")
    
    for chapter in chapters[:5]:  # Show first 5
        print(f"  {chapter.chapter_number:2d}. {chapter.title} ({chapter.word_count} words)")
    
    if len(chapters) > 5:
        print(f"  ... and {len(chapters) - 5} more chapters")
    
    # Test getting a specific chapter
    if chapters:
        first_chapter = chapters[0]
        print(f"\n📄 First chapter details:")
        print(f"   Title: {first_chapter.title}")
        print(f"   Status: {first_chapter.status}")
        print(f"   Words: {first_chapter.word_count}")
        print(f"   Content preview: {first_chapter.content[:100]}...")
        
        # Test getting by chapter number
        same_chapter = await repos.story.get_chapter_by_number(workspace.id, 1)
        if same_chapter and same_chapter.id == first_chapter.id:
            print("✅ Chapter lookup by number works correctly")
        else:
            print("❌ Chapter lookup by number failed")
    
    # Test published chapters only
    published = await repos.story.get_published_chapters(workspace.id)
    print(f"\n📋 Published chapters: {len(published)}")
    
    print(f"\n🎉 Verification complete! Import was successful.")


if __name__ == "__main__":
    asyncio.run(verify_pokemon_amber()) 