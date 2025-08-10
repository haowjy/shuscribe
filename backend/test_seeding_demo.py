#!/usr/bin/env python3
"""
Seeding Demonstration Script

This script demonstrates how the ShuScribe seeding system works by:
1. Setting up an in-memory repository backend
2. Running the seeding process 
3. Querying and displaying the generated data

Run with: uv run python test_seeding_demo.py
"""
import asyncio
import logging
import sys
import os
from typing import Dict, Any

# Add the current directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(__file__))

from src.config import settings, Environment
from src.database.factory import init_repositories, get_repositories
from src.database.seeder import DatabaseSeeder


def setup_logging():
    """Setup logging for the demo script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_subsection(title: str):
    """Print a subsection header"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")


async def main():
    """Main demonstration function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print_section("ShuScribe Seeding Demonstration")
    print("This script demonstrates the seeding system using in-memory storage.")
    
    try:
        # Step 1: Configure for memory backend
        print_subsection("Step 1: Configuring Memory Backend")
        
        # Override settings for this demo
        original_backend = settings.DATABASE_BACKEND
        original_env = settings.ENVIRONMENT
        settings.DATABASE_BACKEND = "memory"
        settings.ENVIRONMENT = Environment.DEV
        
        print(f"Backend: {settings.DATABASE_BACKEND}")
        print(f"Environment: {settings.ENVIRONMENT}")
        
        # Step 2: Initialize repositories
        print_subsection("Step 2: Initializing Repositories")
        init_repositories(backend="memory")
        repositories = get_repositories()
        
        print("✓ Memory repositories initialized")
        print(f"  - Project Repository: {type(repositories.project).__name__}")
        print(f"  - Document Repository: {type(repositories.document).__name__}")
        print(f"  - File Tree Repository: {type(repositories.file_tree).__name__}")
        print(f"  - Tag Repository: {type(repositories.tag).__name__}")
        print(f"  - User Repository: {type(repositories.user).__name__}")
        
        # Step 3: Run seeding
        print_subsection("Step 3: Running Seeding Process")
        seeder = DatabaseSeeder(repositories)
        
        print("Starting seeding with 'medium' dataset...")
        results = await seeder.seed_database(clear_first=True, data_size="medium")
        
        if "error" in results:
            print(f"❌ Seeding failed: {results['error']}")
            return
        
        print("✓ Seeding completed successfully!")
        print(f"  📊 Tags created: {results['tags_created']}")
        print(f"  📁 Projects created: {results['projects_created']}")
        print(f"  📄 Documents created: {results['documents_created']}")
        print(f"  🌳 File tree items created: {results['file_tree_items_created']}")
        
        if results.get('errors'):
            print(f"  ⚠️  Errors: {len(results['errors'])}")
            for error in results['errors']:
                print(f"    - {error}")
        
        # Step 4: Query and display the data
        print_subsection("Step 4: Querying Generated Data")
        
        # Get all tags
        all_tags = await repositories.tag.get_global_tags()
        print(f"\n🏷️  Global Tags ({len(all_tags)} total):")
        for tag in all_tags[:10]:  # Show first 10
            print(f"  • {tag.name} ({tag.category}) - {tag.color}")
        if len(all_tags) > 10:
            print(f"  ... and {len(all_tags) - 10} more")
        
        # Get all projects
        all_projects = await repositories.project.list_all()
        print(f"\n📁 Projects ({len(all_projects)} total):")
        
        for project in all_projects:
            print(f"\n  📖 {project.title}")
            print(f"     Description: {project.description[:100]}...")
            print(f"     Word Count: {project.word_count:,}")
            print(f"     Document Count: {project.document_count}")
            print(f"     Tags: {', '.join(project.tags[:5])}")
            if len(project.tags) > 5:
                print(f"           ... and {len(project.tags) - 5} more")
            
            # Get file tree for this project
            file_tree = await repositories.file_tree.get_by_project_id(project.id)
            print(f"     File Tree Items: {len(file_tree)}")
            
            # Show folder structure
            folders = [item for item in file_tree if item.type == "folder"]
            files = [item for item in file_tree if item.type == "file"]
            
            print(f"       📁 Folders ({len(folders)}):")
            for folder in folders:
                folder_files = [f for f in files if f.parent_id == folder.id]
                print(f"         • {folder.name}/ ({len(folder_files)} files)")
                
                # Show first few files in each folder
                for file in folder_files[:3]:
                    print(f"           - {file.name}")
                if len(folder_files) > 3:
                    print(f"           ... and {len(folder_files) - 3} more")
        
        # Step 5: Demonstrate querying specific data
        print_subsection("Step 5: Advanced Queries")
        
        if all_projects:
            # Get documents for first project
            first_project = all_projects[0]
            
            # Since we don't have get_by_project_id for documents yet, 
            # we'll simulate by showing the document structure
            print(f"\n📄 Sample Project Structure: {first_project.title}")
            
            project_files = await repositories.file_tree.get_by_project_id(first_project.id)
            document_files = [item for item in project_files if item.type == "file" and item.document_id]
            
            print(f"  Documents ({len(document_files)} total):")
            for doc_file in document_files[:5]:  # Show first 5
                if doc_file.document_id:
                    # Get the actual document
                    document = await repositories.document.get_by_id(doc_file.document_id)
                    if document:
                        content_preview = ""
                        if document.content and "content" in document.content:
                            # Extract text from ProseMirror content for preview
                            for block in document.content["content"][:2]:  # First 2 blocks
                                if block.get("type") == "paragraph" and "content" in block:
                                    for text_node in block["content"]:
                                        if text_node.get("type") == "text":
                                            content_preview += text_node.get("text", "")[:50]
                                            break
                                    break
                        
                        print(f"    📄 {document.title}")
                        print(f"       Path: {document.path}")
                        print(f"       Word Count: {document.word_count}")
                        print(f"       Tags: {', '.join(document.tags)}")
                        if content_preview:
                            print(f"       Preview: {content_preview}...")
            
            if len(document_files) > 5:
                print(f"    ... and {len(document_files) - 5} more documents")
        
        print_subsection("Demo Complete!")
        print("✓ Successfully demonstrated seeding with in-memory storage")
        print("✓ Generated realistic test data with proper relationships")
        print("✓ Showed how to query the seeded data")
        print("\nThe in-memory storage will be cleared when this script exits.")
        
        # Restore original settings
        settings.DATABASE_BACKEND = original_backend
        settings.ENVIRONMENT = original_env
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())