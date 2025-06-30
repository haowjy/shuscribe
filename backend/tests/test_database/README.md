# ShuScribe Database Test Suite

Comprehensive test suite for the ShuScribe database layer, covering all repository implementations, file storage operations, and integration scenarios.

## 🏗️ Test Architecture

### Test Structure
```
tests/test_database/
├── conftest.py                    # Database-specific fixtures
├── test_user_repository.py        # User & API key management tests
├── test_story_repository.py       # Chapter & story metadata tests
├── test_wiki_repository.py        # Wiki & spoiler prevention tests
├── test_workspace_repository.py   # Workspace management tests
├── test_runner.py                 # Test runner utility
└── README.md                      # This file
```

### Fixture Hierarchy
- **Root conftest.py**: Shared utilities, temp workspace management
- **Database conftest.py**: Repository fixtures, sample data, factory patterns
- **Individual tests**: Specific test scenarios and edge cases

## 🧪 Test Categories

### Unit Tests (Default)
Basic repository operations, CRUD functionality, validation, and error handling.

**Coverage:**
- ✅ User CRUD operations
- ✅ BYOK API key management & encryption  
- ✅ Chapter creation, updating, publishing
- ✅ Story metadata and statistics
- ✅ Wiki article management
- ✅ Workspace operations and settings
- ✅ Edge cases and error conditions

### Integration Tests (`@pytest.mark.integration`)
Real-world scenarios using the import scripts and complete workflows.

**Coverage:**
- ✅ Pokemon Amber story import and validation
- ✅ Complete spoiler prevention workflows
- ✅ Cross-repository operations
- ✅ File system integration
- ✅ End-to-end story publishing

### Performance Tests (`@pytest.mark.slow` / `@pytest.mark.performance`)
Performance validation for large datasets and concurrent operations.

**Coverage:**
- ✅ Many chapters (50+ chapters)
- ✅ Large content (100k+ words)  
- ✅ Multiple API keys (50+ keys)
- ✅ Many wiki versions (50+ versions)
- ✅ Multiple workspaces (25+ workspaces)

## 🚀 Running Tests

### Quick Start
```bash
# Run basic tests (excluding slow/integration)
python tests/test_database/test_runner.py quick

# Run all tests
python tests/test_database/test_runner.py all

# Run specific repository tests
python tests/test_database/test_runner.py user
python tests/test_database/test_runner.py story
python tests/test_database/test_runner.py wiki
python tests/test_database/test_runner.py workspace
```

### Test Suites
```bash
# Unit tests only (fast)
python tests/test_database/test_runner.py unit

# Integration tests only
python tests/test_database/test_runner.py integration

# Performance tests only
python tests/test_database/test_runner.py performance
```

### Advanced Options
```bash
# With coverage report
python tests/test_database/test_runner.py all --coverage

# Verbose output with fail-fast
python tests/test_database/test_runner.py quick -v -x

# Skip slow tests
python tests/test_database/test_runner.py all --no-slow

# Skip integration tests
python tests/test_database/test_runner.py all --no-integration

# Parallel execution (requires pytest-xdist)
python tests/test_database/test_runner.py unit -n 4
```

### Direct pytest Usage
```bash
# Run specific test
pytest tests/test_database/test_user_repository.py::TestAPIKeyManagement::test_store_api_key -v

# Run with markers
pytest tests/test_database/ -m "not slow and not integration" -v

# Run with coverage
pytest tests/test_database/ --cov=src/database --cov-report=html
```

## 📊 Test Data

### Fixtures Available
- `temp_workspace_path`: Clean temporary workspace for each test
- `file_repos`: File-based repository instances
- `current_user`: Auto-created user for testing
- `sample_workspace`: Pre-created workspace with metadata
- `sample_chapters`: 3 published chapters (1-3)
- `sample_wiki_articles`: Character and location articles
- `sample_api_keys`: OpenAI, Anthropic, and Google API keys
- `wiki_with_versions`: Article with 3 chapter versions for spoiler testing
- `pokemon_amber_workspace`: Real story data (17 chapters, ~47k words)
- `workspace_factory`: Factory for creating custom test workspaces

### Test Data Patterns
```python
async def test_example(workspace_factory):
    # Create workspace with specific content
    workspace_path, repos, workspace_id = await workspace_factory(
        name="Test Workspace",
        chapter_count=5,    # Create 5 chapters
        wiki_count=3,       # Create 3 wiki articles  
        with_api_keys=True  # Add sample API keys
    )
    
    # Use repositories
    chapters = await repos.story.get_chapters_by_workspace(workspace_id)
    assert len(chapters) == 5
```

## 🔍 Key Test Scenarios

### User Repository Tests
- **Basic Operations**: User CRUD, email lookup, current user management
- **API Key Management**: Store, retrieve, update, delete BYOK keys
- **Encryption**: Verify keys are encrypted at rest, decrypted on retrieval
- **Edge Cases**: Invalid users, empty keys, special characters, large metadata

### Story Repository Tests
- **Chapter Management**: Create, update, delete chapters with proper ordering
- **Publication Workflow**: Draft → Published → Archived transitions
- **Word Count**: Accurate calculation for various content types
- **Statistics**: Story metadata updates based on chapter changes
- **Performance**: Handle 50+ chapters and 100k+ word content

### Wiki Repository Tests  
- **Article Operations**: CRUD operations for different article types
- **Spoiler Prevention**: Chapter-based versioning to prevent spoilers
- **Version Management**: Progressive content revelation through story
- **Connections**: Article-to-article relationships and dependencies
- **Current Versions**: Working versions separate from published versions

### Workspace Repository Tests
- **Workspace Management**: Create, update, delete workspaces with metadata
- **Ownership**: Multiple workspaces per user, access control
- **Settings**: Custom configurations, large settings objects
- **File Structure**: Proper directory creation and config files
- **Integration**: Workspaces with story content, wiki articles, API keys

## 🛠️ Writing New Tests

### Test Class Structure
```python
class TestFeatureName:
    """Test description of the feature."""
    
    async def test_basic_operation(self, fixture_name):
        """Test basic functionality."""
        # Arrange
        data = SomeCreate(field="value")
        
        # Act  
        result = await repo.method(data)
        
        # Assert
        assert result.field == "value"
        assert result.id is not None
    
    async def test_edge_case(self, fixture_name):
        """Test edge case or error condition."""
        # Test what happens with invalid input
        pass
```

### Naming Conventions
- **Test files**: `test_{repository_name}_repository.py`
- **Test classes**: `Test{FeatureName}` (PascalCase)
- **Test methods**: `test_{what_is_being_tested}` (snake_case)
- **Fixtures**: Descriptive names like `sample_workspace`, `wiki_with_versions`

### Test Markers
```python
@pytest.mark.slow          # Long-running tests
@pytest.mark.integration   # Tests using real data/imports
@pytest.mark.performance   # Performance benchmarks
```

## 🔧 Configuration

### pytest.ini Settings
The test suite uses these key configurations from the root `pyproject.toml`:
- Async support via `pytest-asyncio`
- Coverage tracking for `src/database`
- Custom markers for test categorization
- Temporary workspace cleanup

### Environment Setup
Tests automatically:
- Create temporary workspaces in `temp/` directory
- Clean up test data after each test
- Handle file permissions (600 for config files)
- Manage encryption keys for API key testing

## 🚨 Common Issues

### Test Failures
1. **Import Errors**: Ensure `src/` is in Python path (handled by conftest.py)
2. **Permission Errors**: Tests create files with secure permissions
3. **Cleanup Issues**: Use fixtures for automatic cleanup
4. **Async Issues**: All test methods should be `async def`

### Performance Considerations
- Performance tests are marked `@pytest.mark.slow`
- Integration tests may download/use real data
- Use `--no-slow` to skip time-intensive tests during development
- Temp workspace cleanup happens automatically

### Coverage Expectations
- Aim for >90% coverage on repository implementations
- Focus on edge cases and error conditions
- Integration tests validate real-world usage patterns
- Performance tests ensure scalability

## 📈 Metrics

### Current Test Coverage
- **User Repository**: Full CRUD, API keys, encryption, edge cases
- **Story Repository**: Chapters, metadata, publishing, statistics  
- **Wiki Repository**: Articles, versioning, spoiler prevention, connections
- **Workspace Repository**: Management, settings, ownership, file structure

### Test Performance
- **Quick Suite**: ~30 seconds (basic functionality)
- **Full Suite**: ~2-3 minutes (including integration)
- **Performance Suite**: ~1-2 minutes (load testing)

### Test Counts (Approximate)
- **Total Tests**: 100+ test methods
- **Unit Tests**: ~70 tests
- **Integration Tests**: ~15 tests  
- **Performance Tests**: ~15 tests 