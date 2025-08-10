# backend/src/database/sqlalchemy/repositories/user_repository.py
"""
SQLAlchemy User repository implementation
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC

from sqlalchemy import select, update, delete

from src.database.interfaces.user_repository import IUserRepository
from src.database.interfaces.models import User as DomainUser, UserAPIKey as DomainUserAPIKey
from src.database.connection import get_session_context
from src.database.sqlalchemy.models import User as SQLAlchemyUser, UserAPIKey as SQLAlchemyUserAPIKey
from src.database.sqlalchemy.mappers import UserMapper, UserAPIKeyMapper
from src.core.constants import PROVIDER_ID

logger = logging.getLogger(__name__)


class DatabaseUserRepository(IUserRepository):
    """Database-backed user repository using SQLAlchemy"""
    
    async def get_user_by_id(self, user_id: str) -> Optional[DomainUser]:
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyUser).where(SQLAlchemyUser.id == user_id)
            )
            sqlalchemy_user = result.scalar_one_or_none()
            
            if sqlalchemy_user:
                return UserMapper.to_domain(sqlalchemy_user)
            return None

    async def create_or_update_user(self, user_id: str, email: str, metadata: Optional[Dict[str, Any]] = None) -> DomainUser:
        async with get_session_context() as session:
            # Check if user exists
            existing_user = await session.get(SQLAlchemyUser, user_id)
            
            if existing_user:
                # Update existing user
                existing_user.email = email
                existing_user.user_metadata = metadata or {}
                existing_user.updated_at = datetime.now(UTC).replace(tzinfo=None)
                await session.flush()
                return UserMapper.to_domain(existing_user)
            else:
                # Create new user
                domain_user = DomainUser(
                    id=user_id,
                    email=email,
                    metadata=metadata or {}
                )
                sqlalchemy_user = UserMapper.to_sqlalchemy(domain_user)
                session.add(sqlalchemy_user)
                await session.flush()
                return UserMapper.to_domain(sqlalchemy_user)

    async def get_api_key(self, user_id: str, provider: PROVIDER_ID) -> Optional[DomainUserAPIKey]:
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyUserAPIKey).where(
                    SQLAlchemyUserAPIKey.user_id == user_id,
                    SQLAlchemyUserAPIKey.provider == provider
                )
            )
            sqlalchemy_api_key = result.scalar_one_or_none()
            
            if sqlalchemy_api_key:
                return UserAPIKeyMapper.to_domain(sqlalchemy_api_key)
            return None

    async def store_api_key(
        self, 
        user_id: str, 
        provider: PROVIDER_ID, 
        encrypted_api_key: str,
        validation_status: str = "unknown",
        provider_metadata: Optional[Dict[str, Any]] = None
    ) -> DomainUserAPIKey:
        async with get_session_context() as session:
            # Check if API key already exists
            existing_key = await session.execute(
                select(SQLAlchemyUserAPIKey).where(
                    SQLAlchemyUserAPIKey.user_id == user_id,
                    SQLAlchemyUserAPIKey.provider == provider
                )
            )
            existing_api_key = existing_key.scalar_one_or_none()
            
            if existing_api_key:
                # Update existing API key
                existing_api_key.encrypted_api_key = encrypted_api_key
                existing_api_key.validation_status = validation_status
                existing_api_key.provider_metadata = provider_metadata or {}
                existing_api_key.updated_at = datetime.now(UTC).replace(tzinfo=None)
                await session.flush()
                return UserAPIKeyMapper.to_domain(existing_api_key)
            else:
                # Create new API key
                domain_api_key = DomainUserAPIKey(
                    user_id=user_id,
                    provider=provider,
                    encrypted_api_key=encrypted_api_key,
                    validation_status=validation_status,
                    provider_metadata=provider_metadata or {}
                )
                sqlalchemy_api_key = UserAPIKeyMapper.to_sqlalchemy(domain_api_key)
                session.add(sqlalchemy_api_key)
                await session.flush()
                return UserAPIKeyMapper.to_domain(sqlalchemy_api_key)

    async def delete_api_key(self, user_id: str, provider: PROVIDER_ID) -> bool:
        async with get_session_context() as session:
            result = await session.execute(
                delete(SQLAlchemyUserAPIKey).where(
                    SQLAlchemyUserAPIKey.user_id == user_id,
                    SQLAlchemyUserAPIKey.provider == provider
                )
            )
            return result.rowcount > 0

    async def list_user_api_keys(self, user_id: str) -> List[DomainUserAPIKey]:
        async with get_session_context() as session:
            result = await session.execute(
                select(SQLAlchemyUserAPIKey).where(SQLAlchemyUserAPIKey.user_id == user_id)
            )
            sqlalchemy_api_keys = result.scalars().all()
            
            return [UserAPIKeyMapper.to_domain(api_key) for api_key in sqlalchemy_api_keys]

    async def update_api_key_validation(
        self, 
        user_id: str, 
        provider: PROVIDER_ID, 
        validation_status: str,
        last_validated_at: Optional[datetime] = None
    ) -> bool:
        async with get_session_context() as session:
            result = await session.execute(
                update(SQLAlchemyUserAPIKey)
                .where(
                    SQLAlchemyUserAPIKey.user_id == user_id,
                    SQLAlchemyUserAPIKey.provider == provider
                )
                .values(
                    validation_status=validation_status,
                    last_validated_at=last_validated_at or datetime.now(UTC).replace(tzinfo=None),
                    updated_at=datetime.now(UTC).replace(tzinfo=None)
                )
            )
            return result.rowcount > 0