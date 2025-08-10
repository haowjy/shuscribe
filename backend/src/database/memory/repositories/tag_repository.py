# backend/src/database/memory/repositories/tag_repository.py
"""
Memory Tag repository implementation
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC

from src.database.interfaces.tag_repository import TagRepository
from src.database.interfaces.models import Tag as DomainTag


class MemoryTagRepository(TagRepository):
    """In-memory tag repository for testing"""
    
    def __init__(self):
        self._tags: Dict[str, DomainTag] = {}
    
    async def get_by_id(self, tag_id: str) -> Optional[DomainTag]:
        return self._tags.get(tag_id)
    
    async def get_global_tags(self, include_archived: bool = False) -> List[DomainTag]:
        tags = [tag for tag in self._tags.values() if tag.is_global]
        if not include_archived:
            tags = [tag for tag in tags if not tag.is_archived]
        return sorted(tags, key=lambda t: t.name)
    
    async def get_user_tags(self, user_id: str, include_archived: bool = False) -> List[DomainTag]:
        tags = [tag for tag in self._tags.values() if tag.user_id == user_id]
        if not include_archived:
            tags = [tag for tag in tags if not tag.is_archived]
        return sorted(tags, key=lambda t: t.name)
    
    async def get_by_project_id(self, project_id: str, include_archived: bool = False) -> List[DomainTag]:
        tags = [tag for tag in self._tags.values() if tag.project_id == project_id]
        if not include_archived:
            tags = [tag for tag in tags if not tag.is_archived]
        return sorted(tags, key=lambda t: t.name)
    
    async def get_by_name(self, name: str, user_id: Optional[str] = None) -> Optional[DomainTag]:
        for tag in self._tags.values():
            if user_id is None:
                # Search global tags
                if tag.name == name and tag.is_global:
                    return tag
            else:
                # Search user's private tags
                if tag.name == name and tag.user_id == user_id:
                    return tag
        return None
    
    async def create(self, tag_data: Dict[str, Any]) -> DomainTag:
        tag_id = tag_data.get("id", str(uuid.uuid4()))
        now = datetime.now(UTC).replace(tzinfo=None)
        
        tag = DomainTag(
            id=tag_id,
            name=tag_data["name"],
            icon=tag_data.get("icon"),
            color=tag_data.get("color"),
            description=tag_data.get("description"),
            category=tag_data.get("category"),
            is_global=tag_data.get("is_global", False),
            user_id=tag_data.get("user_id"),
            project_id=tag_data.get("project_id"),
            usage_count=tag_data.get("usage_count", 0),
            is_system=tag_data.get("is_system", False),
            is_archived=tag_data.get("is_archived", False),
            created_at=now,
            updated_at=now,
        )
        self._tags[tag_id] = tag
        return tag
    
    async def update(self, tag_id: str, updates: Dict[str, Any]) -> Optional[DomainTag]:
        if tag_id not in self._tags:
            return None
        
        tag = self._tags[tag_id]
        
        # Create updated tag (dataclass is immutable)
        update_data = {
            "id": tag.id,
            "name": updates.get("name", tag.name),
            "icon": updates.get("icon", tag.icon),
            "color": updates.get("color", tag.color),
            "description": updates.get("description", tag.description),
            "category": updates.get("category", tag.category),
            "is_global": updates.get("is_global", tag.is_global),
            "user_id": updates.get("user_id", tag.user_id),
            "project_id": updates.get("project_id", tag.project_id),
            "usage_count": updates.get("usage_count", tag.usage_count),
            "is_system": updates.get("is_system", tag.is_system),
            "is_archived": updates.get("is_archived", tag.is_archived),
            "created_at": tag.created_at,
            "updated_at": datetime.now(UTC).replace(tzinfo=None),
        }
        
        updated_tag = DomainTag(**update_data)
        self._tags[tag_id] = updated_tag
        return updated_tag
    
    async def delete(self, tag_id: str) -> bool:
        if tag_id in self._tags:
            del self._tags[tag_id]
            return True
        return False
    
    async def archive(self, tag_id: str) -> Optional[DomainTag]:
        return await self.update(tag_id, {"is_archived": True})
    
    async def unarchive(self, tag_id: str) -> Optional[DomainTag]:
        return await self.update(tag_id, {"is_archived": False})
    
    async def increment_usage(self, tag_id: str) -> Optional[DomainTag]:
        if tag_id in self._tags:
            tag = self._tags[tag_id]
            return await self.update(tag_id, {"usage_count": tag.usage_count + 1})
        return None
    
    async def decrement_usage(self, tag_id: str) -> Optional[DomainTag]:
        if tag_id in self._tags:
            tag = self._tags[tag_id]
            return await self.update(tag_id, {"usage_count": max(0, tag.usage_count - 1)})
        return None
    
    async def get_by_category(self, category: str, user_id: Optional[str] = None) -> List[DomainTag]:
        if user_id is None:
            # Get global tags by category
            tags = [
                tag for tag in self._tags.values()
                if tag.is_global and tag.category == category and not tag.is_archived
            ]
        else:
            # Get global and user's private tags by category
            tags = [
                tag for tag in self._tags.values()
                if tag.category == category and not tag.is_archived
                and (tag.is_global or tag.user_id == user_id)
            ]
        return sorted(tags, key=lambda t: t.name)
    
    async def get_system_tags(self) -> List[DomainTag]:
        tags = [
            tag for tag in self._tags.values()
            if tag.is_system and tag.is_global and not tag.is_archived
        ]
        return sorted(tags, key=lambda t: t.name)
    
    async def search_tags(self, query: str, user_id: Optional[str] = None, limit: int = 20) -> List[DomainTag]:
        if user_id is None:
            # Search only global tags
            tags = [
                tag for tag in self._tags.values()
                if tag.is_global
                and query.lower() in tag.name.lower()
                and not tag.is_archived
            ]
        else:
            # Search global and user's private tags
            tags = [
                tag for tag in self._tags.values()
                if query.lower() in tag.name.lower()
                and not tag.is_archived
                and (tag.is_global or tag.user_id == user_id)
            ]
        # Sort by usage count desc, then name
        tags.sort(key=lambda t: (-t.usage_count, t.name))
        return tags[:limit]
    
    # Tag forking and precedence methods
    
    async def get_global_tag_by_name(self, name: str) -> Optional[DomainTag]:
        """Get global tag by name"""
        for tag in self._tags.values():
            if tag.name == name and tag.is_global and not tag.is_archived:
                return tag
        return None
    
    async def get_project_tag_by_name(self, project_id: str, name: str) -> Optional[DomainTag]:
        """Get project-specific tag by name"""
        for tag in self._tags.values():
            if (tag.name == name and 
                tag.project_id == project_id and 
                not tag.is_archived):
                return tag
        return None
    
    async def get_tag_by_name_with_precedence(self, project_id: str, name: str) -> Optional[DomainTag]:
        """Get tag by name with project → global precedence"""
        # Try project-specific first
        project_tag = await self.get_project_tag_by_name(project_id, name)
        if project_tag:
            return project_tag
        
        # Fallback to global
        return await self.get_global_tag_by_name(name)
    
    async def get_all_usable_tags(self, project_id: str, include_archived: bool = False) -> List[DomainTag]:
        """Get all tags available to project (project-specific + global) with precedence deduplication"""
        # Get all tags that are either project-specific or global
        candidate_tags = [
            tag for tag in self._tags.values()
            if (tag.project_id == project_id or tag.is_global) and 
            (include_archived or not tag.is_archived)
        ]
        
        # Deduplicate by name with project precedence
        tag_by_name = {}
        for tag in candidate_tags:
            if tag.name not in tag_by_name:
                tag_by_name[tag.name] = tag
            else:
                # Keep project-specific over global (project_id is not None)
                current = tag_by_name[tag.name]
                if tag.project_id == project_id and current.is_global:
                    tag_by_name[tag.name] = tag
        
        # Return sorted by name
        return sorted(tag_by_name.values(), key=lambda t: t.name)
    
    async def fork_global_tag(self, project_id: str, global_tag_id: str, customizations: Dict[str, Any]) -> DomainTag:
        """Create project-specific copy of global tag with customizations"""
        # Get the global tag
        global_tag = self._tags.get(global_tag_id)
        if not global_tag:
            raise ValueError(f"Tag with ID {global_tag_id} not found")
        
        if not global_tag.is_global:
            raise ValueError("Can only fork global tags")
        
        # Check if project-specific tag with same name already exists
        existing_project_tag = await self.get_project_tag_by_name(project_id, global_tag.name)
        if existing_project_tag:
            raise ValueError(f"Project-specific tag '{global_tag.name}' already exists")
        
        # Create project-specific copy with customizations
        fork_data = {
            "name": global_tag.name,
            "description": global_tag.description,
            "category": global_tag.category,
            "project_id": project_id,
            "is_global": False,
            "is_system": False,  # Forked tags are never system tags
            "usage_count": 0,    # Start with zero usage
            # Apply customizations
            **customizations
        }
        
        # Use the existing create method
        return await self.create(fork_data)