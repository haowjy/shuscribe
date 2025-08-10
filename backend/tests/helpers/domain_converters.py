"""
Helpers for converting domain models to repository-compatible dictionaries.

This bridge layer allows tests to use proper domain models while working with
the current repository interfaces that expect dictionaries.
"""
from typing import Dict, Any

from src.database.interfaces.models import Project, Document, FileTreeItem, Tag, User, UserAPIKey


class DomainToRepositoryConverter:
    """Convert domain models to dictionaries for repository method calls."""
    
    @staticmethod
    def project_to_dict(project: Project) -> Dict[str, Any]:
        """Convert Project domain model to repository dictionary format."""
        return {
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "owner_id": project.owner_id,
            "created_by": project.created_by,
            "updated_by": project.updated_by,
            "collaborators": project.collaborators,
            "word_count": project.word_count,
            "document_count": project.document_count,
            "settings": project.settings,
            "tags": project.tags,
            # Timestamps are handled by repository layer
        }
    
    @staticmethod
    def document_to_dict(document: Document) -> Dict[str, Any]:
        """Convert Document domain model to repository dictionary format."""
        return {
            "id": document.id,
            "project_id": document.project_id,
            "title": document.title,
            "path": document.path,
            "content": document.content,
            "word_count": document.word_count,
            "version": document.version,
            "is_locked": document.is_locked,
            "locked_by": document.locked_by,
            "file_tree_id": document.file_tree_id,
            "created_by": document.created_by,
            "updated_by": document.updated_by,
            "tags": document.tags,
            # Timestamps are handled by repository layer
        }
    
    @staticmethod
    def file_tree_item_to_dict(item: FileTreeItem) -> Dict[str, Any]:
        """Convert FileTreeItem domain model to repository dictionary format."""
        return {
            "id": item.id,
            "project_id": item.project_id,
            "name": item.name,
            "type": item.type,
            "path": item.path,
            "parent_id": item.parent_id,
            "document_id": item.document_id,
            "word_count": item.word_count,
            "icon": item.icon,
            "tags": item.tags,
            # Timestamps are handled by repository layer
        }
    
    @staticmethod
    def tag_to_dict(tag: Tag) -> Dict[str, Any]:
        """Convert Tag domain model to repository dictionary format."""
        return {
            "id": tag.id,
            "name": tag.name,
            "icon": tag.icon,
            "color": tag.color,
            "description": tag.description,
            "category": tag.category,
            "project_id": tag.project_id,
            "is_global": tag.is_global,
            "user_id": tag.user_id,
            "is_system": tag.is_system,
            "is_archived": tag.is_archived,
            "usage_count": tag.usage_count,
            # Timestamps are handled by repository layer
        }
    
    @staticmethod
    def user_to_dict(user: User) -> Dict[str, Any]:
        """Convert User domain model to repository dictionary format."""
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "metadata": user.metadata,
            # Timestamps are handled by repository layer
        }
    
    @staticmethod
    def user_api_key_to_dict(api_key: UserAPIKey) -> Dict[str, Any]:
        """Convert UserAPIKey domain model to repository dictionary format."""
        return {
            "user_id": api_key.user_id,
            "provider": api_key.provider,
            "encrypted_api_key": api_key.encrypted_api_key,
            "validation_status": api_key.validation_status,
            "last_validated_at": api_key.last_validated_at,
            "provider_metadata": api_key.provider_metadata,
            # Timestamps are handled by repository layer
        }
    
    @staticmethod
    def project_updates_to_dict(project: Project, fields_to_update: set = None) -> Dict[str, Any]:
        """
        Convert Project domain model to update dictionary for repository update calls.
        
        Args:
            project: Project domain model
            fields_to_update: Set of field names to include in update, or None for all fields
            
        Returns:
            Dictionary with only the specified fields for updating
        """
        full_dict = DomainToRepositoryConverter.project_to_dict(project)
        
        if fields_to_update is None:
            # Remove id since it shouldn't be updated
            full_dict.pop("id", None)
            return full_dict
        
        return {key: value for key, value in full_dict.items() if key in fields_to_update}