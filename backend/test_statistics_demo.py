#!/usr/bin/env python3
"""
Project Statistics Demonstration Script

This script demonstrates the project statistics calculation system by:
1. Setting up an in-memory repository backend
2. Running the seeding process
3. Testing the statistics recalculation functionality
4. Showing before/after word counts

Run with: uv run python test_statistics_demo.py
"""
import asyncio
import logging
import sys
import os

# Add the current directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(__file__))

from src.config import settings, Environment
from src.database.factory import init_repositories, get_repositories
from src.database.seeder import DatabaseSeeder
from src.database.utils import ProjectStatisticsService


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
    
    print_section("Project Statistics Demonstration")
    print("This script demonstrates the statistics calculation system.")
    
    try:
        # Step 1: Configure for memory backend
        print_subsection("Step 1: Setup and Seeding")
        
        # Override settings for this demo
        settings.DATABASE_BACKEND = "memory"
        settings.ENVIRONMENT = Environment.DEV
        
        # Initialize repositories and seed data
        init_repositories(backend="memory")
        repositories = get_repositories()
        
        seeder = DatabaseSeeder(repositories)
        results = await seeder.seed_database(clear_first=True, data_size="small")
        
        print(f"✓ Seeded: {results['projects_created']} projects, {results['documents_created']} documents")
        
        # Step 2: Show initial statistics
        print_subsection("Step 2: Initial Project Statistics")
        
        all_projects = await repositories.project.list_all()
        
        for project in all_projects:
            print(f"📁 {project.title}")
            print(f"   Word Count: {project.word_count:,}")
            print(f"   Document Count: {project.document_count}")
            
            # Show actual document details
            documents = await repositories.document.get_by_project_id(project.id)
            actual_doc_count = len(documents)
            actual_word_count = sum(doc.word_count for doc in documents)
            
            print(f"   Actual Documents: {actual_doc_count}")
            print(f"   Actual Word Count: {actual_word_count:,}")
            
            if project.word_count != actual_word_count or project.document_count != actual_doc_count:
                print("   ⚠️  Statistics are out of sync!")
            else:
                print("   ✓ Statistics are accurate")
        
        # Step 3: Test manual statistics modification
        print_subsection("Step 3: Testing Statistics Recalculation")
        
        if all_projects:
            test_project = all_projects[0]
            print(f"Testing with project: {test_project.title}")
            
            # Manually corrupt the statistics
            print("\n1. Manually corrupting statistics...")
            corrupted_project = await repositories.project.update(test_project.id, {
                "word_count": 99999,
                "document_count": 999
            })
            
            print(f"   Corrupted Word Count: {corrupted_project.word_count:,}")
            print(f"   Corrupted Document Count: {corrupted_project.document_count}")
            
            # Use statistics service to recalculate
            print("\n2. Recalculating statistics using ProjectStatisticsService...")
            
            stats_service = ProjectStatisticsService(repositories)
            fixed_project = await stats_service.recalculate_project_statistics(test_project.id)
            
            print(f"   Fixed Word Count: {fixed_project.word_count:,}")
            print(f"   Fixed Document Count: {fixed_project.document_count}")
            
            # Verify accuracy
            documents = await repositories.document.get_by_project_id(test_project.id)
            expected_docs = len(documents)
            expected_words = sum(doc.word_count for doc in documents)
            
            if (fixed_project.word_count == expected_words and 
                fixed_project.document_count == expected_docs):
                print("   ✅ Statistics successfully recalculated!")
            else:
                print("   ❌ Statistics recalculation failed!")
        
        # Step 4: Test bulk refresh
        print_subsection("Step 4: Bulk Statistics Refresh")
        
        # First corrupt all projects
        print("Corrupting all project statistics...")
        for project in all_projects:
            await repositories.project.update(project.id, {
                "word_count": 0,
                "document_count": 0
            })
        
        # Refresh all statistics
        print("Refreshing all project statistics...")
        stats_service = ProjectStatisticsService(repositories)
        refresh_results = await stats_service.refresh_all_project_statistics()
        
        print(f"✓ Updated {refresh_results['updated']}/{refresh_results['total']} projects")
        if refresh_results['errors']:
            print(f"❌ {len(refresh_results['errors'])} errors occurred")
            for error in refresh_results['errors']:
                print(f"   - {error}")
        
        # Verify final state
        print_subsection("Step 5: Final Verification")
        
        all_projects = await repositories.project.list_all()
        
        all_accurate = True
        for project in all_projects:
            documents = await repositories.document.get_by_project_id(project.id)
            expected_docs = len(documents)
            expected_words = sum(doc.word_count for doc in documents)
            
            accurate = (project.word_count == expected_words and 
                       project.document_count == expected_docs)
            
            print(f"📁 {project.title}")
            print(f"   Word Count: {project.word_count:,} {'✓' if project.word_count == expected_words else '❌'}")
            print(f"   Document Count: {project.document_count} {'✓' if project.document_count == expected_docs else '❌'}")
            
            if not accurate:
                all_accurate = False
        
        print_subsection("Demo Complete!")
        if all_accurate:
            print("✅ All project statistics are now accurate!")
        else:
            print("❌ Some statistics are still incorrect")
        
        print("✓ Successfully demonstrated statistics calculation system")
        print("✓ Showed manual recalculation for individual projects")
        print("✓ Showed bulk refresh for all projects")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())