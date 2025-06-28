"""
Integration tests for Story and Wiki repositories using Pokemon Amber test data
"""
import pytest
from pathlib import Path
from uuid import UUID

from src.database.repositories.story.story_in_memory import InMemoryStoryRepository
from src.database.repositories.wikipage.wikipage_in_memory import InMemoryWikiPageRepository
from src.core.story_workspace import StoryWorkspace
from src.schemas.story import StoryCreate, ChapterCreate
from src.schemas.wiki import (
    WikiPageCreate, ArticleCreate, ArticleSnapshotCreate,
    ArticleStoryAssociationCreate, WikiPageArticleLinkCreate,
    ArticleType
)


class TestStoryWorkspaceIntegration:
    """Test loading real story data using StoryWorkspace"""

    @pytest.mark.asyncio
    async def test_load_pokemon_amber_story(self, pokemon_story_path: Path, test_user_id: UUID):
        """Test loading the Pokemon Amber story from test resources"""
        # Initialize workspace
        workspace = StoryWorkspace(pokemon_story_path, test_user_id)
        
        # Verify metadata was loaded correctly
        metadata = workspace.story_metadata
        assert metadata.title == "Pokemon: Ambertwo"
        assert metadata.author == "ChronicImmortality"
        assert "Pokemon fan gets isekai'd" in metadata.synopsis
        assert "Drama" in metadata.genres
        assert "Reincarnation" in metadata.tags
        
        # Verify chapters were loaded
        assert len(workspace.chapters) == 17
        
        # Test lazy loading - get first chapter through get_chunk method
        first_chapter_list = workspace.chapters.get_chunk(1, 1)
        chapter_1 = first_chapter_list[0]
        assert chapter_1.chapter_number == 1
        assert chapter_1.title == "[Chapter 1] Truck-kun Strikes Again"
        
        # Test chapter content access
        content = workspace.get_chapter_content_chunked(start=1, count=1)
        assert len(content) > 0
        assert isinstance(content, str)

    @pytest.mark.asyncio
    async def test_workspace_chapter_range(self, pokemon_story_path: Path, test_user_id: UUID):
        """Test chapter range operations"""
        workspace = StoryWorkspace(pokemon_story_path, test_user_id)
        
        # Test getting a range of chapters
        chapters_1_to_3 = workspace.chapters.get_range(1, 3)
        assert len(chapters_1_to_3) == 3
        assert chapters_1_to_3[0].chapter_number == 1
        assert chapters_1_to_3[2].chapter_number == 3
        
        # Test chunked content loading
        chunked_content = workspace.get_chapter_content_chunked(start=1, count=3)
        assert len(chunked_content) > 0
        assert "Chapter 1" in chunked_content
        assert "Chapter 3" in chunked_content


class TestRepositoryIntegration:
    """Test story and wiki repositories working together"""

    @pytest.mark.asyncio
    async def test_create_story_with_wiki(self, story_repo: InMemoryStoryRepository, 
                                         wiki_repo: InMemoryWikiPageRepository, 
                                         test_user_id: UUID, pokemon_story_path: Path):
        """Test creating a story and associated wiki content"""
        # Load story data
        workspace = StoryWorkspace(pokemon_story_path, test_user_id)
        
        # Create story in repository
        story_create = StoryCreate(
            title=workspace.story_metadata.title,
            author=workspace.story_metadata.author,
            owner_id=test_user_id
        )
        story = await story_repo.create_story(story_create)
        
        # Add first few chapters
        chapters_1_to_3 = workspace.chapters.get_range(1, 3)
        for chapter_data in chapters_1_to_3:
            chapter_create = ChapterCreate(
                story_id=story.id,
                chapter_number=chapter_data.chapter_number,
                title=chapter_data.title,
                raw_content=chapter_data.content
            )
            await story_repo.create_chapter(chapter_create)
        
        # Create associated wiki page
        wiki_create = WikiPageCreate(
            title=f"{story.title} Wiki",
            description=f"Wiki for {story.title}",
            is_public=True,
            safe_through_chapter=3,  # Safe through chapter 3
            creator_id=test_user_id
        )
        wiki_page = await wiki_repo.create_wiki_page(wiki_create)
        
        # Verify integration
        chapters = await story_repo.get_chapters(story.id)
        assert len(chapters) == 3
        assert wiki_page.safe_through_chapter == 3

    @pytest.mark.asyncio
    async def test_article_snapshot_workflow(self, story_repo: InMemoryStoryRepository,
                                           wiki_repo: InMemoryWikiPageRepository,
                                           test_user_id: UUID):
        """Test the complete article snapshot workflow"""
        # Create a story
        story = await story_repo.create_story(StoryCreate(
            title="Pokemon Adventures", author="Test Author", owner_id=test_user_id
        ))
        
        # Add some chapters
        await story_repo.create_chapter(ChapterCreate(
            story_id=story.id, chapter_number=1, title="Meeting Pikachu",
            raw_content="Ash meets Pikachu for the first time..."
        ))
        await story_repo.create_chapter(ChapterCreate(
            story_id=story.id, chapter_number=2, title="First Battle",
            raw_content="Pikachu's first battle against Team Rocket..."
        ))
        await story_repo.create_chapter(ChapterCreate(
            story_id=story.id, chapter_number=3, title="New Powers",
            raw_content="Pikachu learns Thunderbolt attack..."
        ))
        
        # Create wiki page
        wiki_page = await wiki_repo.create_wiki_page(WikiPageCreate(
            title="Pokemon Adventures Wiki", description="Character guide",
            is_public=True, safe_through_chapter=3, creator_id=test_user_id
        ))
        
        # Create base article for Pikachu
        pikachu_article = await wiki_repo.create_article(ArticleCreate(
            title="Pikachu", slug="pikachu", article_type=ArticleType.CHARACTER,
            canonical_name="Pikachu", aliases=["Electric Mouse", "Pika"],
            tags=["electric", "pokemon", "main"], creator_id=test_user_id
        ))
        
        # Create article snapshots showing character development
        
        # Snapshot 1: After chapter 1 (basic info)
        snapshot_v1 = await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=pikachu_article.id,
            content="Pikachu is an Electric-type Pokemon. Initially distrustful of humans.",
            preview="Electric-type Pokemon, initially distrustful",
            last_safe_chapter=1,
            source_story_id=story.id,
            version_number=1,
            parent_snapshot_id=None
        ))
        
        # Snapshot 2: After chapter 2 (shows loyalty development)
        snapshot_v2 = await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=pikachu_article.id,
            content="Pikachu is an Electric-type Pokemon. After the Team Rocket incident, shows growing trust in Ash.",
            preview="Electric-type Pokemon, growing trust in Ash",
            last_safe_chapter=2,
            source_story_id=story.id,
            version_number=2,
            parent_snapshot_id=snapshot_v1.id
        ))
        
        # Snapshot 3: After chapter 3 (shows power growth)
        snapshot_v3 = await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=pikachu_article.id,
            content="Pikachu is an Electric-type Pokemon. Loyal partner to Ash. Has mastered the Thunderbolt attack.",
            preview="Electric-type Pokemon, loyal partner, knows Thunderbolt",
            last_safe_chapter=3,
            source_story_id=story.id,
            version_number=3,
            parent_snapshot_id=snapshot_v2.id
        ))
        
        # Create story-article association
        association = await wiki_repo.create_article_story_association(ArticleStoryAssociationCreate(
            article_id=pikachu_article.id,
            story_id=story.id,
            first_mentioned_chapter=1,
            importance_level=10,  # Main character
            relationship_type="protagonist"
        ))
        
        # Link the latest snapshot to the wiki page
        wiki_link = await wiki_repo.create_page_snapshot_link(WikiPageArticleLinkCreate(
            wiki_page_id=wiki_page.id,
            article_snapshot_id=snapshot_v3.id,  # Latest version
            display_order=1,
            is_featured=True
        ))
        
        # Verify the complete workflow
        
        # 1. Story has chapters
        chapters = await story_repo.get_chapters(story.id)
        assert len(chapters) == 3
        
        # 2. Article has multiple snapshots
        snapshots = await wiki_repo.get_article_snapshots(article_id=pikachu_article.id)
        assert len(snapshots) == 3
        
        # 3. Snapshots form a version chain
        v3_snapshot = next(s for s in snapshots if s.version_number == 3)
        v2_snapshot = next(s for s in snapshots if s.version_number == 2)
        v1_snapshot = next(s for s in snapshots if s.version_number == 1)
        
        assert v3_snapshot.parent_snapshot_id == v2_snapshot.id
        assert v2_snapshot.parent_snapshot_id == v1_snapshot.id
        assert v1_snapshot.parent_snapshot_id is None
        
        # 4. Progressive safety levels
        assert v1_snapshot.last_safe_chapter == 1
        assert v2_snapshot.last_safe_chapter == 2
        assert v3_snapshot.last_safe_chapter == 3
        
        # 5. Content evolution
        assert "Initially distrustful" in v1_snapshot.content
        assert "growing trust" in v2_snapshot.content
        assert "Loyal partner" in v3_snapshot.content
        assert "Thunderbolt" in v3_snapshot.content
        
        # 6. Wiki page links to current version
        wiki_snapshots = await wiki_repo.get_wiki_page_snapshots(wiki_page.id)
        assert len(wiki_snapshots) == 1
        assert wiki_snapshots[0].id == snapshot_v3.id
        
        # 7. Story-article association exists
        story_associations = await wiki_repo.get_article_story_associations(story_id=story.id)
        assert len(story_associations) == 1
        assert story_associations[0].article_id == pikachu_article.id
        assert story_associations[0].importance_level == 10

    @pytest.mark.asyncio
    async def test_spoiler_safety_filtering(self, story_repo: InMemoryStoryRepository,
                                          wiki_repo: InMemoryWikiPageRepository,
                                          test_user_id: UUID):
        """Test that article snapshots respect spoiler safety levels"""
        # Create story with chapters
        story = await story_repo.create_story(StoryCreate(
            title="Mystery Story", author="Test Author", owner_id=test_user_id
        ))
        
        for i in range(1, 6):  # 5 chapters
            await story_repo.create_chapter(ChapterCreate(
                story_id=story.id, chapter_number=i, title=f"Chapter {i}",
                raw_content=f"Content of chapter {i}"
            ))
        
        # Create character article
        character = await wiki_repo.create_article(ArticleCreate(
            title="Mystery Character", slug="mystery", article_type=ArticleType.CHARACTER,
            canonical_name="Mystery Character", creator_id=test_user_id
        ))
        
        # Create snapshots with different safety levels
        snapshot1 = await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=character.id, content="Basic introduction", preview="Basic intro",
            last_safe_chapter=2, source_story_id=story.id, version_number=1,
            parent_snapshot_id=None
        ))
        
        snapshot2 = await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=character.id, content="SPOILER: Character is the villain!", preview="Major reveal",
            last_safe_chapter=4, source_story_id=story.id, version_number=2,
            parent_snapshot_id=snapshot1.id
        ))
        
        snapshot3 = await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=character.id, content="HUGE SPOILER: Character dies!", preview="Final fate",
            last_safe_chapter=5, source_story_id=story.id, version_number=3,
            parent_snapshot_id=snapshot2.id
        ))
        
        # Create wiki pages with different safety levels
        safe_wiki = await wiki_repo.create_wiki_page(WikiPageCreate(
            title="Safe Wiki", description="No spoilers", is_public=True,
            safe_through_chapter=2, creator_id=test_user_id
        ))
        
        spoiler_wiki = await wiki_repo.create_wiki_page(WikiPageCreate(
            title="Spoiler Wiki", description="Contains spoilers", is_public=True,
            safe_through_chapter=5, creator_id=test_user_id
        ))
        
        # Link appropriate snapshots to each wiki
        safe_snapshot = (await wiki_repo.get_article_snapshots(
            article_id=character.id, story_id=story.id
        ))[0]  # Version 1, safe through chapter 2
        
        spoiler_snapshot = (await wiki_repo.get_article_snapshots(
            article_id=character.id, story_id=story.id
        ))[-1]  # Version 3, safe through chapter 5
        
        await wiki_repo.create_page_snapshot_link(WikiPageArticleLinkCreate(
            wiki_page_id=safe_wiki.id, article_snapshot_id=safe_snapshot.id,
            display_order=1, is_featured=True
        ))
        
        await wiki_repo.create_page_snapshot_link(WikiPageArticleLinkCreate(
            wiki_page_id=spoiler_wiki.id, article_snapshot_id=spoiler_snapshot.id,
            display_order=1, is_featured=True
        ))
        
        # Verify spoiler safety
        safe_snapshots = await wiki_repo.get_wiki_page_snapshots(safe_wiki.id)
        spoiler_snapshots = await wiki_repo.get_wiki_page_snapshots(spoiler_wiki.id)
        
        assert len(safe_snapshots) == 1
        assert len(spoiler_snapshots) == 1
        
        # Safe wiki should only have basic content
        safe_snapshot_content = safe_snapshots[0].content
        assert "Basic introduction" in safe_snapshot_content
        assert "SPOILER" not in safe_snapshot_content
        
        # Spoiler wiki should have the full content
        spoiler_snapshot_content = spoiler_snapshots[0].content
        assert "HUGE SPOILER" in spoiler_snapshot_content 