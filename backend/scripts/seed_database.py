#!/usr/bin/env python3
"""
Manual database seeding script for ShuScribe

Usage:
    python scripts/seed_database.py                    # Seed if database is empty
    python scripts/seed_database.py --force            # Seed even if data exists
    python scripts/seed_database.py --clear            # Clear and seed
    python scripts/seed_database.py --size large       # Seed with large dataset
    python scripts/seed_database.py --help             # Show help

This script allows developers to manually seed the database with sample data.
"""
import asyncio
import argparse
import sys
import os
import logging

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import settings
from src.database.connection import init_database, create_tables, close_database
from src.database.factory import init_repositories
from src.database.seeder import seed_development_database, is_database_empty


def setup_logging():
    """Setup logging for the seeding script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


async def main():
    """Main seeding function"""
    parser = argparse.ArgumentParser(description='Seed ShuScribe database with sample data')
    parser.add_argument('--force', action='store_true', 
                       help='Force seeding even if database is not empty')
    parser.add_argument('--clear', action='store_true',
                       help='Clear existing data before seeding')
    parser.add_argument('--size', choices=['small', 'medium', 'large'], 
                       default='medium', help='Size of dataset to generate')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check if database is empty, do not seed')
    
    args = parser.parse_args()
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check environment
    if settings.ENVIRONMENT.lower() not in ["development", "testing"]:
        logger.error("Seeding is only allowed in development/testing environments")
        logger.error(f"Current environment: {settings.ENVIRONMENT}")
        sys.exit(1)
    
    try:
        # Initialize database
        logger.info("Initializing database connection...")
        init_database()
        
        if settings.DATABASE_BACKEND != "memory":
            # Only drop tables if explicitly clearing
            await create_tables(drop_existing=args.clear)
            logger.info("Database tables created/verified")
        
        # Initialize repositories
        init_repositories(backend=settings.DATABASE_BACKEND)
        logger.info(f"Repositories initialized with {settings.DATABASE_BACKEND} backend")
        
        # Check if database is empty
        is_empty = await is_database_empty()
        logger.info(f"Database empty: {is_empty}")
        
        if args.check_only:
            print(f"Database is {'empty' if is_empty else 'not empty'}")
            return
        
        # Override settings if specified
        if args.size:
            settings.SEED_DATA_SIZE = args.size
        if args.clear:
            settings.CLEAR_BEFORE_SEED = True
        
        # Determine if we should seed
        should_seed = args.force or is_empty
        
        if not should_seed:
            logger.info("Database is not empty. Use --force to seed anyway.")
            print("Database is not empty. Use --force to seed anyway.")
            return
        
        # Perform seeding
        logger.info(f"Starting database seeding with size: {settings.SEED_DATA_SIZE}")
        results = await seed_development_database(force=args.force)
        
        if "error" in results:
            logger.error(f"Seeding failed: {results['error']}")
            sys.exit(1)
        
        if results.get("skipped"):
            logger.info(f"Seeding skipped: {results['reason']}")
            print(f"Seeding skipped: {results['reason']}")
        else:
            logger.info("Seeding completed successfully!")
            print("\nSeeding Results:")
            print(f"  Projects created: {results.get('projects_created', 0)}")
            print(f"  Documents created: {results.get('documents_created', 0)}")
            print(f"  File tree items created: {results.get('file_tree_items_created', 0)}")
            
            if results.get('errors'):
                print(f"  Errors encountered: {len(results['errors'])}")
                for error in results['errors']:
                    print(f"    - {error}")
            
            print("\nDatabase seeding completed successfully!")
    
    except Exception as e:
        logger.error(f"Seeding script failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    
    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())