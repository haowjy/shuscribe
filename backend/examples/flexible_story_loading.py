#!/usr/bin/env python3
"""
Example: Flexible Story Loading with Dependency Injection

This example demonstrates how to use the new story loader with:
1. Any repository implementation (memory, file, database)
2. Any story directory that follows the _meta.xml format
3. Full dependency injection for maximum flexibility
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils.test.import_story import (
    load_story_with_repositories,
    load_pokemon_amber_with_repositories,
    create_test_story_with_repositories
)
from src.api.dependencies import (
    get_story_repository_dependency,
    get_workspace_repository_dependency,
    get_user_repository_dependency
)


async def example_1_load_pokemon_amber():
    """Example 1: Load Pokemon Amber with dependency injection"""
    print("🎯 Example 1: Loading Pokemon Amber with dependency injection")
    print("=" * 60)
    
    # Get repositories using dependency injection
    story_repo = get_story_repository_dependency()
    workspace_repo = get_workspace_repository_dependency()
    user_repo = get_user_repository_dependency()
    
    print(f"📁 Using repositories:")
    print(f"   📖 Story: {type(story_repo).__name__}")
    print(f"   📁 Workspace: {type(workspace_repo).__name__}")
    print(f"   👤 User: {type(user_repo).__name__}")
    
    try:
        # Load Pokemon Amber with injected repositories
        result = await load_pokemon_amber_with_repositories(
            story_repository=story_repo,
            workspace_repository=workspace_repo,
            user_repository=user_repo
        )
        
        print("\n✅ Successfully loaded Pokemon Amber!")
        print(result.summary())
        
        return result
        
    except FileNotFoundError as e:
        print(f"❌ Pokemon Amber not found: {e}")
        return None


async def example_2_load_custom_story():
    """Example 2: Load any story directory with _meta.xml format"""
    print("\n🎯 Example 2: Loading custom story directory")
    print("=" * 60)
    
    # Get repositories
    story_repo = get_story_repository_dependency()
    workspace_repo = get_workspace_repository_dependency()
    user_repo = get_user_repository_dependency()
    
    # Example: Load from a custom story directory
    # Replace this path with your own story directory
    custom_story_path = Path("../tests/resources/pokemon_amber/story")
    
    if custom_story_path.exists():
        print(f"📁 Loading story from: {custom_story_path}")
        
        result = await load_story_with_repositories(
            story_directory=custom_story_path,
            story_repository=story_repo,
            workspace_repository=workspace_repo,
            user_repository=user_repo,
            workspace_name="Custom Pokemon Workspace",
            user_email="custom@example.com",
            user_display_name="Custom User"
        )
        
        print("\n✅ Successfully loaded custom story!")
        print(result.summary())
        
        return result
    else:
        print(f"⚠️  Custom story directory not found: {custom_story_path}")
        return None


async def example_3_create_test_story():
    """Example 3: Create minimal test story"""
    print("\n🎯 Example 3: Creating minimal test story")
    print("=" * 60)
    
    # Get repositories
    story_repo = get_story_repository_dependency()
    workspace_repo = get_workspace_repository_dependency()
    user_repo = get_user_repository_dependency()
    
    # Create test story with custom parameters
    result = await create_test_story_with_repositories(
        story_repository=story_repo,
        workspace_repository=workspace_repo,
        user_repository=user_repo,
        workspace_name="Example Test Workspace",
        user_email="example@test.com",
        user_display_name="Example Test User"
    )
    
    print("\n✅ Successfully created test story!")
    print(result.summary())
    
    return result


async def example_4_use_with_different_repositories():
    """Example 4: Use with different repository implementations"""
    print("\n🎯 Example 4: Using with different repository implementations")
    print("=" * 60)
    
    # Example: Use memory repositories directly
    from src.database.factory import get_repositories
    
    # Memory repositories
    memory_repos = get_repositories(backend="memory")
    print("📁 Using memory repositories:")
    print(f"   📖 Story: {type(memory_repos.story).__name__}")
    print(f"   📁 Workspace: {type(memory_repos.workspace).__name__}")
    print(f"   👤 User: {type(memory_repos.user).__name__}")
    
    # Create test story with memory repositories
    result = await create_test_story_with_repositories(
        story_repository=memory_repos.story,
        workspace_repository=memory_repos.workspace,
        user_repository=memory_repos.user,
        workspace_name="Memory Test Workspace"
    )
    
    print("\n✅ Successfully created story with memory repositories!")
    print(result.summary())
    
    return result


async def main():
    """Run all examples"""
    print("🚀 Flexible Story Loading Examples")
    print("=" * 80)
    print("This demonstrates the new story loader with full dependency injection.")
    print("You can use any repository implementation and any story directory format.\n")
    
    # Run examples
    results = []
    
    # Example 1: Load Pokemon Amber
    result1 = await example_1_load_pokemon_amber()
    if result1:
        results.append(("Pokemon Amber", result1))
    
    # Example 2: Load custom story
    result2 = await example_2_load_custom_story()
    if result2:
        results.append(("Custom Story", result2))
    
    # Example 3: Create test story
    result3 = await example_3_create_test_story()
    if result3:
        results.append(("Test Story", result3))
    
    # Example 4: Different repositories
    result4 = await example_4_use_with_different_repositories()
    if result4:
        results.append(("Memory Story", result4))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Summary of loaded stories:")
    for name, result in results:
        print(f"   📖 {name}: {result.story.title} ({result.chapters_count} chapters)")
    
    print(f"\n🎯 Key Benefits:")
    print(f"   ✅ Works with any IStoryRepository implementation")
    print(f"   ✅ Works with any story directory following _meta.xml format")
    print(f"   ✅ Full dependency injection for maximum flexibility")
    print(f"   ✅ Clean separation of concerns")
    print(f"   ✅ Easy to test and mock")


if __name__ == "__main__":
    asyncio.run(main()) 