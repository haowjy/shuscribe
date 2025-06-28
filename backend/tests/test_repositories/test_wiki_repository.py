"""
Tests for InMemoryWikiPageRepository - Article Snapshot Architecture
"""
import pytest
from uuid import UUID, uuid4
from src.database.repositories.wikipage.wikipage_in_memory import InMemoryWikiPageRepository
from src.schemas.wiki import (
    WikiPageCreate, WikiPageUpdate,
    ArticleCreate, ArticleUpdate,
    ArticleSnapshotCreate, ArticleSnapshotUpdate,
    ArticleStoryAssociationCreate,
    WikiPageArticleLinkCreate,
    ArticleType
)


class TestWikiPageRepository:
    """Test suite for wiki page operations"""

    @pytest.mark.asyncio
    async def test_create_wiki_page(self, wiki_repo: InMemoryWikiPageRepository, test_user_id: UUID):
        """Test creating a new wiki page"""
        wiki_create = WikiPageCreate(
            title="Pokemon World Wiki",
            description="A wiki about the Pokemon world",
            is_public=True,
            safe_through_chapter=5,
            creator_id=test_user_id
        )
        
        wiki = await wiki_repo.create_wiki_page(wiki_create)
        
        assert wiki.title == "Pokemon World Wiki"
        assert wiki.description == "A wiki about the Pokemon world"
        assert wiki.is_public is True
        assert wiki.safe_through_chapter == 5
        assert wiki.creator_id == test_user_id
        assert wiki.id is not None

    @pytest.mark.asyncio
    async def test_get_wiki_page_existing(self, wiki_repo: InMemoryWikiPageRepository, sample_wiki_page):
        """Test retrieving an existing wiki page"""
        wiki = sample_wiki_page
        retrieved_wiki = await wiki_repo.get_wiki_page(wiki.id)
        
        assert retrieved_wiki.id == wiki.id
        assert retrieved_wiki.title == wiki.title
        assert retrieved_wiki.description == wiki.description

    @pytest.mark.asyncio
    async def test_get_wiki_page_nonexistent(self, wiki_repo: InMemoryWikiPageRepository):
        """Test retrieving a non-existent wiki page returns empty wiki"""
        fake_id = uuid4()
        empty_wiki = await wiki_repo.get_wiki_page(fake_id)
        
        assert empty_wiki.id == UUID(int=0)
        assert empty_wiki.title == ""

    @pytest.mark.asyncio
    async def test_update_wiki_page(self, wiki_repo: InMemoryWikiPageRepository, sample_wiki_page):
        """Test updating an existing wiki page"""
        wiki = sample_wiki_page
        update_data = WikiPageUpdate(safe_through_chapter=10)
        
        updated_wiki = await wiki_repo.update_wiki_page(wiki.id, update_data)
        
        assert updated_wiki.safe_through_chapter == 10
        assert updated_wiki.title == wiki.title  # Unchanged

    @pytest.mark.asyncio
    async def test_delete_wiki_page(self, wiki_repo: InMemoryWikiPageRepository, sample_wiki_page):
        """Test deleting a wiki page"""
        wiki = sample_wiki_page
        result = await wiki_repo.delete_wiki_page(wiki.id)
        assert result is True
        
        # Verify wiki is gone
        empty_wiki = await wiki_repo.get_wiki_page(wiki.id)
        assert empty_wiki.id == UUID(int=0)


class TestArticleOperations:
    """Test suite for base article operations"""

    @pytest.mark.asyncio
    async def test_create_article(self, wiki_repo: InMemoryWikiPageRepository, test_user_id: UUID):
        """Test creating a new base article"""
        article_create = ArticleCreate(
            title="Pikachu",
            slug="pikachu",
            article_type=ArticleType.CHARACTER,
            canonical_name="Pikachu",
            aliases=["Electric Mouse", "Pika"],
            tags=["electric", "pokemon", "main"],
            creator_id=test_user_id
        )
        
        article = await wiki_repo.create_article(article_create)
        
        assert article.title == "Pikachu"
        assert article.slug == "pikachu"
        assert article.article_type == ArticleType.CHARACTER
        assert article.canonical_name == "Pikachu"
        assert "Electric Mouse" in article.aliases
        assert "electric" in article.tags
        assert article.creator_id == test_user_id

    @pytest.mark.asyncio
    async def test_get_article_existing(self, wiki_repo: InMemoryWikiPageRepository, sample_article):
        """Test retrieving an existing article"""
        article = sample_article
        retrieved_article = await wiki_repo.get_article(article.id)
        
        assert retrieved_article.id == article.id
        assert retrieved_article.title == article.title
        assert retrieved_article.article_type == article.article_type

    @pytest.mark.asyncio
    async def test_update_article(self, wiki_repo: InMemoryWikiPageRepository, sample_article):
        """Test updating an existing article"""
        article = sample_article
        update_data = ArticleUpdate(tags=["updated", "character"])
        
        updated_article = await wiki_repo.update_article(article.id, update_data)
        
        assert "updated" in updated_article.tags
        assert updated_article.title == article.title  # Unchanged

    @pytest.mark.asyncio
    async def test_search_articles_by_type(self, wiki_repo: InMemoryWikiPageRepository, sample_wiki_page, test_user_id: UUID):
        """Test searching articles by type"""
        wiki = sample_wiki_page
        story_id = uuid4()
        
        # Create articles of different types
        char1 = await wiki_repo.create_article(ArticleCreate(
            title="Ash Ketchum", slug="ash-ketchum", article_type=ArticleType.CHARACTER,
            canonical_name="Ash Ketchum", creator_id=test_user_id
        ))
        location = await wiki_repo.create_article(ArticleCreate(
            title="Pallet Town", slug="pallet-town", article_type=ArticleType.LOCATION,
            canonical_name="Pallet Town", creator_id=test_user_id
        ))
        char2 = await wiki_repo.create_article(ArticleCreate(
            title="Team Rocket", slug="team-rocket", article_type=ArticleType.CHARACTER,
            canonical_name="Team Rocket", creator_id=test_user_id
        ))
        
        # Create snapshots and link them to the wiki page
        for article in [char1, location, char2]:
            snapshot = await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
                article_id=article.id, content=f"Content for {article.title}", 
                preview=f"Preview for {article.title}", last_safe_chapter=5, 
                source_story_id=story_id, version_number=1, parent_snapshot_id=None
            ))
            await wiki_repo.create_page_snapshot_link(WikiPageArticleLinkCreate(
                wiki_page_id=wiki.id, article_snapshot_id=snapshot.id,
                display_order=1, is_featured=False
            ))
        
        # Search for characters only
        character_articles = await wiki_repo.search_articles(
            wiki_page_id=wiki.id, 
            query="",
            article_types=[ArticleType.CHARACTER]
        )
        
        assert len(character_articles) == 2
        assert {a.title for a in character_articles} == {"Ash Ketchum", "Team Rocket"}


class TestArticleSnapshotOperations:
    """Test suite for article snapshot operations"""

    @pytest.mark.asyncio
    async def test_create_article_snapshot(self, wiki_repo: InMemoryWikiPageRepository, sample_article, test_user_id: UUID):
        """Test creating an article snapshot"""
        article = sample_article
        story_id = uuid4()
        
        snapshot_create = ArticleSnapshotCreate(
            article_id=article.id,
            content="Pikachu is an Electric-type Pokemon...",
            preview="Pikachu is an Electric-type...",
            last_safe_chapter=3,
            source_story_id=story_id,
            version_number=1,
            parent_snapshot_id=None
        )
        
        snapshot = await wiki_repo.create_article_snapshot(snapshot_create)
        
        assert snapshot.article_id == article.id
        assert snapshot.content == "Pikachu is an Electric-type Pokemon..."
        assert snapshot.last_safe_chapter == 3
        assert snapshot.source_story_id == story_id
        assert snapshot.version_number == 1

    @pytest.mark.asyncio
    async def test_get_article_snapshots_by_article(self, wiki_repo: InMemoryWikiPageRepository, sample_article, test_user_id: UUID):
        """Test retrieving snapshots for an article"""
        article = sample_article
        story1_id = uuid4()
        story2_id = uuid4()
        
        # Create snapshots for different stories
        await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=article.id, content="Content 1", preview="Preview 1",
            last_safe_chapter=5, source_story_id=story1_id, version_number=1,
            parent_snapshot_id=None
        ))
        await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=article.id, content="Content 2", preview="Preview 2",
            last_safe_chapter=3, source_story_id=story2_id, version_number=1,
            parent_snapshot_id=None
        ))
        
        # Get all snapshots for this article
        snapshots = await wiki_repo.get_article_snapshots(article_id=article.id)
        
        assert len(snapshots) == 2
        assert {s.source_story_id for s in snapshots} == {story1_id, story2_id}

    @pytest.mark.asyncio
    async def test_get_article_snapshots_by_story(self, wiki_repo: InMemoryWikiPageRepository, sample_article, test_user_id: UUID):
        """Test retrieving snapshots for a story"""
        article = sample_article
        story_id = uuid4()
        
        # Create snapshot for this story
        snapshot = await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=article.id, content="Story content", preview="Story preview",
            last_safe_chapter=7, source_story_id=story_id, version_number=1,
            parent_snapshot_id=None
        ))
        
        # Create snapshot for different story
        await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=article.id, content="Other content", preview="Other preview",
            last_safe_chapter=2, source_story_id=uuid4(), version_number=1,
            parent_snapshot_id=None
        ))
        
        # Get snapshots for specific story
        story_snapshots = await wiki_repo.get_article_snapshots(article_id=article.id, story_id=story_id)
        
        assert len(story_snapshots) == 1
        assert story_snapshots[0].id == snapshot.id

    @pytest.mark.asyncio
    async def test_update_article_snapshot(self, wiki_repo: InMemoryWikiPageRepository, sample_article, test_user_id: UUID):
        """Test updating an article snapshot"""
        article = sample_article
        story_id = uuid4()
        
        snapshot = await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=article.id, content="Original content", preview="Original preview",
            last_safe_chapter=5, source_story_id=story_id, version_number=1,
            parent_snapshot_id=None
        ))
        
        update_data = ArticleSnapshotUpdate(last_safe_chapter=10)
        updated_snapshot = await wiki_repo.update_article_snapshot(snapshot.id, update_data)
        
        assert updated_snapshot.last_safe_chapter == 10
        assert updated_snapshot.content == "Original content"  # Unchanged

    @pytest.mark.asyncio
    async def test_article_snapshot_versioning(self, wiki_repo: InMemoryWikiPageRepository, sample_article, test_user_id: UUID):
        """Test creating multiple versions of a snapshot"""
        article = sample_article
        story_id = uuid4()
        
        # Create initial snapshot
        v1 = await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=article.id, content="Version 1 content", preview="Version 1",
            last_safe_chapter=5, source_story_id=story_id, version_number=1,
            parent_snapshot_id=None
        ))
        
        # Create updated version referencing the first
        v2 = await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=article.id, content="Version 2 content", preview="Version 2",
            last_safe_chapter=8, source_story_id=story_id, version_number=2,
            parent_snapshot_id=v1.id
        ))
        
        # Verify version chain
        assert v2.parent_snapshot_id == v1.id
        assert v1.version_number == 1
        assert v2.version_number == 2


class TestArticleStoryAssociations:
    """Test suite for article-story association operations"""

    @pytest.mark.asyncio
    async def test_create_article_story_association(self, wiki_repo: InMemoryWikiPageRepository, sample_article):
        """Test creating an article-story association"""
        article = sample_article
        story_id = uuid4()
        
        association_create = ArticleStoryAssociationCreate(
            article_id=article.id,
            story_id=story_id,
            first_mentioned_chapter=3,
            importance_level=8,
            relationship_type="main_character"
        )
        
        association = await wiki_repo.create_article_story_association(association_create)
        
        assert association.article_id == article.id
        assert association.story_id == story_id
        assert association.first_mentioned_chapter == 3
        assert association.importance_level == 8
        assert association.relationship_type == "main_character"

    @pytest.mark.asyncio
    async def test_get_article_stories(self, wiki_repo: InMemoryWikiPageRepository, sample_article):
        """Test getting stories that reference an article"""
        article = sample_article
        story1_id = uuid4()
        story2_id = uuid4()
        
        # Create associations
        await wiki_repo.create_article_story_association(ArticleStoryAssociationCreate(
            article_id=article.id, story_id=story1_id, first_mentioned_chapter=1,
            importance_level=9, relationship_type="protagonist"
        ))
        await wiki_repo.create_article_story_association(ArticleStoryAssociationCreate(
            article_id=article.id, story_id=story2_id, first_mentioned_chapter=5,
            importance_level=3, relationship_type="minor_character"
        ))
        
        # Get associated stories
        associations = await wiki_repo.get_article_story_associations(article_id=article.id)
        
        assert len(associations) == 2
        assert {a.story_id for a in associations} == {story1_id, story2_id}

    @pytest.mark.asyncio
    async def test_get_story_articles(self, wiki_repo: InMemoryWikiPageRepository, sample_article, test_user_id: UUID):
        """Test getting articles referenced by a story"""
        article1 = sample_article
        article2 = await wiki_repo.create_article(ArticleCreate(
            title="Misty", slug="misty", article_type=ArticleType.CHARACTER,
            canonical_name="Misty", creator_id=test_user_id
        ))
        story_id = uuid4()
        
        # Create associations
        await wiki_repo.create_article_story_association(ArticleStoryAssociationCreate(
            article_id=article1.id, story_id=story_id, first_mentioned_chapter=1,
            importance_level=10, relationship_type="protagonist"
        ))
        await wiki_repo.create_article_story_association(ArticleStoryAssociationCreate(
            article_id=article2.id, story_id=story_id, first_mentioned_chapter=2,
            importance_level=7, relationship_type="supporting"
        ))
        
        # Get articles for this story
        associations = await wiki_repo.get_article_story_associations(story_id=story_id)
        
        assert len(associations) == 2
        assert {a.article_id for a in associations} == {article1.id, article2.id}


class TestWikiPageArticleLinks:
    """Test suite for wiki page to article snapshot linking operations"""

    @pytest.mark.asyncio
    async def test_create_wiki_page_article_link(self, wiki_repo: InMemoryWikiPageRepository, 
                                                 sample_wiki_page, sample_article, test_user_id: UUID):
        """Test linking a wiki page to an article snapshot"""
        wiki = sample_wiki_page
        article = sample_article
        story_id = uuid4()
        
        # Create a snapshot first
        snapshot = await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=article.id, content="Article content", preview="Preview",
            last_safe_chapter=5, source_story_id=story_id, version_number=1,
            parent_snapshot_id=None
        ))
        
        # Create the link
        link_create = WikiPageArticleLinkCreate(
            wiki_page_id=wiki.id,
            article_snapshot_id=snapshot.id,
            display_order=1,
            is_featured=True
        )
        
        link = await wiki_repo.create_wiki_page_article_link(link_create)
        
        assert link.wiki_page_id == wiki.id
        assert link.article_snapshot_id == snapshot.id
        assert link.display_order == 1
        assert link.is_featured is True

    @pytest.mark.asyncio
    async def test_get_wiki_page_articles(self, wiki_repo: InMemoryWikiPageRepository,
                                         sample_wiki_page, sample_article, test_user_id: UUID):
        """Test getting article snapshots linked to a wiki page"""
        wiki = sample_wiki_page
        article = sample_article
        story_id = uuid4()
        
        # Create snapshots and links
        snapshot1 = await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=article.id, content="Content 1", preview="Preview 1",
            last_safe_chapter=3, source_story_id=story_id, version_number=1,
            parent_snapshot_id=None
        ))
        snapshot2 = await wiki_repo.create_article_snapshot(ArticleSnapshotCreate(
            article_id=article.id, content="Content 2", preview="Preview 2",
            last_safe_chapter=7, source_story_id=story_id, version_number=2,
            parent_snapshot_id=snapshot1.id
        ))
        
        await wiki_repo.create_wiki_page_article_link(WikiPageArticleLinkCreate(
            wiki_page_id=wiki.id, article_snapshot_id=snapshot1.id,
            display_order=2, is_featured=False
        ))
        await wiki_repo.create_wiki_page_article_link(WikiPageArticleLinkCreate(
            wiki_page_id=wiki.id, article_snapshot_id=snapshot2.id,
            display_order=1, is_featured=True
        ))
        
        # Get linked articles (should be sorted by display_order)
        links = await wiki_repo.get_wiki_page_article_links(wiki.id)
        
        assert len(links) == 2
        assert links[0].display_order == 1  # Featured one first
        assert links[1].display_order == 2 