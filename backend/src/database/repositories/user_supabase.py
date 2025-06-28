"""
Supabase-backed user repository with API key management
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from supabase import Client

from src.schemas.user import User, UserAPIKey, UserCreate, UserAPIKeyCreate
from src.database.repositories.user_abc import AbstractUserRepository
from src.core.exceptions import ShuScribeException


class SupabaseUserRepository(AbstractUserRepository):
    """Repository for user operations, backed by Supabase."""
    
    def __init__(self, client: Client):
        self.client = client
    
    async def get(self, id: UUID) -> Optional[User]:
        """Retrieve a single user by their ID."""
        try:
            response = self.client.table("users").select("*").eq("id", str(id)).execute()
            if response.data:
                return User(**response.data[0])
            return None
        except Exception as e:
            raise ShuScribeException(f"Error retrieving user {id}: {e}")
    
    async def get_multi(self, *, offset: int = 0, limit: int = 100) -> List[User]:
        """Retrieve multiple users with pagination."""
        try:
            response = (
                self.client.table("users")
                .select("*")
                .range(offset, offset + limit - 1)
                .execute()
            )
            return [User(**user) for user in response.data]
        except Exception as e:
            raise ShuScribeException(f"Error retrieving users: {e}")
    
    async def create(self, obj_in: dict) -> User:
        """Create a new user."""
        try:
            # Add ID if not provided
            if "id" not in obj_in:
                obj_in["id"] = str(uuid4())
            
            response = self.client.table("users").insert(obj_in).execute()
            if response.data:
                return User(**response.data[0])
            raise ShuScribeException("Failed to create user: no data returned")
        except Exception as e:
            raise ShuScribeException(f"Error creating user: {e}")
    
    async def update(self, db_obj: User, obj_in: dict) -> User:
        """Update an existing user."""
        try:
            # Add updated_at timestamp
            obj_in["updated_at"] = datetime.utcnow().isoformat()
            
            response = (
                self.client.table("users")
                .update(obj_in)
                .eq("id", str(db_obj.id))
                .execute()
            )
            if response.data:
                return User(**response.data[0])
            raise ShuScribeException("Failed to update user: no data returned")
        except Exception as e:
            raise ShuScribeException(f"Error updating user {db_obj.id}: {e}")
    
    async def delete(self, db_obj: User) -> None:
        """Delete a user."""
        try:
            self.client.table("users").delete().eq("id", str(db_obj.id)).execute()
        except Exception as e:
            raise ShuScribeException(f"Error deleting user {db_obj.id}: {e}")

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address."""
        try:
            response = self.client.table("users").select("*").eq("email", email).execute()
            if response.data:
                return User(**response.data[0])
            return None
        except Exception as e:
            raise ShuScribeException(f"Error retrieving user by email {email}: {e}")

    async def get_api_key(self, user_id: UUID, provider: str) -> Optional[UserAPIKey]:
        """Get user's API key for a specific provider."""
        try:
            response = (
                self.client.table("user_api_keys")
                .select("*")
                .eq("user_id", str(user_id))
                .eq("provider", provider)
                .execute()
            )
            if response.data:
                return UserAPIKey(**response.data[0])
            return None
        except Exception as e:
            raise ShuScribeException(f"Error retrieving API key for user {user_id}, provider {provider}: {e}")
    
    async def get_all_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        """Get all API keys for a user."""
        try:
            response = (
                self.client.table("user_api_keys")
                .select("*")
                .eq("user_id", str(user_id))
                .execute()
            )
            return [UserAPIKey(**key) for key in response.data]
        except Exception as e:
            raise ShuScribeException(f"Error retrieving API keys for user {user_id}: {e}")
    
    async def store_api_key(
        self,
        user_id: UUID,
        provider: str,
        encrypted_key: str,
        provider_metadata: Optional[dict] = None,
        validation_status: str = "pending",
        last_validated_at: Optional[datetime] = None,
    ) -> UserAPIKey:
        """Store or update user's API key for a provider."""
        try:
            # Check if key already exists
            existing_key = await self.get_api_key(user_id, provider)
            
            key_data = {
                "user_id": str(user_id),
                "provider": provider,
                "encrypted_api_key": encrypted_key,
                "provider_metadata": provider_metadata,
                "validation_status": validation_status,
                "last_validated_at": last_validated_at.isoformat() if last_validated_at else None,
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            if existing_key:
                # Update existing key
                response = (
                    self.client.table("user_api_keys")
                    .update(key_data)
                    .eq("user_id", str(user_id))
                    .eq("provider", provider)
                    .execute()
                )
            else:
                # Create new key
                response = (
                    self.client.table("user_api_keys")
                    .insert(key_data)
                    .execute()
                )
            
            if response.data:
                return UserAPIKey(**response.data[0])
            raise ShuScribeException("Failed to store API key: no data returned")
        except Exception as e:
            raise ShuScribeException(f"Error storing API key for user {user_id}, provider {provider}: {e}")
    
    async def delete_api_key(self, user_id: UUID, provider: str) -> bool:
        """Delete user's API key for a provider."""
        try:
            response = (
                self.client.table("user_api_keys")
                .delete()
                .eq("user_id", str(user_id))
                .eq("provider", provider)
                .execute()
            )
            # Supabase returns the deleted rows, so if there's data, deletion was successful
            return len(response.data) > 0
        except Exception as e:
            raise ShuScribeException(f"Error deleting API key for user {user_id}, provider {provider}: {e}") 