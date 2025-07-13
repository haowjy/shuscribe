# backend/src/database/seeder.py
"""
Database seeding service for development environment
"""
import logging
import random
from typing import Dict, Any, List

from src.config import settings
from src.database.factory import get_repositories, RepositoryContainer
from src.database.connection import get_session_context
from src.database.models import Base
from src.database.seed import MockDataFactory, ProjectTemplates

logger = logging.getLogger(__name__)


class DatabaseSeeder:
    """Service for seeding the database with mock data in development"""
    
    def __init__(self, repositories: RepositoryContainer):
        self.repositories = repositories
        self.factory = MockDataFactory()
    
    async def seed_database(self, clear_first: bool = True, data_size: str = "medium") -> Dict[str, Any]:
        """
        Seed the database with mock data
        
        Args:
            clear_first: Whether to clear existing test data first
            data_size: Size of dataset - "small", "medium", or "large"
            
        Returns:
            Dictionary with seeding results and statistics
        """
        if settings.ENVIRONMENT.lower() not in ["development", "testing"]:
            logger.warning("Database seeding is only allowed in development/testing environments")
            return {"error": "Seeding not allowed in production"}
        
        logger.info(f"Starting database seeding with size: {data_size}")
        
        results = {
            "cleared": False,
            "projects_created": 0,
            "documents_created": 0, 
            "file_tree_items_created": 0,
            "tags_created": 0,
            "errors": []
        }
        
        try:
            # Validate seeding preconditions before clearing data
            await self._validate_seeding_preconditions()
            
            # Clear existing data if requested
            if clear_first:
                await self._clear_test_data()
                results["cleared"] = True
                logger.info("Cleared existing test data")
            
            # Create global tags first
            global_tag_results = await self._create_global_tags()
            results["tags_created"] += global_tag_results["tags_created"]
            if global_tag_results.get("errors"):
                results["errors"].extend(global_tag_results["errors"])
            
            # Get the created global tags for assignment
            global_tags = await self.repositories.tag.get_global_tags()
            
            # Determine number of projects based on data size
            project_counts = {
                "small": 2,
                "medium": 3,
                "large": 5
            }
            num_projects = project_counts.get(data_size, 3)
            
            # Create projects using templates
            templates = [
                ProjectTemplates.FANTASY_NOVEL,
                ProjectTemplates.SCIFI_THRILLER, 
                ProjectTemplates.MYSTERY_NOVEL
            ]
            
            for i in range(num_projects):
                template = templates[i % len(templates)]
                
                try:
                    project_result = await self._create_project_from_template(template, global_tags)
                    results["projects_created"] += 1
                    results["documents_created"] += project_result["documents_created"]
                    results["file_tree_items_created"] += project_result["file_tree_items_created"]
                    
                    logger.info(f"Created project {i+1}/{num_projects}: {project_result['project_title']}")
                    
                except Exception as e:
                    error_msg = f"Failed to create project {i+1}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
            
            logger.info(f"Database seeding completed: {results['tags_created']} tags, {results['projects_created']} projects, "
                       f"{results['documents_created']} documents, {results['file_tree_items_created']} file items")
            
        except Exception as e:
            error_msg = f"Database seeding failed: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        return results
    
    async def _validate_seeding_preconditions(self) -> None:
        """
        Validate that seeding can succeed before clearing any data
        
        Raises:
            Exception: If seeding preconditions are not met
        """
        try:
            # Check that repositories are accessible
            test_projects = await self.repositories.project.list_all()
            logger.debug(f"Repository validation successful (found {len(test_projects)} existing projects)")
            
            # Check that mock data factory can generate data
            test_project_data = self.factory.generate_project(genre="fantasy")
            if not test_project_data or not test_project_data.get('title'):
                raise Exception("Mock data factory is not working properly")
            
            # Check that required mock data templates exist
            from src.database.seed import ProjectTemplates
            required_templates = [
                ProjectTemplates.FANTASY_NOVEL,
                ProjectTemplates.SCIFI_THRILLER,
                ProjectTemplates.MYSTERY_NOVEL
            ]
            for template in required_templates:
                if not template or not template.get('genre'):
                    raise Exception(f"Invalid project template: {template}")
            
            logger.debug("All seeding preconditions validated successfully")
            
        except Exception as e:
            logger.error(f"Seeding precondition validation failed: {e}")
            raise Exception(f"Cannot proceed with seeding: {e}")
    
    async def _clear_test_data(self) -> None:
        """Clear all test data from tables with the configured prefix"""
        if settings.DATABASE_BACKEND == "memory":
            # For memory backend, the repositories handle their own data clearing
            # In-memory repositories are automatically fresh on each restart
            logger.info("Memory backend detected - data automatically cleared on restart")
            return
            
        if not settings.table_prefix:
            logger.warning("No table prefix configured - skipping data clearing for safety")
            return
            
        logger.info(f"Clearing tables with prefix: {settings.table_prefix}")
        
        try:
            # Get database engine and clear tables
            from src.database.connection import get_engine
            from sqlalchemy import text
            
            engine = get_engine()
            
            async with engine.begin() as conn:
                # Clear in reverse dependency order to avoid foreign key constraints
                await conn.execute(text(f"DELETE FROM {settings.table_prefix}file_tree_items"))
                await conn.execute(text(f"DELETE FROM {settings.table_prefix}documents")) 
                await conn.execute(text(f"DELETE FROM {settings.table_prefix}projects"))
                await conn.execute(text(f"DELETE FROM {settings.table_prefix}tags"))
                
                logger.info("Successfully cleared test data")
                
        except Exception as e:
            logger.error(f"Failed to clear test data: {e}")
            raise
    
    async def _create_project_from_template(self, template: Dict[str, Any], global_tags: List = None) -> Dict[str, Any]:
        """Create a complete project with structure from template"""
        # Generate project data
        project_data = self.factory.generate_project(genre=template["genre"])
        
        # Assign relevant global tags to the project
        if global_tags:
            project_tags = self._select_relevant_tags(global_tags, template["genre"], "project")
            project_data["tag_ids"] = [tag.id for tag in project_tags]
        
        project = await self.repositories.project.create(project_data)
        
        result = {
            "project_title": project.title,
            "project_id": project.id,
            "documents_created": 0,
            "file_tree_items_created": 0
        }
        
        # Create folder structure
        folder_map = {}  # name -> folder_item
        for folder_config in template["folders"]:
            folder_item_data = self.factory.generate_file_tree_item(
                project_id=project.id,
                name=folder_config["name"],
                item_type="folder", 
                path=folder_config["path"]
            )
            
            # Assign relevant global tags to folders
            if global_tags:
                folder_tags = self._select_relevant_tags(global_tags, folder_config["name"], "folder")
                folder_item_data["tag_ids"] = [tag.id for tag in folder_tags]
            
            folder_item = await self.repositories.file_tree.create(folder_item_data)
            folder_map[folder_config["name"]] = folder_item
            result["file_tree_items_created"] += 1
        
        # Create documents and file items
        chapter_counter = 1
        for doc_config in template["documents"]:
            folder_name = doc_config["folder"]
            folder_item = folder_map.get(folder_name)
            
            if not folder_item:
                logger.warning(f"Folder {folder_name} not found for documents")
                continue
            
            for i in range(doc_config["count"]):
                # Generate document
                if doc_config["type"] == "chapter":
                    document_data = self.factory.generate_document(
                        project_id=project.id,
                        document_type="chapter",
                        chapter_num=chapter_counter
                    )
                    chapter_counter += 1
                else:
                    document_data = self.factory.generate_document(
                        project_id=project.id,
                        document_type=doc_config["type"]
                    )
                
                # Assign relevant global tags to documents
                if global_tags:
                    doc_tags = self._select_relevant_tags(global_tags, doc_config["type"], "document")
                    document_data["tag_ids"] = [tag.id for tag in doc_tags]
                
                document = await self.repositories.document.create(document_data)
                result["documents_created"] += 1
                
                # Create corresponding file tree item
                file_path = document.path
                file_name = file_path.split("/")[-1]
                
                file_item_data = self.factory.generate_file_tree_item(
                    project_id=project.id,
                    name=file_name,
                    item_type="file",
                    path=file_path,
                    parent_id=folder_item.id,
                    document_id=document.id
                )
                
                # Assign relevant global tags to file items (inherit from document plus file-specific)
                if global_tags:
                    file_tags = self._select_relevant_tags(global_tags, doc_config["type"], "file")
                    file_item_data["tag_ids"] = [tag.id for tag in file_tags]
                
                await self.repositories.file_tree.create(file_item_data)
                result["file_tree_items_created"] += 1
        
        # Update project document count
        await self.repositories.project.update(project.id, {
            "document_count": result["documents_created"],
            "word_count": sum(doc.word_count for doc in 
                            await self._get_project_documents(project.id))
        })
        
        return result
    
    async def _create_global_tags(self) -> Dict[str, Any]:
        """Create global system tags available to all users"""
        result = {
            "tags_created": 0,
            "errors": []
        }
        
        try:
            # Generate global tags
            global_tags = self.factory.generate_global_tags()
            
            # Create each global tag
            for tag_data in global_tags:
                try:
                    await self.repositories.tag.create(tag_data)
                    result["tags_created"] += 1
                except Exception as e:
                    error_msg = f"Failed to create global tag '{tag_data['name']}': {str(e)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)
            
            logger.info(f"Created {result['tags_created']} global tags")
            
        except Exception as e:
            error_msg = f"Failed to create global tags: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
        
        return result
    
    def _select_relevant_tags(self, global_tags: List, context: str, entity_type: str) -> List:
        """Select relevant tags for an entity based on context and type"""
        if not global_tags:
            return []
        
        # Create mapping of tag names to tag objects for easy lookup
        tag_map = {tag.name: tag for tag in global_tags}
        relevant_tags = []
        
        # Always add some status tags with probability
        status_tags = ["draft", "review", "published"]
        for tag_name in status_tags:
            if tag_name in tag_map and random.random() < 0.3:  # 30% chance
                relevant_tags.append(tag_map[tag_name])
        
        # Add content type tags based on context
        content_type_map = {
            "chapter": ["chapter"],
            "character": ["character"],
            "location": ["location"],
            "notes": ["notes"],
            "research": ["research"],
            "Characters": ["character"],
            "Locations": ["location"],
            "Notes": ["notes"],
            "Research": ["research"],
            "Chapters": ["chapter"],
            "Magic System": ["research"],
            "Technology": ["research"],
            "Clues": ["notes"],
            "Timeline": ["notes"]
        }
        
        if context in content_type_map:
            for tag_name in content_type_map[context]:
                if tag_name in tag_map and tag_map[tag_name] not in relevant_tags:
                    relevant_tags.append(tag_map[tag_name])
        
        # Add genre tags based on project genre (for projects and some documents)
        if entity_type in ["project", "document"]:
            genre_tags = ["fantasy", "sci-fi", "mystery", "romance", "thriller"]
            context_lower = context.lower()
            for genre in genre_tags:
                if genre in context_lower and genre in tag_map:
                    if tag_map[genre] not in relevant_tags:
                        relevant_tags.append(tag_map[genre])
        
        # Add some random priority tags occasionally
        priority_tags = ["high-priority", "medium-priority", "low-priority"]
        if random.random() < 0.2:  # 20% chance
            priority_tag = random.choice(priority_tags)
            if priority_tag in tag_map and tag_map[priority_tag] not in relevant_tags:
                relevant_tags.append(tag_map[priority_tag])
        
        # Limit to 2-4 tags per entity to keep it realistic
        if len(relevant_tags) > 4:
            relevant_tags = random.sample(relevant_tags, 4)
        
        return relevant_tags
    
    async def _get_project_documents(self, project_id: str) -> List[Any]:
        """Get all documents for a project (helper method)"""
        # This is a simplified implementation - in a real scenario you'd
        # have a method on the document repository to get by project_id
        try:
            # For now, return empty list since we don't have get_by_project_id implemented
            return []
        except Exception:
            return []


async def seed_development_database(force: bool = False) -> Dict[str, Any]:
    """
    Main function to seed development database
    
    Args:
        force: If True, seed even if database is not empty
    
    Returns:
        Seeding results and statistics
    """
    if settings.ENVIRONMENT.lower() not in ["development", "testing"]:
        return {"error": "Seeding only allowed in development/testing"}
    
    logger.info("Initializing database seeding for development environment")
    
    try:
        # Check if database is empty (unless forced)
        if not force:
            is_empty = await is_database_empty()
            if not is_empty:
                logger.info("Database is not empty - skipping automatic seeding. Use force=True to seed anyway.")
                return {
                    "skipped": True, 
                    "reason": "Database is not empty",
                    "projects_created": 0,
                    "documents_created": 0,
                    "file_tree_items_created": 0,
                    "errors": []
                }
        
        repositories = get_repositories()
        seeder = DatabaseSeeder(repositories)
        
        # Get seeding configuration from settings
        data_size = getattr(settings, 'SEED_DATA_SIZE', 'medium')
        clear_first = getattr(settings, 'CLEAR_BEFORE_SEED', True)
        
        # If forcing and not clearing, don't clear to avoid data loss
        if force and not clear_first:
            logger.info("Forced seeding without clearing existing data")
        
        results = await seeder.seed_database(
            clear_first=clear_first,
            data_size=data_size
        )
        
        return results
        
    except Exception as e:
        error_msg = f"Database seeding initialization failed: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}


async def is_database_empty() -> bool:
    """
    Check if the database is empty (no projects exist)
    
    Returns:
        True if database is empty, False otherwise
    """
    try:
        repositories = get_repositories()
        all_projects = await repositories.project.list_all()
        return len(all_projects) == 0
    except Exception as e:
        logger.warning(f"Could not check if database is empty: {e}")
        # If we can't check, assume it's not empty to be safe
        return False


def should_seed_database() -> bool:
    """
    Determine if database should be seeded based on configuration and database state
    
    Auto-seeds in development if database is empty, unless explicitly disabled.
    Never seeds in production for safety.
    
    Returns:
        True if seeding should occur, False otherwise
    """
    # Never seed in production for safety
    if settings.ENVIRONMENT.lower() not in ["development", "testing"]:
        logger.info("Skipping seeding: not in development/testing environment")
        return False
    
    # Check if seeding is explicitly disabled
    if hasattr(settings, 'ENABLE_DATABASE_SEEDING'):
        explicit_setting = getattr(settings, 'ENABLE_DATABASE_SEEDING', None)
        if explicit_setting is False:
            logger.info("Seeding explicitly disabled via ENABLE_DATABASE_SEEDING=false")
            return False
        elif explicit_setting is True:
            logger.info("Seeding explicitly enabled via ENABLE_DATABASE_SEEDING=true")
            return True
    
    # Default behavior in development: seed if database appears empty
    # Note: This will be checked again in seed_development_database() with async context
    logger.info("Development environment detected - will check if database is empty")
    return True