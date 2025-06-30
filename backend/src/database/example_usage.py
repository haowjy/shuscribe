"""
Example Usage of ShuScribe Database Architecture

Simple example showing how to use the repository system for MVP functionality.
"""

import asyncio
from uuid import uuid4
from datetime import datetime

from src.database import (
    get_repositories,
    UserCreate, WorkspaceCreate, ChapterCreate, WikiArticleCreate,
    SubscriptionTier, ChapterStatus, WikiArticleType
)


async def example_usage():
    """Example showing basic repository usage"""
    print("🚀 ShuScribe Database Example")
    print("=" * 40)
    
    # Get in-memory repositories for testing
    repos = get_repositories(backend="memory")
    user_repo = repos.user
    workspace_repo = repos.workspace
    story_repo = repos.story
    wiki_repo = repos.wiki
    
    # 1. Create a user
    print("\n📝 Creating user...")
    user_data = UserCreate(
        email="author@example.com",
        display_name="Jane Author",
        subscription_tier=SubscriptionTier.LOCAL
    )
    user = await user_repo.create(user_data)
    print(f"✅ Created user: {user.display_name} ({user.email})")
    
    # 2. Store API key for BYOK
    print("\n🔑 Storing API key...")
    from .models.user import UserAPIKeyCreate
    api_key_data = UserAPIKeyCreate(
        provider="openai",
        api_key="sk-test-123456",
        provider_metadata={"model": "gpt-4"}
    )
    api_key = await user_repo.store_api_key(user.id, api_key_data)
    print(f"✅ Stored API key for {api_key.provider}")
    
    # 3. Create a workspace
    print("\n📁 Creating workspace...")
    workspace_data = WorkspaceCreate(
        name="My Fantasy Novel",
        description="An epic fantasy adventure",
        owner_id=user.id
    )
    workspace = await workspace_repo.create(workspace_data)
    print(f"✅ Created workspace: {workspace.name}")
    
    # 4. Create story metadata
    print("\n📚 Creating story metadata...")
    story_metadata = await story_repo.create_story_metadata(
        workspace.id,
        title="The Dragon's Quest",
        author="Jane Author"
    )
    print(f"✅ Created story: {story_metadata.title}")
    
    # 5. Add some chapters
    print("\n📄 Adding chapters...")
    chapters = []
    for i in range(1, 4):
        chapter_data = ChapterCreate(
            workspace_id=workspace.id,
            title=f"Chapter {i}: The Adventure Begins",
            content=f"This is the content of chapter {i}. It's an exciting part of the story!",
            chapter_number=i,
            status=ChapterStatus.PUBLISHED
        )
        chapter = await story_repo.create_chapter(chapter_data)
        chapters.append(chapter)
        print(f"  ✅ Added: {chapter.title} ({chapter.word_count} words)")
    
    # 6. Create wiki articles
    print("\n📖 Creating wiki articles...")
    
    # Character article
    character_data = WikiArticleCreate(
        title="Aria the Dragon Rider",
        article_type=WikiArticleType.CHARACTER,
        content="A brave young warrior who can communicate with dragons.",
        safe_through_chapter=3
    )
    character_article = await wiki_repo.create_article(workspace.id, character_data)
    print(f"  ✅ Created character: {character_article.title}")
    
    # Location article  
    location_data = WikiArticleCreate(
        title="The Crystal Caves",
        article_type=WikiArticleType.LOCATION,
        content="Ancient caves filled with magical crystals.",
        safe_through_chapter=3
    )
    location_article = await wiki_repo.create_article(workspace.id, location_data)
    print(f"  ✅ Created location: {location_article.title}")
    
    # 7. Create chapter-specific versions for spoiler prevention
    print("\n🔒 Creating spoiler-safe versions...")
    
    # Version safe through chapter 1 (no spoilers)
    await wiki_repo.create_chapter_version(
        character_article.id,
        content="A mysterious young person seen in the village.",
        safe_through_chapter=1
    )
    
    # Version safe through chapter 3 (more details revealed)
    await wiki_repo.create_chapter_version(
        character_article.id,
        content="Aria the Dragon Rider - a brave warrior with the rare ability to communicate with dragons. She seeks the ancient Crystal of Power.",
        safe_through_chapter=3
    )
    print("  ✅ Created spoiler-safe versions")
    
    # 8. Test spoiler prevention
    print("\n🛡️  Testing spoiler prevention...")
    
    # Get version safe for someone who's only read chapter 1
    version_ch1 = await wiki_repo.get_version_for_chapter(character_article.id, 1)
    if version_ch1:
        print(f"  Chapter 1 reader sees: '{version_ch1.content}'")
    
    # Get version safe for someone who's read chapter 3
    version_ch3 = await wiki_repo.get_version_for_chapter(character_article.id, 3)
    if version_ch3:
        print(f"  Chapter 3 reader sees: '{version_ch3.content}'")
    
    # 9. Create article connections
    print("\n🔗 Creating article connections...")
    connection = await wiki_repo.create_connection(
        character_article.id,
        location_article.id,
        connection_type="explores",
        strength=0.8,
        context="Aria explores the Crystal Caves in chapter 3"
    )
    print(f"  ✅ Connected {character_article.title} -> {location_article.title}")
    
    # 10. Summary
    print("\n📊 Summary:")
    print(f"  👤 Users: 1")
    print(f"  📁 Workspaces: 1") 
    print(f"  📄 Chapters: {len(chapters)}")
    print(f"  📖 Wiki Articles: 2")
    print(f"  🔗 Article Connections: 1")
    
    print("\n🎉 Example completed successfully!")
    print("=" * 40)


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_usage()) 