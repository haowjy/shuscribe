"""
Root conftest.py for ShuScribe backend tests

Shared fixtures and utilities for all test modules.
"""

import asyncio
import pytest
import shutil
from pathlib import Path
from typing import Iterator, AsyncIterator
from uuid import uuid4

# Async test support
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """Create a temporary directory in backend/temp that's cleaned up after test."""
    backend_root = Path(__file__).parent.parent
    temp_root = backend_root / "temp"
    temp_root.mkdir(exist_ok=True)
    
    # Create unique temp directory
    temp_name = f"test_temp_{uuid4().hex[:8]}"
    temp_path = temp_root / temp_name
    temp_path.mkdir()
    
    yield temp_path
    
    # Cleanup after test
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def temp_workspace_path() -> Iterator[Path]:
    """Create a temporary workspace path in temp/ directory."""
    backend_root = Path(__file__).parent.parent
    temp_root = backend_root / "temp"
    temp_root.mkdir(exist_ok=True)
    
    # Create unique workspace path
    workspace_name = f"test_workspace_{uuid4().hex[:8]}"
    workspace_path = temp_root / workspace_name
    
    yield workspace_path
    
    # Cleanup after test
    if workspace_path.exists():
        shutil.rmtree(workspace_path)


@pytest.fixture(scope="session", autouse=True)
def cleanup_temp_workspaces():
    """Clean up any leftover temp workspaces and directories at start and end of test session."""
    backend_root = Path(__file__).parent.parent
    temp_root = backend_root / "temp"
    
    def cleanup():
        if temp_root.exists():
            for item in temp_root.iterdir():
                if item.is_dir() and (item.name.startswith("test_workspace_") or item.name.startswith("test_temp_")):
                    try:
                        shutil.rmtree(item)
                    except:
                        pass  # Ignore cleanup errors
    
    # Clean up at start of session
    cleanup()
    
    yield
    
    # Clean up at end of session
    cleanup()


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "medium: marks tests as medium speed")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
