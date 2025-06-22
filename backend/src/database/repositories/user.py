# backend/src/database/repositories/user.py
"""
User repository with API key management
"""
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, UserAPIKey
from src.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for user operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_api_key(self, user_id: UUID, provider: str) -> Optional[UserAPIKey]:
        """Get user's API key for a specific provider."""
        
        stmt = select(UserAPIKey).where(
            UserAPIKey.user_id == user_id,
            UserAPIKey.provider == provider
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        """Get all API keys for a user."""
        
        stmt = select(UserAPIKey).where(UserAPIKey.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
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
        
        # Check if key already exists
        existing_key = await self.get_api_key(user_id, provider)
        
        if existing_key:
            # Update existing key
            existing_key.encrypted_api_key = encrypted_key
            existing_key.provider_metadata = provider_metadata
            existing_key.validation_status = validation_status
            existing_key.last_validated_at = last_validated_at
            self.session.add(existing_key) # Re-add to session to mark as modified
            await self.session.commit()
            await self.session.refresh(existing_key)
            return existing_key
        else:
            # Create new key
            new_key = UserAPIKey(
                user_id=user_id,
                provider=provider,
                encrypted_api_key=encrypted_key,
                provider_metadata=provider_metadata,
                validation_status=validation_status,
                last_validated_at=last_validated_at
            )
            self.session.add(new_key)
            await self.session.commit()
            await self.session.refresh(new_key)
            return new_key
    
    async def delete_api_key(self, user_id: UUID, provider: str) -> bool:
        """Delete user's API key for a provider."""
        
        key = await self.get_api_key(user_id, provider)
        if key:
            await self.session.delete(key)
            await self.session.commit()
            return True
        return False