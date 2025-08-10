"""
TagFactory for creating Tag domain models in tests.
"""
import uuid
from datetime import datetime, UTC
from typing import Optional

from src.database.interfaces.models import Tag


class TagFactory:
    """Factory for creating Tag domain models with realistic test data."""
    
    # Fantasy writing tag presets
    FANTASY_TAGS = {
        "character": {"icon": "👤", "color": "#3b82f6", "category": "character"},
        "protagonist": {"icon": "⭐", "color": "#10b981", "category": "character"},
        "antagonist": {"icon": "🗡️", "color": "#ef4444", "category": "character"},
        "location": {"icon": "🗺️", "color": "#8b5cf6", "category": "location"},
        "magic": {"icon": "✨", "color": "#f59e0b", "category": "magic-system"},
        "fantasy": {"icon": "🏰", "color": "#6366f1", "category": "genre"},
        "adventure": {"icon": "⚔️", "color": "#059669", "category": "genre"},
        "chapter": {"icon": "📖", "color": "#06b6d4", "category": "story"},
        "draft": {"icon": "📝", "color": "#64748b", "category": "status"},
        "published": {"icon": "✅", "color": "#22c55e", "category": "status"},
        "worldbuilding": {"icon": "🌍", "color": "#7c3aed", "category": "worldbuilding"},
        "timeline": {"icon": "🕒", "color": "#f97316", "category": "timeline"},
    }
    
    @staticmethod
    def create(
        id: Optional[str] = None,
        name: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        project_id: Optional[str] = None,
        is_global: bool = False,
        user_id: Optional[str] = None,
        is_system: bool = False,
        is_archived: bool = False,
        usage_count: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs
    ) -> Tag:
        """
        Create a Tag domain model with sensible defaults.
        
        Args:
            id: Tag ID (auto-generated UUID if not provided)
            name: Tag name (auto-generated if not provided)
            icon: Display icon (auto-selected based on name if not provided)
            color: Hex color code (auto-selected based on name if not provided)
            description: Tag description (auto-generated if not provided)
            category: Tag category (auto-selected based on name if not provided)
            project_id: Project ID (auto-generated UUID if not provided and not global)
            is_global: Whether tag is global (default False)
            user_id: User ID (auto-generated UUID if not provided)
            is_system: Whether tag is system-generated (default False)
            is_archived: Whether tag is archived (default False)
            usage_count: Number of times tag is used (default 0)
            created_at: Creation timestamp (current time if not provided)
            updated_at: Update timestamp (current time if not provided)
            **kwargs: Additional keyword arguments
            
        Returns:
            Properly constructed Tag domain model
        """
        # Generate defaults
        tag_id = id or str(uuid.uuid4())
        tag_name = name or f"test-tag-{tag_id[:8]}"
        tag_user_id = user_id or str(uuid.uuid4())
        now = datetime.now(UTC).replace(tzinfo=None)
        
        # Auto-select icon, color, and category from presets
        if name and name.lower() in TagFactory.FANTASY_TAGS:
            preset = TagFactory.FANTASY_TAGS[name.lower()]
            icon = icon or preset.get("icon", "🏷️")
            color = color or preset.get("color", "#6b7280")
            category = category or preset.get("category", "general")
        else:
            icon = icon or "🏷️"
            color = color or "#6b7280"
            category = category or "general"
        
        # Generate description if not provided
        if description is None and name:
            description = f"Tag for {name} related content"
        
        # Handle project_id for non-global tags
        if not is_global and project_id is None:
            project_id = str(uuid.uuid4())
        elif is_global:
            project_id = None  # Global tags don't belong to specific projects
        
        return Tag(
            id=tag_id,
            name=tag_name,
            icon=icon,
            color=color,
            description=description,
            category=category,
            project_id=project_id,
            is_global=is_global,
            user_id=tag_user_id,
            is_system=is_system,
            is_archived=is_archived,
            usage_count=usage_count,
            created_at=created_at or now,
            updated_at=updated_at or now,
        )
    
    @staticmethod
    def create_character_tag(
        name: str = "character",
        project_id: Optional[str] = None,
        usage_count: int = 0
    ) -> Tag:
        """Create a character-related tag."""
        return TagFactory.create(
            name=name,
            icon="👤",
            color="#3b82f6",
            description="Tag for character-related content",
            category="character",
            project_id=project_id,
            usage_count=usage_count
        )
    
    @staticmethod
    def create_location_tag(
        name: str = "location",
        project_id: Optional[str] = None,
        usage_count: int = 0
    ) -> Tag:
        """Create a location-related tag."""
        return TagFactory.create(
            name=name,
            icon="🗺️",
            color="#8b5cf6",
            description="Tag for location-related content",
            category="location",
            project_id=project_id,
            usage_count=usage_count
        )
    
    @staticmethod
    def create_global_tag(
        name: str = "fantasy",
        user_id: Optional[str] = None
    ) -> Tag:
        """Create a global tag that can be shared across projects."""
        return TagFactory.create(
            name=name,
            project_id=None,
            is_global=True,
            user_id=user_id,
            usage_count=0
        )
    
    @staticmethod
    def create_system_tag(
        name: str = "system",
        project_id: Optional[str] = None
    ) -> Tag:
        """Create a system-generated tag."""
        return TagFactory.create(
            name=name,
            icon="⚙️",
            color="#6b7280",
            description="System-generated tag",
            category="system",
            project_id=project_id,
            is_system=True
        )
    
    @staticmethod
    def create_fantasy_tags(
        project_id: str,
        tag_names: Optional[list] = None
    ) -> list[Tag]:
        """Create a set of common fantasy writing tags."""
        if tag_names is None:
            tag_names = ["character", "protagonist", "location", "magic", "fantasy", "adventure", "chapter"]
        
        tags = []
        for tag_name in tag_names:
            tag = TagFactory.create(
                name=tag_name,
                project_id=project_id
            )
            tags.append(tag)
        
        return tags
    
    @staticmethod
    def create_with_high_usage(
        name: str = "popular-tag",
        project_id: Optional[str] = None,
        usage_count: int = 50
    ) -> Tag:
        """Create a tag with high usage count for testing statistics."""
        return TagFactory.create(
            name=name,
            project_id=project_id,
            usage_count=usage_count,
            icon="🔥",
            color="#ef4444",
            description="A highly used tag for testing"
        )
    
    @staticmethod
    def create_archived(
        name: str = "archived-tag",
        project_id: Optional[str] = None
    ) -> Tag:
        """Create an archived tag for testing soft deletion."""
        return TagFactory.create(
            name=name,
            project_id=project_id,
            is_archived=True,
            icon="📦",
            color="#9ca3af",
            description="An archived tag for testing"
        )