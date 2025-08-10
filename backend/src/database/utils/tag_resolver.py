# backend/src/database/utils/tag_resolver.py
"""
Tag resolution service for converting tag names to Tag objects
"""
import logging
import uuid
from typing import List, Dict, Set, Optional
from datetime import datetime, UTC

from src.database.interfaces.models import Tag as DomainTag
from src.database.sqlalchemy.models import Tag as SQLAlchemyTag
from src.database.connection import get_session_context
from sqlalchemy import select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class TagResolver:
    """Service for resolving tag names to Tag objects"""

    @staticmethod
    async def resolve_tags(
        session: Session,
        tag_names: List[str],
        project_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[SQLAlchemyTag]:
        """
        Resolve a list of tag names to SQLAlchemy Tag objects.
        Creates new tags if they don't exist.
        
        Args:
            session: SQLAlchemy session to use
            tag_names: List of tag name strings
            project_id: Optional project ID for project-scoped tags
            user_id: Optional user ID for user-scoped tags
            
        Returns:
            List of SQLAlchemy Tag objects
        """
        if not tag_names:
            return []

        # Get existing tags
        existing_tags = await TagResolver._get_existing_tags(
            session, tag_names, project_id, user_id
        )
        
        # Find missing tag names
        existing_names = {tag.name for tag in existing_tags}
        missing_names = [name for name in tag_names if name not in existing_names]
        
        # Create missing tags
        new_tags = []
        if missing_names:
            new_tags = await TagResolver._create_missing_tags(
                session, missing_names, project_id, user_id
            )
        
        # Return all tags
        all_tags = existing_tags + new_tags
        return all_tags

    @staticmethod
    async def _get_existing_tags(
        session: Session,
        tag_names: List[str],
        project_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[SQLAlchemyTag]:
        """Get existing tags by names"""
        # Build query for existing tags
        query = select(SQLAlchemyTag).where(SQLAlchemyTag.name.in_(tag_names))
        
        # Add scope filtering
        if project_id:
            # Project-scoped or global tags
            query = query.where(
                (SQLAlchemyTag.project_id == project_id) | 
                (SQLAlchemyTag.is_global == True)
            )
        elif user_id:
            # User-scoped or global tags
            query = query.where(
                (SQLAlchemyTag.user_id == user_id) |
                (SQLAlchemyTag.is_global == True)
            )
        else:
            # Only global tags
            query = query.where(SQLAlchemyTag.is_global == True)
        
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def _create_missing_tags(
        session: Session,
        tag_names: List[str],
        project_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[SQLAlchemyTag]:
        """Create new tags for missing names"""
        new_tags = []
        now = datetime.now(UTC).replace(tzinfo=None)
        
        for name in tag_names:
            tag = SQLAlchemyTag(
                id=str(uuid.uuid4()),
                name=name,
                project_id=project_id,
                user_id=user_id,
                is_global=(project_id is None and user_id is None),
                is_system=False,
                is_archived=False,
                usage_count=0,
                created_at=now,
                updated_at=now
            )
            session.add(tag)
            new_tags.append(tag)
        
        # Flush to get IDs
        await session.flush()
        return new_tags

    @staticmethod
    async def increment_tag_usage(tag_ids: List[str]) -> None:
        """Increment usage count for tags"""
        if not tag_ids:
            return
            
        async with get_session_context() as session:
            # Increment usage count for all tags
            for tag_id in tag_ids:
                result = await session.execute(
                    select(SQLAlchemyTag).where(SQLAlchemyTag.id == tag_id)
                )
                tag = result.scalar_one_or_none()
                if tag:
                    tag.usage_count = (tag.usage_count or 0) + 1
                    tag.updated_at = datetime.now(UTC).replace(tzinfo=None)