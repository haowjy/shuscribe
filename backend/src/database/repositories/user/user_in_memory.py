# backend/src/database/repositories/user_in_memory.py
"""In-memory implementation of the User Repository for development and testing."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from src.schemas.user import User, UserAPIKey
from src.database.repositories.user.user_abc import AbstractUserRepository
from src.core.exceptions import ShuScribeException


class InMemoryUserRepository(AbstractUserRepository):
    """In-memory user repository for when a database is not available."""

    def __init__(self):
        self._users: Dict[UUID, User] = {}
        self._api_keys: Dict[str, UserAPIKey] = {}

    async def get(self, id: UUID) -> Optional[User]:
        return self._users.get(id)

    async def get_multi(self, *, offset: int = 0, limit: int = 100) -> List[User]:
        return list(self._users.values())[offset : offset + limit]

    async def create(self, obj_in: dict) -> User:
        if "id" not in obj_in:
            obj_in["id"] = uuid.uuid4()
        
        if await self.get_by_email(obj_in["email"]):
            raise ShuScribeException(f"User with email {obj_in['email']} already exists.")

        # Add required timestamp fields
        if "created_at" not in obj_in:
            obj_in["created_at"] = datetime.utcnow()
        if "updated_at" not in obj_in:
            obj_in["updated_at"] = None

        user = User(**obj_in)
        self._users[user.id] = user
        return user

    async def update(self, db_obj: User, obj_in: dict) -> User:
        user = self._users.get(db_obj.id)
        if not user:
            raise ShuScribeException("User not found")

        for field, value in obj_in.items():
            setattr(user, field, value)
        user.updated_at = datetime.utcnow()
        return user

    async def delete(self, db_obj: User) -> None:
        if db_obj.id in self._users:
            del self._users[db_obj.id]

    async def get_by_email(self, email: str) -> Optional[User]:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def _get_api_key_composite_key(self, user_id: UUID, provider: str) -> str:
        return f"{user_id}::{provider}"

    async def get_api_key(self, user_id: UUID, provider: str) -> Optional[UserAPIKey]:
        return self._api_keys.get(self._get_api_key_composite_key(user_id, provider))

    async def get_all_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        return [key for key in self._api_keys.values() if key.user_id == user_id]

    async def store_api_key(
        self,
        user_id: UUID,
        provider: str,
        encrypted_key: str,
        provider_metadata: Optional[dict] = None,
        validation_status: str = "pending",
        last_validated_at: Optional[datetime] = None,
    ) -> UserAPIKey:
        composite_key = self._get_api_key_composite_key(user_id, provider)
        
        if composite_key in self._api_keys:
            key = self._api_keys[composite_key]
            key.encrypted_api_key = encrypted_key
            key.provider_metadata = provider_metadata
            key.validation_status = validation_status
            key.last_validated_at = last_validated_at
            key.updated_at = datetime.utcnow()
        else:
            key = UserAPIKey(
                user_id=user_id,
                provider=provider,
                encrypted_api_key=encrypted_key,
                provider_metadata=provider_metadata,
                validation_status=validation_status,
                last_validated_at=last_validated_at,
                created_at=datetime.utcnow(),
                updated_at=None,
            )
            self._api_keys[composite_key] = key
        return key

    async def delete_api_key(self, user_id: UUID, provider: str) -> bool:
        composite_key = self._get_api_key_composite_key(user_id, provider)
        if composite_key in self._api_keys:
            del self._api_keys[composite_key]
            return True
        return False
