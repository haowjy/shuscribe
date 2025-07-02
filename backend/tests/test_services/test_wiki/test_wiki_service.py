"""
Comprehensive tests for WikiService with memory repositories
"""

import pytest
from typing import Dict, Any, List
from uuid import uuid4

from src.schemas.db.wiki import (
    WikiArticle, WikiArticleCreate, WikiArticleUpdate, WikiArticleType,
    ChapterVersion, ArticleConnection
)
from src.schemas.db.workspace import Workspace
from src.services.wiki.wiki_service import WikiService
from src.database.factory import RepositoryContainer


@pytest.fixture
async def wiki_service(repository_container: RepositoryContainer) -> WikiService:
    """Provide WikiService with memory repositories."""
    return WikiService(
        wiki_repository=repository_container.wiki,
        workspace_repository=repository_container.workspace
    )


@pytest.fixture
async def sample_workspace(repository_container: RepositoryContainer) -> Workspace:
    """Create a sample workspace for wiki articles."""
    from src.schemas.db.user import UserCreate
    from src.schemas.db.workspace import WorkspaceCreate
    
    user = await repository_container.user.create_user(UserCreate(
        email="wiki_user@example.com",
        display_name="Wiki User"
    ))
    
    return await repository_container.workspace.create_workspace(WorkspaceCreate(
        owner_id=user.id,
        name="Wiki Workspace",
        description="Workspace for wiki testing"
    ))


@pytest.fixture
async def sample_article(wiki_service: WikiService, sample_workspace: Workspace) -> WikiArticle:
    """Create a sample wiki article for testing."""
    article_data = WikiArticleCreate(
        workspace_id=sample_workspace.id,
        title="Sample Character",
        content="A sample character for testing wiki functionality.",
        article_type=WikiArticleType.CHARACTER,
        tags=["main", "protagonist"],
    )
    return await wiki_service.create_article(article_data)


class TestArticleManagement:
    """Test wiki article CRUD operations"""
    
    async def test_create_article_success(self, wiki_service: WikiService, sample_workspace: Workspace):
        """Test creating a new wiki article"""
        article_data = WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Test Location",
            content="A mysterious location in the story.",
            article_type=WikiArticleType.LOCATION,
            tags=["mysterious", "important"],
            metadata={"region": "north"}
            )
        
        article = await wiki_service.create_article(article_data)
        
        assert article.id is not None
        assert article.workspace_id == sample_workspace.id
        assert article.title == "Test Location"
        assert article.content == "A mysterious location in the story."
        assert article.article_type == WikiArticleType.LOCATION
        assert article.tags == ["mysterious", "important"]
        assert article.metadata["region"] == "north"
        assert article.created_at is not None
    
    async def test_create_article_workspace_not_found(self, wiki_service: WikiService):
        """Test error when creating article for non-existent workspace"""
        fake_workspace_id = uuid4()
        article_data = WikiArticleCreate(
            workspace_id=fake_workspace_id,
            title="Test Article",
            content="Test content",
            article_type=WikiArticleType.CONCEPT,
        )
        
        with pytest.raises(ValueError) as exc_info:
            await wiki_service.create_article(article_data)
        
        assert f"Workspace {fake_workspace_id} not found" in str(exc_info.value)
    
    async def test_get_article_by_id(self, wiki_service: WikiService, sample_article: WikiArticle):
        """Test retrieving article by ID"""
        retrieved = await wiki_service.get_article(sample_article.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_article.id
        assert retrieved.title == sample_article.title
        assert retrieved.content == sample_article.content
    
    async def test_get_article_not_found(self, wiki_service: WikiService):
        """Test retrieving non-existent article returns None"""
        fake_id = uuid4()
        article = await wiki_service.get_article(fake_id)
        assert article is None
    
    async def test_update_article_success(self, wiki_service: WikiService, sample_article: WikiArticle):
        """Test updating article content and metadata"""
        update_data = WikiArticleUpdate(
            title="Updated Character",
            content="Updated character description with more details.",
            tags=["main", "protagonist", "updated"],
            metadata={"importance": "critical", "arc": "main"}
        )
        
        updated = await wiki_service.update_article(sample_article.id, update_data)
        
        assert updated.title == "Updated Character"
        assert updated.content == "Updated character description with more details."
        assert updated.tags == ["main", "protagonist", "updated"]
        assert updated.metadata["importance"] == "critical"
        assert updated.metadata["arc"] == "main"
        assert updated.article_type == sample_article.article_type  # Unchanged
    
    async def test_update_article_not_found(self, wiki_service: WikiService):
        """Test error when updating non-existent article"""
        fake_id = uuid4()
        update_data = WikiArticleUpdate(
            title="New Title",
            content=None
        )
        
        with pytest.raises(ValueError) as exc_info:
            await wiki_service.update_article(fake_id, update_data)
        
        assert f"Article {fake_id} not found" in str(exc_info.value)
    
    async def test_delete_article_success(self, wiki_service: WikiService, sample_article: WikiArticle):
        """Test deleting an article"""
        result = await wiki_service.delete_article(sample_article.id)
        assert result is True
        
        # Verify it's gone
        retrieved = await wiki_service.get_article(sample_article.id)
        assert retrieved is None
    
    async def test_delete_article_not_found(self, wiki_service: WikiService):
        """Test deleting non-existent article returns False"""
        fake_id = uuid4()
        result = await wiki_service.delete_article(fake_id)
        assert result is False


class TestArticleQueries:
    """Test article query operations"""
    
    async def test_get_articles_by_workspace(self, wiki_service: WikiService, sample_workspace: Workspace):
        """Test getting all articles for a workspace"""
        # Create multiple articles
        article_types = [WikiArticleType.CHARACTER, WikiArticleType.LOCATION, WikiArticleType.CONCEPT]
        created_articles = []
        
        for i, article_type in enumerate(article_types):
            article = await wiki_service.create_article(WikiArticleCreate(
                workspace_id=sample_workspace.id,
                title=f"Test {article_type.value} {i}",
                content=f"Content for {article_type.value} {i}",
                article_type=article_type
            ))
            created_articles.append(article)
        
        # Get all articles
        articles = await wiki_service.get_articles_by_workspace(sample_workspace.id)
        
        assert len(articles) == 3
        titles = [a.title for a in articles]
        assert "Test character 0" in titles
        assert "Test location 1" in titles
        assert "Test concept 2" in titles
    
    async def test_get_articles_by_workspace_filtered_by_type(self, wiki_service: WikiService, sample_workspace: Workspace):
        """Test filtering articles by type"""
        # Create articles of different types
        await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Character 1",
            content="A character",
            article_type=WikiArticleType.CHARACTER
        ))
        
        await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Location 1",
            content="A location",
            article_type=WikiArticleType.LOCATION
        ))
        
        await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Character 2",
            content="Another character",
            article_type=WikiArticleType.CHARACTER
        ))
        
        # Get only character articles
        characters = await wiki_service.get_articles_by_workspace(
            sample_workspace.id,
            article_type=WikiArticleType.CHARACTER
        )
        
        assert len(characters) == 2
        assert all(a.article_type == WikiArticleType.CHARACTER for a in characters)
        titles = [a.title for a in characters]
        assert "Character 1" in titles
        assert "Character 2" in titles
    
    async def test_search_articles_by_content(self, wiki_service: WikiService, sample_workspace: Workspace):
        """Test searching articles by content"""
        # Create articles with specific content
        await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Wizard Character",
            content="A powerful wizard who can cast magical spells.",
            article_type=WikiArticleType.CHARACTER
        ))
        
        await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Magic Tower",
            content="A tall tower where wizards study ancient magic.",
            article_type=WikiArticleType.LOCATION
        ))
        
        await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Sword Fighter",
            content="A warrior skilled with blade combat.",
            article_type=WikiArticleType.CHARACTER
        ))
        
        # Search for "magic"
        magic_articles = await wiki_service.search_articles(sample_workspace.id, "magic")
        
        assert len(magic_articles) == 2
        titles = [a.title for a in magic_articles]
        assert "Wizard Character" in titles
        assert "Magic Tower" in titles
        assert "Sword Fighter" not in titles
    
    async def test_get_articles_by_tags(self, wiki_service: WikiService, sample_workspace: Workspace):
        """Test filtering articles by tags"""
        # Create articles with different tags
        await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Hero",
            content="The main hero",
            article_type=WikiArticleType.CHARACTER,
            tags=["main", "protagonist", "hero"]
        ))
        
        await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Villain",
            content="The main villain",
            article_type=WikiArticleType.CHARACTER,
            tags=["main", "antagonist", "villain"]
        ))
        
        await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Side Character",
            content="A side character",
            article_type=WikiArticleType.CHARACTER,
            tags=["side", "supporting"]
        ))
        
        # Get articles with "main" tag
        main_articles = await wiki_service.get_articles_by_tags(sample_workspace.id, ["main"])
        
        assert len(main_articles) == 2
        titles = [a.title for a in main_articles]
        assert "Hero" in titles
        assert "Villain" in titles
        assert "Side Character" not in titles


class TestChapterVersions:
    """Test chapter-specific article versioning"""
    
    async def test_create_chapter_version(self, wiki_service: WikiService, sample_article: WikiArticle):
        """Test creating a chapter-specific version of an article"""
        chapter_number = 5
        content = "Character description safe through chapter 5."
        summary = "Basic character introduction"
        
        version = await wiki_service.create_chapter_version(
            sample_article.id,
            chapter_number,
            content,
            summary
        )
        
        assert version.article_id == sample_article.id
        assert version.chapter_number == chapter_number
        assert version.content == content
        assert version.summary == summary
        assert version.created_at is not None
    
    async def test_create_chapter_version_article_not_found(self, wiki_service: WikiService):
        """Test error when creating version for non-existent article"""
        fake_article_id = uuid4()
        
        with pytest.raises(ValueError) as exc_info:
            await wiki_service.create_chapter_version(
                fake_article_id,
                1,
                "content",
                "summary"
            )
        
        assert f"Article {fake_article_id} not found" in str(exc_info.value)
    
    async def test_get_article_at_chapter(self, wiki_service: WikiService, sample_article: WikiArticle):
        """Test retrieving article version safe through specific chapter"""
        # Create versions for different chapters
        await wiki_service.create_chapter_version(
            sample_article.id,
            3,
            "Content safe through chapter 3",
            "Early version"
        )
        
        await wiki_service.create_chapter_version(
            sample_article.id,
            7,
            "Content safe through chapter 7",
            "Mid version"
        )
        
        await wiki_service.create_chapter_version(
            sample_article.id,
            10,
            "Content safe through chapter 10",
            "Late version"
        )
        
        # Get version for chapter 5 (should get chapter 3 version)
        version = await wiki_service.get_article_at_chapter(sample_article.id, 5)
        
        assert version is not None
        assert version.chapter_number == 3
        assert version.content == "Content safe through chapter 3"
        
        # Get version for chapter 8 (should get chapter 7 version)
        version = await wiki_service.get_article_at_chapter(sample_article.id, 8)
        
        assert version is not None
        assert version.chapter_number == 7
        assert version.content == "Content safe through chapter 7"
    
    async def test_get_article_at_chapter_no_version(self, wiki_service: WikiService, sample_article: WikiArticle):
        """Test retrieving article version when no suitable version exists"""
        # Request version for chapter 1 when no versions exist
        version = await wiki_service.get_article_at_chapter(sample_article.id, 1)
        assert version is None
    
    async def test_get_chapter_versions(self, wiki_service: WikiService, sample_article: WikiArticle):
        """Test retrieving all chapter versions for an article"""
        # Create multiple versions
        chapters = [1, 5, 10, 15]
        for chapter in chapters:
            await wiki_service.create_chapter_version(
                sample_article.id,
                chapter,
                f"Content for chapter {chapter}",
                f"Summary {chapter}"
            )
        
        # Get all versions
        versions = await wiki_service.get_chapter_versions(sample_article.id)
        
        assert len(versions) == 4
        version_chapters = [v.chapter_number for v in versions]
        assert sorted(version_chapters) == [1, 5, 10, 15]


class TestArticleConnections:
    """Test connections between articles"""
    
    async def test_create_connection(self, wiki_service: WikiService, sample_workspace: Workspace):
        """Test creating a connection between two articles"""
        # Create two articles
        article1 = await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Character A",
            content="First character",
            article_type=WikiArticleType.CHARACTER
        ))
        
        article2 = await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Character B",
            content="Second character",
            article_type=WikiArticleType.CHARACTER
        ))
        
        # Create connection
        connection = await wiki_service.create_connection(
            article1.id,
            article2.id,
            "friend",
            "They are close friends",
            0.8
        )
        
        assert connection.from_article_id == article1.id
        assert connection.to_article_id == article2.id
        assert connection.connection_type == "friend"
        assert connection.description == "They are close friends"
        assert connection.strength == 0.8
    
    async def test_create_connection_article_not_found(self, wiki_service: WikiService, sample_article: WikiArticle):
        """Test error when creating connection with non-existent article"""
        fake_article_id = uuid4()
        
        with pytest.raises(ValueError) as exc_info:
            await wiki_service.create_connection(
                sample_article.id,
                fake_article_id,
                "related",
                "Some relation"
            )
        
        assert "not found" in str(exc_info.value)
    
    async def test_get_article_connections(self, wiki_service: WikiService, sample_workspace: Workspace):
        """Test retrieving all connections for an article"""
        # Create three articles
        main_article = await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Main Character",
            content="The protagonist",
            article_type=WikiArticleType.CHARACTER
        ))
        
        friend_article = await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Friend",
            content="A friend",
            article_type=WikiArticleType.CHARACTER
        ))
        
        enemy_article = await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Enemy",
            content="An enemy",
            article_type=WikiArticleType.CHARACTER
        ))
        
        # Create connections
        await wiki_service.create_connection(
            main_article.id,
            friend_article.id,
            "friend",
            "Close friend"
        )
        
        await wiki_service.create_connection(
            main_article.id,
            enemy_article.id,
            "enemy",
            "Sworn enemy"
        )
        
        # Get connections
        connections = await wiki_service.get_article_connections(main_article.id)
        
        assert len(connections) == 2
        connection_types = [c.connection_type for c in connections]
        assert "friend" in connection_types
        assert "enemy" in connection_types


class TestWikiStatistics:
    """Test wiki statistics and analytics"""
    
    async def test_get_wiki_statistics(self, wiki_service: WikiService, sample_workspace: Workspace):
        """Test retrieving comprehensive wiki statistics"""
        # Create articles of different types
        for i in range(3):
            await wiki_service.create_article(WikiArticleCreate(
                workspace_id=sample_workspace.id,
                title=f"Character {i}",
                content=f"Character content {i}",
                article_type=WikiArticleType.CHARACTER
            ))
        
        for i in range(2):
            await wiki_service.create_article(WikiArticleCreate(
                workspace_id=sample_workspace.id,
                title=f"Location {i}",
                content=f"Location content {i}",
                article_type=WikiArticleType.LOCATION
            ))
        
        await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Concept",
            content="Concept content",
            article_type=WikiArticleType.CONCEPT
        ))
        
        # Get statistics
        stats = await wiki_service.get_wiki_statistics(sample_workspace.id)
        
        assert stats["total_articles"] == 6
        assert stats["character_count"] == 3
        assert stats["location_count"] == 2
        assert stats["concept_count"] == 1
        assert stats["workspace_id"] == sample_workspace.id


class TestIntegration:
    """Integration tests for wiki workflows"""
    
    async def test_full_wiki_workflow(self, wiki_service: WikiService, sample_workspace: Workspace):
        """Test complete wiki creation and management workflow"""
        # 1. Create main character article
        hero = await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Hero Protagonist",
            content="The main character of the story.",
            article_type=WikiArticleType.CHARACTER,
            tags=["main", "protagonist"]
        ))
        
        # 2. Create location article
        hometown = await wiki_service.create_article(WikiArticleCreate(
            workspace_id=sample_workspace.id,
            title="Hero's Hometown",
            content="Where the hero grew up.",
            article_type=WikiArticleType.LOCATION,
            tags=["starting", "peaceful"]
        ))
        
        # 3. Create connection between character and location
        await wiki_service.create_connection(
            hero.id,
            hometown.id,
            "origin",
            "Hero was born and raised here",
            1.0
        )
        
        # 4. Create chapter versions
        await wiki_service.create_chapter_version(
            hero.id,
            3,
            "Basic hero introduction - name and appearance only.",
            "Early introduction"
        )
        
        await wiki_service.create_chapter_version(
            hero.id,
            8,
            "Hero's background, family, and basic motivations revealed.",
            "Background revealed"
        )
        
        # 5. Update articles
        await wiki_service.update_article(hero.id, WikiArticleUpdate(
            content="The main character - a brave warrior seeking justice.",
            tags=["main", "protagonist", "warrior"]
        ))
        
        # 6. Test search functionality
        warrior_articles = await wiki_service.search_articles(sample_workspace.id, "warrior")
        assert len(warrior_articles) == 1
        assert warrior_articles[0].id == hero.id
        
        # 7. Test version retrieval
        early_version = await wiki_service.get_article_at_chapter(hero.id, 5)
        assert early_version is not None
        assert early_version.chapter_number == 3
        
        # 8. Test connections
        connections = await wiki_service.get_article_connections(hero.id)
        assert len(connections) == 1
        assert connections[0].connection_type == "origin"
        
        # 9. Get final statistics
        stats = await wiki_service.get_wiki_statistics(sample_workspace.id)
        assert stats["total_articles"] == 2
        assert stats["character_count"] == 1
        assert stats["location_count"] == 1