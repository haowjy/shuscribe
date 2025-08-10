# backend/src/database/sqlalchemy/mappers/user_mapper.py
"""
Mapper for converting between domain User/UserAPIKey and SQLAlchemy User/UserAPIKey models
"""
from typing import Dict, Any

from src.database.interfaces.models import User as DomainUser, UserAPIKey as DomainUserAPIKey
from ..models import User as SQLAlchemyUser, UserAPIKey as SQLAlchemyUserAPIKey


class UserMapper:
    """Handles conversion between domain and SQLAlchemy User models"""
    
    @staticmethod
    def to_domain(sqlalchemy_user: SQLAlchemyUser) -> DomainUser:
        """Convert SQLAlchemy User to domain User"""
        return DomainUser(
            id=sqlalchemy_user.id,
            email=sqlalchemy_user.email,
            name=sqlalchemy_user.name,
            avatar_url=sqlalchemy_user.avatar_url,
            metadata=sqlalchemy_user.user_metadata or {},
            created_at=sqlalchemy_user.created_at,
            updated_at=sqlalchemy_user.updated_at,
        )
    
    @staticmethod
    def to_sqlalchemy(domain_user: DomainUser) -> SQLAlchemyUser:
        """Convert domain User to SQLAlchemy User"""
        return SQLAlchemyUser(
            id=domain_user.id,
            email=domain_user.email,
            name=domain_user.name,
            avatar_url=domain_user.avatar_url,
            user_metadata=domain_user.metadata or {},
            created_at=domain_user.created_at,
            updated_at=domain_user.updated_at,
        )
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> DomainUser:
        """Create domain User from dictionary data"""
        return DomainUser(
            id=data["id"],
            email=data["email"],
            name=data.get("name"),
            avatar_url=data.get("avatar_url"),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
    
    @staticmethod
    def to_dict(domain_user: DomainUser) -> Dict[str, Any]:
        """Convert domain User to dictionary"""
        return {
            "id": domain_user.id,
            "email": domain_user.email,
            "name": domain_user.name,
            "avatar_url": domain_user.avatar_url,
            "metadata": domain_user.metadata,
            "created_at": domain_user.created_at,
            "updated_at": domain_user.updated_at,
        }


class UserAPIKeyMapper:
    """Handles conversion between domain and SQLAlchemy UserAPIKey models"""
    
    @staticmethod
    def to_domain(sqlalchemy_api_key: SQLAlchemyUserAPIKey) -> DomainUserAPIKey:
        """Convert SQLAlchemy UserAPIKey to domain UserAPIKey"""
        return DomainUserAPIKey(
            user_id=sqlalchemy_api_key.user_id,
            provider=sqlalchemy_api_key.provider,
            encrypted_api_key=sqlalchemy_api_key.encrypted_api_key,
            validation_status=sqlalchemy_api_key.validation_status,
            last_validated_at=sqlalchemy_api_key.last_validated_at,
            provider_metadata=sqlalchemy_api_key.provider_metadata or {},
            created_at=sqlalchemy_api_key.created_at,
            updated_at=sqlalchemy_api_key.updated_at,
        )
    
    @staticmethod
    def to_sqlalchemy(domain_api_key: DomainUserAPIKey) -> SQLAlchemyUserAPIKey:
        """Convert domain UserAPIKey to SQLAlchemy UserAPIKey"""
        return SQLAlchemyUserAPIKey(
            user_id=domain_api_key.user_id,
            provider=domain_api_key.provider,
            encrypted_api_key=domain_api_key.encrypted_api_key,
            validation_status=domain_api_key.validation_status,
            last_validated_at=domain_api_key.last_validated_at,
            provider_metadata=domain_api_key.provider_metadata or {},
            created_at=domain_api_key.created_at,
            updated_at=domain_api_key.updated_at,
        )
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> DomainUserAPIKey:
        """Create domain UserAPIKey from dictionary data"""
        return DomainUserAPIKey(
            user_id=data["user_id"],
            provider=data["provider"],
            encrypted_api_key=data["encrypted_api_key"],
            validation_status=data.get("validation_status", "unknown"),
            last_validated_at=data.get("last_validated_at"),
            provider_metadata=data.get("provider_metadata", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
    
    @staticmethod
    def to_dict(domain_api_key: DomainUserAPIKey) -> Dict[str, Any]:
        """Convert domain UserAPIKey to dictionary"""
        return {
            "user_id": domain_api_key.user_id,
            "provider": domain_api_key.provider,
            "encrypted_api_key": domain_api_key.encrypted_api_key,
            "validation_status": domain_api_key.validation_status,
            "last_validated_at": domain_api_key.last_validated_at,
            "provider_metadata": domain_api_key.provider_metadata,
            "created_at": domain_api_key.created_at,
            "updated_at": domain_api_key.updated_at,
        }