#!/usr/bin/env python3
"""
Migration script to add user ownership to existing projects
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config import settings
from src.database.connection import get_session_context
from src.database.models import Project
from sqlalchemy import text, update, select

logger = logging.getLogger(__name__)

# Default user ID for existing projects (can be overridden)
DEFAULT_USER_ID = "migration_default_user"

async def migrate_user_ownership(default_user_id: str = DEFAULT_USER_ID):
    """
    Migrate existing projects to have user ownership fields
    
    Args:
        default_user_id: User ID to assign to projects that don't have one
    """
    if settings.ENVIRONMENT == "prod":
        logger.error("This migration should not be run in production without careful consideration")
        return False
    
    logger.info(f"Starting user ownership migration with default user: {default_user_id}")
    
    try:
        async with get_session_context() as session:
            # Check if user_id and created_by columns exist
            try:
                # Test query to see if columns exist
                result = await session.execute(
                    text(f"SELECT user_id, created_by FROM {settings.table_prefix}projects LIMIT 1")
                )
                logger.info("user_id and created_by columns already exist")
            except Exception as e:
                logger.error(f"Columns don't exist or there's an issue: {e}")
                logger.info("Please run database schema updates first")
                return False
            
            # Find projects without user_id
            result = await session.execute(
                select(Project).where(Project.user_id.is_(None))
            )
            projects_to_update = result.scalars().all()
            
            if not projects_to_update:
                logger.info("No projects found that need user ownership migration")
                return True
            
            logger.info(f"Found {len(projects_to_update)} projects to update")
            
            # Update projects to have user ownership
            for project in projects_to_update:
                logger.info(f"Updating project: {project.title} (ID: {project.id})")
                
                # Update the project with user ownership
                await session.execute(
                    update(Project)
                    .where(Project.id == project.id)
                    .values(
                        user_id=default_user_id,
                        created_by=default_user_id
                    )
                )
            
            await session.commit()
            logger.info(f"Successfully migrated {len(projects_to_update)} projects")
            return True
            
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return False

async def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate existing projects to have user ownership")
    parser.add_argument(
        "--user-id", 
        default=DEFAULT_USER_ID,
        help=f"User ID to assign to existing projects (default: {DEFAULT_USER_ID})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without making changes"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Table prefix: {settings.table_prefix}")
    
    if args.dry_run:
        logger.info("DRY RUN - No changes will be made")
        
        try:
            async with get_session_context() as session:
                result = await session.execute(
                    select(Project).where(Project.user_id.is_(None))
                )
                projects_to_update = result.scalars().all()
                
                if not projects_to_update:
                    logger.info("No projects found that need user ownership migration")
                else:
                    logger.info(f"Would migrate {len(projects_to_update)} projects:")
                    for project in projects_to_update:
                        logger.info(f"  - {project.title} (ID: {project.id})")
                        
        except Exception as e:
            logger.error(f"Error during dry run: {e}")
            return 1
            
        return 0
    
    success = await migrate_user_ownership(args.user_id)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))