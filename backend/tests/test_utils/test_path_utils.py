"""
Tests for path utilities
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.utils.path_utils import (
    normalize_path,
    parse_path_segments,
    extract_folder_path,
    ensure_folder_hierarchy_exists,
    validate_document_path,
    get_folder_name_from_path
)
from src.database.interfaces.models import FileTreeItem
from datetime import datetime, UTC


class TestNormalizePath:
    """Test path normalization functionality"""
    
    def test_normalize_already_normalized_path(self):
        """Test that already normalized paths remain unchanged"""
        assert normalize_path("/characters/elara") == "/characters/elara"
        assert normalize_path("/characters") == "/characters"
        assert normalize_path("/") == "/"
    
    def test_normalize_path_without_leading_slash(self):
        """Test adding leading slash"""
        assert normalize_path("characters/elara") == "/characters/elara"
        assert normalize_path("characters") == "/characters"
    
    def test_normalize_path_with_trailing_slash(self):
        """Test removing trailing slash"""
        assert normalize_path("/characters/elara/") == "/characters/elara"
        assert normalize_path("/characters/") == "/characters"
        assert normalize_path("/") == "/"  # Root should keep slash
    
    def test_normalize_path_with_double_slashes(self):
        """Test cleaning up double slashes"""
        assert normalize_path("/characters//elara") == "/characters/elara"
        assert normalize_path("//characters/elara//") == "/characters/elara"
    
    def test_normalize_empty_paths(self):
        """Test handling empty or whitespace paths"""
        assert normalize_path("") == "/"
        assert normalize_path("   ") == "/"
        assert normalize_path(None) == "/"
    
    def test_normalize_complex_paths(self):
        """Test complex path normalization scenarios"""
        assert normalize_path(" /characters//locations/../locations/taverns/ ") == "/characters/locations/taverns"
        assert normalize_path("characters/./elara") == "/characters/elara"


class TestParsePathSegments:
    """Test path segment parsing"""
    
    def test_parse_multilevel_path(self):
        """Test parsing multi-level paths"""
        result = parse_path_segments("/characters/locations/taverns")
        expected = ["/characters", "/characters/locations", "/characters/locations/taverns"]
        assert result == expected
    
    def test_parse_single_level_path(self):
        """Test parsing single-level paths"""
        result = parse_path_segments("/characters")
        expected = ["/characters"]
        assert result == expected
    
    def test_parse_root_path(self):
        """Test parsing root path"""
        result = parse_path_segments("/")
        assert result == []
    
    def test_parse_unnormalized_path(self):
        """Test that parsing normalizes paths first"""
        result = parse_path_segments("characters/locations/")
        expected = ["/characters", "/characters/locations"]
        assert result == expected


class TestExtractFolderPath:
    """Test folder path extraction"""
    
    def test_extract_from_nested_document(self):
        """Test extracting folder from nested document path"""
        result = extract_folder_path("/characters/locations/taverns/prancing-pony")
        assert result == "/characters/locations/taverns"
    
    def test_extract_from_single_level_document(self):
        """Test extracting folder from single-level document"""
        result = extract_folder_path("/characters/elara")
        assert result == "/characters"
    
    def test_extract_from_root_document(self):
        """Test extracting from root-level document"""
        result = extract_folder_path("/standalone-doc")
        assert result is None
    
    def test_extract_from_root_path(self):
        """Test extracting from root path"""
        result = extract_folder_path("/")
        assert result is None


class TestValidateDocumentPath:
    """Test document path validation"""
    
    def test_valid_paths(self):
        """Test various valid path formats"""
        valid_paths = [
            "/characters/elara",
            "/characters/locations/taverns/prancing-pony",
            "/standalone-document",
            "/very/deeply/nested/folder/structure/document"
        ]
        
        for path in valid_paths:
            is_valid, error = validate_document_path(path)
            assert is_valid, f"Path '{path}' should be valid, got error: {error}"
            assert error is None
    
    def test_empty_paths(self):
        """Test empty path validation"""
        invalid_paths = ["", "   ", None]
        
        for path in invalid_paths:
            is_valid, error = validate_document_path(path)
            assert not is_valid
            assert "empty" in error.lower()
    
    def test_paths_with_double_dots(self):
        """Test paths with .. segments"""
        is_valid, error = validate_document_path("/characters/../elara")
        assert not is_valid
        assert ".." in error
    
    def test_very_long_path(self):
        """Test path length validation"""
        # Create a path longer than 500 characters
        long_path = "/characters/" + "a" * 500
        is_valid, error = validate_document_path(long_path)
        assert not is_valid
        assert "too long" in error.lower()
    
    def test_long_segment(self):
        """Test individual segment length validation"""
        long_segment = "a" * 101
        path = f"/characters/{long_segment}/document"
        is_valid, error = validate_document_path(path)
        assert not is_valid
        assert "too long" in error.lower()


class TestGetFolderNameFromPath:
    """Test folder name extraction"""
    
    def test_extract_from_nested_path(self):
        """Test extracting name from nested folder path"""
        assert get_folder_name_from_path("/characters/locations/taverns") == "taverns"
    
    def test_extract_from_single_level_path(self):
        """Test extracting name from single-level path"""
        assert get_folder_name_from_path("/characters") == "characters"
    
    def test_extract_from_root_path(self):
        """Test extracting name from root path"""
        assert get_folder_name_from_path("/") == ""


class TestEnsureFolderHierarchyExists:
    """Test automatic folder hierarchy creation"""
    
    @pytest.fixture
    def mock_file_tree_repo(self):
        """Create mock file tree repository"""
        repo = AsyncMock()
        return repo
    
    @pytest.fixture
    def sample_existing_folders(self):
        """Sample existing folder structure"""
        now = datetime.now(UTC).replace(tzinfo=None)
        return [
            FileTreeItem(
                id="folder_characters",
                project_id="proj_123",
                name="Characters",
                path="/characters",
                type="folder",
                parent_id=None,
                tags=[],
                created_at=now,
                updated_at=now
            ),
            FileTreeItem(
                id="folder_locations",
                project_id="proj_123", 
                name="Locations",
                path="/characters/locations",
                type="folder",
                parent_id="folder_characters",
                tags=[],
                created_at=now,
                updated_at=now
            )
        ]
    
    async def test_document_at_root_level(self, mock_file_tree_repo):
        """Test document creation at root level (no folders needed)"""
        mock_file_tree_repo.get_by_project_id.return_value = []
        
        result = await ensure_folder_hierarchy_exists(
            "proj_123", 
            "/standalone-document", 
            mock_file_tree_repo
        )
        
        assert result is None
        mock_file_tree_repo.create.assert_not_called()
    
    async def test_all_folders_exist(self, mock_file_tree_repo, sample_existing_folders):
        """Test when all required folders already exist"""
        mock_file_tree_repo.get_by_project_id.return_value = sample_existing_folders
        
        result = await ensure_folder_hierarchy_exists(
            "proj_123",
            "/characters/locations/document",
            mock_file_tree_repo
        )
        
        assert result == "folder_locations"
        mock_file_tree_repo.create.assert_not_called()
    
    async def test_create_missing_folders(self, mock_file_tree_repo, sample_existing_folders):
        """Test creating missing folders in hierarchy"""
        mock_file_tree_repo.get_by_project_id.return_value = sample_existing_folders
        
        # Mock the create method to return new folders
        now = datetime.now(UTC).replace(tzinfo=None)
        created_folder = FileTreeItem(
            id="folder_taverns",
            project_id="proj_123",
            name="Taverns", 
            path="/characters/locations/taverns",
            type="folder",
            parent_id="folder_locations",
            tags=[],
            created_at=now,
            updated_at=now
        )
        mock_file_tree_repo.create.return_value = created_folder
        
        result = await ensure_folder_hierarchy_exists(
            "proj_123",
            "/characters/locations/taverns/prancing-pony",
            mock_file_tree_repo
        )
        
        assert result == "folder_taverns"
        
        # Verify create was called with correct data
        mock_file_tree_repo.create.assert_called_once()
        create_call_args = mock_file_tree_repo.create.call_args[0][0]
        
        assert create_call_args["project_id"] == "proj_123"
        assert create_call_args["name"] == "taverns"
        assert create_call_args["path"] == "/characters/locations/taverns"
        assert create_call_args["type"] == "folder"
        assert create_call_args["parent_id"] == "folder_locations"
        assert create_call_args["tags"] == []
    
    async def test_create_entire_hierarchy(self, mock_file_tree_repo):
        """Test creating entire folder hierarchy from scratch"""
        mock_file_tree_repo.get_by_project_id.return_value = []
        
        now = datetime.now(UTC).replace(tzinfo=None)
        
        # Mock sequential folder creation
        created_folders = []
        
        def mock_create(folder_data):
            folder_id = f"folder_{len(created_folders)}"
            folder = FileTreeItem(
                id=folder_id,
                project_id=folder_data["project_id"],
                name=folder_data["name"],
                path=folder_data["path"],
                type=folder_data["type"],
                parent_id=folder_data["parent_id"],
                tags=folder_data["tags"],
                created_at=now,
                updated_at=now
            )
            created_folders.append(folder)
            return folder
        
        mock_file_tree_repo.create.side_effect = mock_create
        
        result = await ensure_folder_hierarchy_exists(
            "proj_123",
            "/characters/locations/taverns/prancing-pony",
            mock_file_tree_repo
        )
        
        # Should have created 3 folders and returned ID of deepest one
        assert result == "folder_2"  # Third folder created
        assert mock_file_tree_repo.create.call_count == 3
        
        # Verify the sequence of folder creation
        create_calls = mock_file_tree_repo.create.call_args_list
        
        # First call: /characters
        first_call = create_calls[0][0][0]
        assert first_call["name"] == "characters"
        assert first_call["path"] == "/characters"
        assert first_call["parent_id"] is None
        
        # Second call: /characters/locations  
        second_call = create_calls[1][0][0]
        assert second_call["name"] == "locations"
        assert second_call["path"] == "/characters/locations"
        assert second_call["parent_id"] == "folder_0"  # First created folder
        
        # Third call: /characters/locations/taverns
        third_call = create_calls[2][0][0]
        assert third_call["name"] == "taverns"
        assert third_call["path"] == "/characters/locations/taverns"
        assert third_call["parent_id"] == "folder_1"  # Second created folder