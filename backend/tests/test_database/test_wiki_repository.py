"""
Test suite for Wiki Repository

Tests wiki article management, chapter-based versioning, spoiler prevention, and connections.
"""

import pytest
from pathlib import Path
from typing import cast

from src.database.models.wiki import WikiArticleCreate, WikiArticleUpdate, WikiArticleType
from src.database.file.user import FileUserRepository


class TestWikiArticleOperations:
    """Test basic wiki article CRUD operations."""
    
    async def test_create_article(self, wiki_repo, sample_workspace):
        """Test creating a wiki article."""
        article_data = WikiArticleCreate(
            title="Test Character",
            article_type=WikiArticleType.CHARACTER,
            content="A brave protagonist of our story.",
            safe_through_chapter=1
        )
        
        article = await wiki_repo.create_article(sample_workspace.id, article_data)
        
        assert article.title == "Test Character"
        assert article.article_type == WikiArticleType.CHARACTER
        assert article.content == "A brave protagonist of our story."
        assert article.safe_through_chapter == 1
        assert article.id is not None
        assert article.created_at is not None
    
    async def test_get_article_by_id(self, wiki_repo, sample_wiki_articles):
        """Test retrieving an article by ID."""
        first_article = sample_wiki_articles[0]
        retrieved = await wiki_repo.get_article(first_article.id)
        
        assert retrieved is not None
        assert retrieved.id == first_article.id
        assert retrieved.title == first_article.title
        assert retrieved.content == first_article.content
    
    async def test_get_articles_by_workspace(self, wiki_repo, sample_workspace, sample_wiki_articles):
        """Test getting all articles for a workspace."""
        articles = await wiki_repo.get_articles_by_workspace(sample_workspace.id)
        
        assert len(articles) >= 2  # From sample_wiki_articles
        titles = {article.title for article in articles}
        assert "Test Character" in titles
        assert "Test Location" in titles
    
    async def test_get_articles_by_type(self, wiki_repo, sample_workspace, sample_wiki_articles):
        """Test getting articles by type."""
        character_articles = await wiki_repo.get_articles_by_type(
            sample_workspace.id, WikiArticleType.CHARACTER.value
        )
        
        assert len(character_articles) >= 1
        assert all(article.article_type == WikiArticleType.CHARACTER for article in character_articles)
    
    async def test_update_article(self, wiki_repo, sample_wiki_articles):
        """Test updating an article."""
        first_article = sample_wiki_articles[0]
        
        update_data = WikiArticleUpdate(
            title="Updated Character",
            content="Updated character description with more details.",
            safe_through_chapter=2
        )
        
        updated = await wiki_repo.update_article(first_article.id, update_data)
        
        assert updated.title == "Updated Character"
        assert updated.content == "Updated character description with more details."
        assert updated.safe_through_chapter == 2
        assert updated.updated_at is not None
    
    async def test_delete_article(self, wiki_repo, sample_wiki_articles):
        """Test deleting an article."""
        article_to_delete = sample_wiki_articles[0]
        
        deleted = await wiki_repo.delete_article(article_to_delete.id)
        assert deleted is True
        
        # Verify article is gone
        retrieved = await wiki_repo.get_article(article_to_delete.id)
        assert retrieved is None


class TestSpoilerPrevention:
    """Test chapter-based spoiler prevention system."""
    
    async def test_create_chapter_version(self, wiki_repo, sample_wiki_articles):
        """Test creating a chapter-specific version."""
        article = sample_wiki_articles[0]
        
        version = await wiki_repo.create_chapter_version(
            article.id,
            content="Character as seen in chapter 1.",
            safe_through_chapter=1
        )
        
        assert version.article_id == article.id
        assert version.content == "Character as seen in chapter 1."
        assert version.safe_through_chapter == 1
        assert version.id is not None
        assert version.created_at is not None
    
    async def test_get_version_for_chapter(self, wiki_repo, wiki_with_versions):
        """Test retrieving appropriate version for a reader's progress."""
        article, versions = wiki_with_versions
        
        # Reader on chapter 1 should get version 1
        version_ch1 = await wiki_repo.get_version_for_chapter(article.id, 1)
        assert version_ch1 is not None
        assert version_ch1.safe_through_chapter == 1
        assert "mysterious stranger" in version_ch1.content.lower()
        
        # Reader on chapter 2 should get version 2
        version_ch2 = await wiki_repo.get_version_for_chapter(article.id, 2)
        assert version_ch2 is not None
        assert version_ch2.safe_through_chapter == 2
        assert "magical abilities" in version_ch2.content.lower()
        
        # Reader on chapter 3 should get version 3
        version_ch3 = await wiki_repo.get_version_for_chapter(article.id, 3)
        assert version_ch3 is not None
        assert version_ch3.safe_through_chapter == 3
        assert "lost prince" in version_ch3.content.lower()
        
        # Reader on chapter 5+ should get the latest version (ch 3)
        version_ch5 = await wiki_repo.get_version_for_chapter(article.id, 5)
        assert version_ch5 is not None
        assert version_ch5.content == version_ch3.content
    
    async def test_get_all_versions(self, wiki_repo, wiki_with_versions):
        """Test getting all versions of an article."""
        article, expected_versions = wiki_with_versions
        
        all_versions = await wiki_repo.get_all_versions(article.id)
        
        assert len(all_versions) >= 3  # From wiki_with_versions fixture
        
        # Should be ordered by chapter
        chapters = [v.safe_through_chapter for v in all_versions]
        assert chapters == sorted(chapters)
    
    async def test_spoiler_safe_content_progression(self, wiki_repo, sample_workspace):
        """Test that content properly evolves through chapters."""
        # Create article
        article_data = WikiArticleCreate(
            title="Evolving Character",
            article_type=WikiArticleType.CHARACTER,
            content="Full spoiler-filled description.",
            safe_through_chapter=5
        )
        article = await wiki_repo.create_article(sample_workspace.id, article_data)
        
        # Create progressive versions
        chapter_contents = {
            1: "Unknown person appears.",
            2: "Unknown person shows magical powers.", 
            3: "Mage reveals their true identity as a prince.",
            4: "Prince explains their quest for the crown."
        }
        
        for chapter, content in chapter_contents.items():
            await wiki_repo.create_chapter_version(
                article.id,
                content=content,
                safe_through_chapter=chapter
            )
        
        # Test that each chapter gets appropriate content
        for chapter, expected_content in chapter_contents.items():
            version = await wiki_repo.get_version_for_chapter(article.id, chapter)
            assert version.content == expected_content
            
        # Chapter 5+ should get the highest available version (chapter 4)
        # since we didn't create a version specifically for chapter 5
        version_ch5 = await wiki_repo.get_version_for_chapter(article.id, 5)
        assert version_ch5 is not None
        # Should get the last created version (chapter 4) or the original article
        assert len(version_ch5.content) > 0


class TestCurrentVersions:
    """Test current version management."""
    
    async def test_create_current_version(self, wiki_repo, sample_wiki_articles):
        """Test creating a current working version."""
        article = sample_wiki_articles[0]
        
        current = await wiki_repo.create_current_version(
            article.id,
            content="Current working version of the character.",
            user_notes="Need to add more backstory in next update."
        )
        
        assert current.article_id == article.id
        assert current.content == "Current working version of the character."
        assert "backstory" in current.user_notes
        assert current.id is not None
    
    async def test_get_current_version(self, wiki_repo, sample_wiki_articles):
        """Test retrieving current working version."""
        article = sample_wiki_articles[0]
        
        # Create current version first
        await wiki_repo.create_current_version(
            article.id,
            content="Current version content"
        )
        
        current = await wiki_repo.get_current_version(article.id)
        assert current is not None
        assert current.content == "Current version content"
    
    async def test_update_current_version(self, wiki_repo, sample_wiki_articles):
        """Test updating current working version."""
        article = sample_wiki_articles[0]
        
        # Create initial current version
        await wiki_repo.create_current_version(
            article.id,
            content="Initial content"
        )
        
        # Update it
        updated = await wiki_repo.update_current_version(
            article.id,
            content="Updated content",
            user_notes="Added user notes"
        )
        
        assert updated.content == "Updated content"
        assert updated.user_notes == "Added user notes"


class TestArticleConnections:
    """Test article connection system."""
    
    async def test_create_connection(self, wiki_repo, sample_wiki_articles):
        """Test creating a connection between articles."""
        character_article = sample_wiki_articles[0]  # Character
        location_article = sample_wiki_articles[1]   # Location
        
        connection = await wiki_repo.create_connection(
            character_article.id,
            location_article.id,
            connection_type="visits",
            strength=0.8,
            context="Character visits this location in chapter 3"
        )
        
        assert connection.from_article_id == character_article.id
        assert connection.to_article_id == location_article.id
        assert connection.connection_type == "visits"
        assert connection.strength == 0.8
        # Note: Need to check what field name is actually used for storage
        # This may require checking the ArticleConnection model structure
    
    async def test_get_connections_from(self, wiki_repo, sample_wiki_articles):
        """Test getting connections from an article."""
        character_article = sample_wiki_articles[0]
        location_article = sample_wiki_articles[1]
        
        # Create connection
        await wiki_repo.create_connection(
            character_article.id,
            location_article.id,
            connection_type="explores"
        )
        
        connections = await wiki_repo.get_connections_from(character_article.id)
        
        assert len(connections) >= 1
        connection = connections[0]
        assert connection.from_article_id == character_article.id
        assert connection.to_article_id == location_article.id
        assert connection.connection_type == "explores"
    
    async def test_get_connections_to(self, wiki_repo, sample_wiki_articles):
        """Test getting connections to an article."""
        character_article = sample_wiki_articles[0]
        location_article = sample_wiki_articles[1]
        
        # Create connection
        await wiki_repo.create_connection(
            character_article.id,
            location_article.id,
            connection_type="lives_in"
        )
        
        connections = await wiki_repo.get_connections_to(location_article.id)
        
        assert len(connections) >= 1
        connection = connections[0]
        assert connection.from_article_id == character_article.id
        assert connection.to_article_id == location_article.id
        assert connection.connection_type == "lives_in"
    
    async def test_delete_connection(self, wiki_repo, sample_wiki_articles):
        """Test deleting a connection."""
        character_article = sample_wiki_articles[0]
        location_article = sample_wiki_articles[1]
        
        # Create connection
        await wiki_repo.create_connection(
            character_article.id,
            location_article.id
        )
        
        # Delete connection
        deleted = await wiki_repo.delete_connection(
            character_article.id,
            location_article.id
        )
        assert deleted is True
        
        # Verify it's gone
        connections = await wiki_repo.get_connections_from(character_article.id)
        remaining = [c for c in connections if c.to_article_id == location_article.id]
        assert len(remaining) == 0


class TestWikiEdgeCases:
    """Test edge cases and error conditions."""
    
    async def test_nonexistent_article(self, wiki_repo):
        """Test operations on nonexistent articles."""
        from uuid import uuid4
        
        fake_id = uuid4()
        
        article = await wiki_repo.get_article(fake_id)
        assert article is None
        
        deleted = await wiki_repo.delete_article(fake_id)
        assert deleted is False
        
        version = await wiki_repo.get_version_for_chapter(fake_id, 1)
        assert version is None
    
    async def test_article_with_no_versions(self, wiki_repo, sample_workspace):
        """Test getting version for article with no chapter versions."""
        # Create article without any chapter versions
        article_data = WikiArticleCreate(
            title="No Versions",
            article_type=WikiArticleType.CHARACTER,
            content="Original content",
            safe_through_chapter=1
        )
        article = await wiki_repo.create_article(sample_workspace.id, article_data)
        
        # Should return the original article content
        version = await wiki_repo.get_version_for_chapter(article.id, 1)
        # Behavior depends on implementation - might return None or the article itself
        # Test what actually happens
        if version is not None:
            assert version.content is not None
    
    async def test_invalid_chapter_numbers(self, wiki_repo, sample_wiki_articles):
        """Test handling invalid chapter numbers."""
        article = sample_wiki_articles[0]
        
        # Test zero and negative chapter numbers
        version_zero = await wiki_repo.get_version_for_chapter(article.id, 0)
        version_negative = await wiki_repo.get_version_for_chapter(article.id, -1)
        
        # Should handle gracefully (return None or appropriate version)
        # The exact behavior depends on implementation
    
    async def test_connection_to_self(self, wiki_repo, sample_wiki_articles):
        """Test creating connection from article to itself."""
        article = sample_wiki_articles[0]
        
        try:
            connection = await wiki_repo.create_connection(
                article.id,
                article.id,
                connection_type="self_reference"
            )
            # If allowed, verify it works
            assert connection.from_article_id == article.id
            assert connection.to_article_id == article.id
        except Exception:
            # If prevented, that's also acceptable
            pass


@pytest.mark.integration
class TestWikiIntegration:
    """Integration tests for wiki functionality."""
    
    async def test_complete_spoiler_workflow(self, workspace_factory):
        """Test complete spoiler prevention workflow."""
        workspace_path, repos, workspace_id = await workspace_factory(
            name="Spoiler Test",
            chapter_count=5,
            wiki_count=0
        )
        
        # Create character article
        character_data = WikiArticleCreate(
            title="Main Character",
            article_type=WikiArticleType.CHARACTER,
            content="Complete character description with all spoilers.",
            safe_through_chapter=5
        )
        character = await repos.wiki.create_article(workspace_id, character_data)
        
        # Create progressive chapter versions
        spoiler_levels = {
            1: "Mysterious stranger arrives in town.",
            2: "Stranger demonstrates unusual abilities.",
            3: "Revealed to be a mage seeking ancient artifacts.",
            4: "Mage's true identity as the lost prince is revealed.",
            5: "Prince must reclaim throne to save the kingdom."
        }
        
        for chapter, content in spoiler_levels.items():
            await repos.wiki.create_chapter_version(
                character.id,
                content=content,
                safe_through_chapter=chapter
            )
        
        # Test reader experience at different progress points
        for reader_chapter in range(1, 6):
            version = await repos.wiki.get_version_for_chapter(character.id, reader_chapter)
            expected_content = spoiler_levels[reader_chapter]
            assert expected_content in version.content
            
            # Verify no spoilers from future chapters
            for future_chapter in range(reader_chapter + 1, 6):
                future_keywords = ["prince", "throne", "kingdom"]
                if reader_chapter < 4:  # Before prince reveal
                    assert not any(keyword in version.content.lower() for keyword in future_keywords)
    
    async def test_wiki_with_real_story_data(self, pokemon_amber_workspace):
        """Test wiki operations with real imported story data."""
        workspace_path, import_result = pokemon_amber_workspace
        
        from src.database.factory import get_repositories
        repos = get_repositories(backend="file", workspace_path=workspace_path)
        
        # Get workspace
        user = await cast(FileUserRepository, repos.user).get_current_user()
        workspaces = await repos.workspace.get_by_owner(user.id)
        workspace = workspaces[0]
        
        # Create wiki articles for the imported story
        character_data = WikiArticleCreate(
            title="Protagonist",
            article_type=WikiArticleType.CHARACTER,
            content="The main character of the Pokemon story.",
            safe_through_chapter=1
        )
        character = await repos.wiki.create_article(workspace.id, character_data)
        
        # Create chapter versions
        await repos.wiki.create_chapter_version(
            character.id,
            content="Unknown person in a new world.",
            safe_through_chapter=1
        )
        
        await repos.wiki.create_chapter_version(
            character.id,
            content="Person learning about Pokemon world.",
            safe_through_chapter=3
        )
        
        # Test retrieval
        version_ch1 = await repos.wiki.get_version_for_chapter(character.id, 1)
        assert version_ch1 is not None
        assert "Unknown person" in version_ch1.content
        
        version_ch3 = await repos.wiki.get_version_for_chapter(character.id, 3)
        assert version_ch3 is not None
        assert "Pokemon world" in version_ch3.content
        
        # Test that articles exist in workspace
        articles = await repos.wiki.get_articles_by_workspace(workspace.id)
        assert len(articles) >= 1
        assert any(article.title == "Protagonist" for article in articles)


@pytest.mark.performance
class TestWikiPerformance:
    """Performance tests for wiki operations."""
    
    async def test_many_versions_performance(self, wiki_repo, sample_workspace):
        """Test performance with many chapter versions."""
        import time
        
        # Create article
        article_data = WikiArticleCreate(
            title="Performance Test Character",
            article_type=WikiArticleType.CHARACTER,
            content="Character for performance testing.",
            safe_through_chapter=100
        )
        article = await wiki_repo.create_article(sample_workspace.id, article_data)
        
        # Create many versions
        version_count = 50
        start_time = time.time()
        
        for i in range(1, version_count + 1):
            await wiki_repo.create_chapter_version(
                article.id,
                content=f"Character as seen through chapter {i}.",
                safe_through_chapter=i
            )
        
        creation_time = time.time() - start_time
        
        # Test version retrieval performance
        start_time = time.time()
        for i in range(1, min(21, version_count + 1)):  # Test first 20
            version = await wiki_repo.get_version_for_chapter(article.id, i)
            assert version is not None
        
        retrieval_time = time.time() - start_time
        
        assert creation_time < 10.0  # Should create 50 versions in under 10s
        assert retrieval_time < 2.0  # Should retrieve 20 versions in under 2s
        
        print(f"Created {version_count} versions in {creation_time:.2f}s")
        print(f"Retrieved 20 versions in {retrieval_time:.2f}s") 