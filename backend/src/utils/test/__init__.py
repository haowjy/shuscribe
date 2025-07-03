"""Test utilities for ShuScribe"""

from src.utils.test.import_story import (
    NotebookStoryLoader,
    StoryLoadResult,
    # Dependency-injected functions
    load_story_with_repositories,
    load_pokemon_amber_with_repositories,
    create_test_story_with_repositories,
    # Legacy convenience functions
    load_pokemon_amber_story,
    load_test_story,
    load_story_from_xml
)

__all__ = [
    "NotebookStoryLoader",
    "StoryLoadResult",
    # Dependency-injected functions
    "load_story_with_repositories",
    "load_pokemon_amber_with_repositories", 
    "create_test_story_with_repositories",
    # Legacy convenience functions
    "load_pokemon_amber_story",
    "load_test_story",
    "load_story_from_xml"
]