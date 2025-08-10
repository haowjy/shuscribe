"""
Tests for database seeding functionality
"""

import pytest
from typing import Dict, Any

from src.database.factory import create_repositories
from src.database.seeder import DatabaseSeeder
from src.database.utils import ProjectStatisticsService


class TestDatabaseSeeding:
    """Test database seeding functionality across backends"""
    
    @pytest.fixture(params=["memory", "database"])
    async def repos(self, request):
        """Provide both memory and database repository implementations"""
        if request.param == "database":
            # Initialize database for database backend tests
            from src.database.connection import init_database, create_tables, close_database
            
            # Initialize database connection
            init_database()
            
            # Create fresh tables (drop existing to ensure clean state)
            await create_tables(drop_existing=True)
            
            repos = create_repositories(backend=request.param)
            
            yield repos
            
            # Cleanup
            await close_database()
        else:
            repos = create_repositories(backend=request.param)
            yield repos
    
    async def test_basic_seeding_functionality(self, repos):
        """Test basic seeding creates expected data"""
        seeder = DatabaseSeeder(repos)
        
        # Test small dataset seeding
        results = await seeder.seed_database(clear_first=True, data_size="small")
        
        # Verify no errors
        assert "error" not in results
        assert len(results.get("errors", [])) == 0
        
        # Verify data was created
        assert results["tags_created"] > 0
        assert results["projects_created"] > 0
        assert results["documents_created"] > 0
        assert results["file_tree_items_created"] > 0
        
        # Verify expected small dataset size (1 project)
        assert results["projects_created"] == 1
        
        # Verify data exists in repositories
        all_projects = await repos.project.list_all()
        assert len(all_projects) == 1
        
        all_tags = await repos.tag.get_global_tags()
        assert len(all_tags) > 0
    
    async def test_seeding_word_count_calculation(self, repos):
        """Test that seeding correctly calculates project word counts"""
        seeder = DatabaseSeeder(repos)
        
        # Seed data
        results = await seeder.seed_database(clear_first=True, data_size="small")
        assert results["projects_created"] == 1
        
        # Get the created project
        all_projects = await repos.project.list_all()
        project = all_projects[0]
        
        # Verify word count is correctly calculated (not zero)
        assert project.word_count > 0
        assert project.document_count > 0
        
        # Verify word count matches actual documents
        documents = await repos.document.get_by_project_id(project.id)
        expected_word_count = sum(doc.word_count for doc in documents)
        expected_doc_count = len(documents)
        
        assert project.word_count == expected_word_count
        assert project.document_count == expected_doc_count
    
    async def test_seeding_data_sizes(self, repos):
        """Test different seeding data sizes"""
        seeder = DatabaseSeeder(repos)
        
        # Test medium dataset
        results = await seeder.seed_database(clear_first=True, data_size="medium")
        assert results["projects_created"] == 2
        
        # Clear and test large dataset
        results = await seeder.seed_database(clear_first=True, data_size="large")
        assert results["projects_created"] == 3
    
    async def test_seeding_project_structure(self, repos):
        """Test that seeded projects have proper structure"""
        seeder = DatabaseSeeder(repos)
        
        # Seed data
        results = await seeder.seed_database(clear_first=True, data_size="small")
        
        # Get the project
        all_projects = await repos.project.list_all()
        project = all_projects[0]
        
        # Verify project has expected properties
        assert project.title is not None
        assert len(project.title) > 0
        assert project.description is not None
        assert len(project.tags) > 0
        assert project.created_at is not None
        assert project.updated_at is not None
        
        # Verify file tree structure
        file_tree = await repos.file_tree.get_by_project_id(project.id)
        assert len(file_tree) > 0
        
        # Should have both folders and files
        folders = [item for item in file_tree if item.type == "folder"]
        files = [item for item in file_tree if item.type == "file"]
        
        assert len(folders) > 0
        assert len(files) > 0
        
        # Files should have document references
        for file_item in files:
            if file_item.document_id:
                doc = await repos.document.get_by_id(file_item.document_id)
                assert doc is not None
                assert doc.project_id == project.id
    
    async def test_seeding_clears_existing_data(self, repos):
        """Test that seeding with clear_first=True removes existing data"""
        seeder = DatabaseSeeder(repos)
        
        # Seed initial data
        await seeder.seed_database(clear_first=True, data_size="small")
        initial_projects = await repos.project.list_all()
        assert len(initial_projects) == 1
        
        # Seed again with different size
        await seeder.seed_database(clear_first=True, data_size="medium")
        final_projects = await repos.project.list_all()
        assert len(final_projects) == 2  # Should be new data, not added to old
        
        # Project IDs should be different (new projects, not same ones)
        final_ids = {p.id for p in final_projects}
        initial_ids = {p.id for p in initial_projects}
        assert final_ids != initial_ids
    
    async def test_seeding_without_clear(self, repos):
        """Test seeding without clearing adds to existing data"""
        seeder = DatabaseSeeder(repos)
        
        # Seed initial data
        await seeder.seed_database(clear_first=True, data_size="small")
        initial_projects = await repos.project.list_all()
        initial_count = len(initial_projects)
        
        # Seed again without clearing
        await seeder.seed_database(clear_first=False, data_size="small")
        final_projects = await repos.project.list_all()
        
        # Should have added to existing data
        assert len(final_projects) == initial_count + 1


class TestProjectStatisticsService:
    """Test the ProjectStatisticsService functionality"""
    
    @pytest.fixture(params=["memory"])  # Focus on memory for service testing
    async def repos(self, request):
        """Provide repository implementations for statistics service testing"""
        repos = create_repositories(backend=request.param)
        return repos
    
    async def test_manual_statistics_recalculation(self, repos):
        """Test ProjectStatisticsService manual recalculation"""
        # Create test project with wrong statistics
        project_data = {
            "id": "stats-service-test",
            "title": "Statistics Service Test",
            "word_count": 999,  # Wrong
            "document_count": 888  # Wrong
        }
        project = await repos.project.create(project_data)
        
        # Create some documents
        doc1 = await repos.document.create({
            "id": "service-doc-1",
            "project_id": project.id,
            "title": "Doc 1",
            "path": "/doc1.md",
            "word_count": 150
        })
        
        doc2 = await repos.document.create({
            "id": "service-doc-2", 
            "project_id": project.id,
            "title": "Doc 2",
            "path": "/doc2.md",
            "word_count": 300
        })
        
        # Use service to recalculate
        stats_service = ProjectStatisticsService(repos)
        updated_project = await stats_service.recalculate_project_statistics(project.id)
        
        # Verify correction
        assert updated_project is not None
        assert updated_project.word_count == 450  # 150 + 300
        assert updated_project.document_count == 2
    
    async def test_bulk_statistics_refresh(self, repos):
        """Test bulk statistics refresh for all projects"""
        # Create multiple projects with wrong statistics
        projects_data = [
            {"id": "bulk-1", "title": "Bulk Test 1", "word_count": 0, "document_count": 0},
            {"id": "bulk-2", "title": "Bulk Test 2", "word_count": 99, "document_count": 88},
        ]
        
        created_projects = []
        for data in projects_data:
            project = await repos.project.create(data)
            created_projects.append(project)
            
            # Add a document to each
            await repos.document.create({
                "id": f"doc-{data['id']}",
                "project_id": project.id,
                "title": f"Document for {data['title']}",
                "path": f"/{data['id']}.md",
                "word_count": 200
            })
        
        # Use service to refresh all
        stats_service = ProjectStatisticsService(repos)
        results = await stats_service.refresh_all_project_statistics()
        
        # Verify results
        assert results["updated"] == 2
        assert results["total"] == 2
        assert len(results["errors"]) == 0
        
        # Verify all projects now have correct statistics
        for project_data in projects_data:
            updated_project = await repos.project.get_by_id(project_data["id"])
            assert updated_project.word_count == 200
            assert updated_project.document_count == 1


class TestSeedingIntegration:
    """Integration tests combining seeding with other functionality"""
    
    @pytest.fixture
    async def seeded_repos(self):
        """Provide pre-seeded memory repositories"""
        repos = create_repositories(backend="memory")
        seeder = DatabaseSeeder(repos)
        
        # Seed with medium dataset
        await seeder.seed_database(clear_first=True, data_size="medium")
        
        return repos
    
    async def test_seeding_with_statistics_service(self, seeded_repos):
        """Test that seeded data works correctly with statistics service"""
        repos = seeded_repos
        
        # Get all projects
        all_projects = await repos.project.list_all()
        assert len(all_projects) == 2  # Medium dataset
        
        # Corrupt statistics for one project
        project = all_projects[0]
        corrupted_project = await repos.project.update(project.id, {
            "word_count": 0,
            "document_count": 0
        })
        
        # Use statistics service to fix
        stats_service = ProjectStatisticsService(repos)
        fixed_project = await stats_service.recalculate_project_statistics(project.id)
        
        # Should be restored to proper values
        assert fixed_project.word_count > 0
        assert fixed_project.document_count > 0
        
        # Should match the documents
        documents = await repos.document.get_by_project_id(project.id)
        expected_word_count = sum(doc.word_count for doc in documents)
        expected_doc_count = len(documents)
        
        assert fixed_project.word_count == expected_word_count
        assert fixed_project.document_count == expected_doc_count
    
    async def test_seeded_project_relationships(self, seeded_repos):
        """Test that seeded data has proper relationships"""
        repos = seeded_repos
        
        # Get all projects and verify relationships
        all_projects = await repos.project.list_all()
        
        for project in all_projects:
            # Get documents
            documents = await repos.document.get_by_project_id(project.id)
            assert len(documents) > 0
            
            # Get file tree
            file_tree = await repos.file_tree.get_by_project_id(project.id)
            assert len(file_tree) > 0
            
            # Verify file-document relationships
            files = [item for item in file_tree if item.type == "file"]
            for file_item in files:
                if file_item.document_id:
                    # Document should exist and belong to project
                    doc = await repos.document.get_by_id(file_item.document_id)
                    assert doc is not None
                    assert doc.project_id == project.id
                    
                    # File path should match document path
                    assert file_item.path == doc.path