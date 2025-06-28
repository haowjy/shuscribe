# backend/src/utils/story_loader.py
"""
DEPRECATED: Story loading utilities

This module has been moved to src.core.story_workspace for better workspace management.
This file provides backward compatibility imports and migration guidance.

NEW USAGE:
- Use src.core.story_workspace.StoryWorkspace for complete workspace management
- Use src.core.story_loading.StoryLoaderFactory for simple story loading

OLD vs NEW:
# OLD (deprecated)
loader = StoryLoader(story_folder)
input_story = loader.load_story()
print(input_story.full_content)  # Loads all chapters at once

# NEW (recommended) 
workspace = StoryWorkspace.create_workspace(story_folder, owner_id)
# Lazy loading with chunking
content = workspace.get_chapter_content_chunked(start=1, count=5)  # Only 5 chapters
# Progressive loading
chapters = await workspace.load_chapters_range(start=1, count=10)
"""
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import uuid4

# Import from new location for backward compatibility
from src.core.story_loading import (
    StoryLoaderFactory,
    StoryLoadingError
)

# Import new workspace system
from src.core.story_workspace import StoryWorkspace

warnings.warn(
    "src.utils.story_loader is deprecated. Please use src.core.story_workspace.StoryWorkspace for complete workspace management or src.core.story_loading.StoryLoaderFactory for simple loading.",
    DeprecationWarning,
    stacklevel=2
)

class StoryLoader:
    """
    DEPRECATED: Legacy StoryLoader class
    
    This is a compatibility wrapper. For new code, use:
    - StoryWorkspace for complete workspace management 
    - StoryLoaderFactory for simple story loading
    
    Migration guide:
    # OLD
    loader = StoryLoader(story_folder)
    story = loader.load_story()
    
    # NEW - Simple loading
    story = StoryLoaderFactory.load_story(story_folder)
    
    # NEW - Full workspace management  
    workspace = StoryWorkspace.create_workspace(story_folder, owner_id)
    """
    
    def __init__(self, story_folder: Path):
        warnings.warn(
            "StoryLoader is deprecated. Use StoryWorkspace for full workspace management or StoryLoaderFactory for simple loading.",
            DeprecationWarning,
            stacklevel=2
        )
        self.story_folder = Path(story_folder)
        self._loader = StoryLoaderFactory.create_loader(self.story_folder)

    def load_story(self):
        """Load the story using the new system"""
        warnings.warn(
            "load_story() is deprecated. Use StoryLoaderFactory.load_story() or create a StoryWorkspace instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self._loader.load_story()

    def create_workspace(self, owner_id=None):
        """
        Create a new StoryWorkspace for this story
        
        Args:
            owner_id: UUID of the workspace owner (generates one if None)
            
        Returns:
            StoryWorkspace instance
        """
        if owner_id is None:
            owner_id = uuid4()
            
        return StoryWorkspace.create_workspace(self.story_folder, owner_id)

    def get_workspace_info(self):
        """Get information about workspace structure"""
        workspace_root = self.story_folder
        return {
            "story_directory": str(workspace_root),
            "wiki_directory": str(workspace_root / "wikipage"),
            "writing_directory": str(workspace_root / "writing"),
            "validation": StoryWorkspace.create_workspace(workspace_root, uuid4()).validate_workspace()
        }

# Re-export for compatibility
__all__ = [
    'StoryLoader',
    'StoryLoaderFactory',
    'StoryLoadingError',
    'StoryWorkspace'  # New addition
]
