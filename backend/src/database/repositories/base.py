# backend/src/database/repositories/base.py
"""
Base repository for common CRUD operations
"""
from typing import Any, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select


ModelType = TypeVar("ModelType", bound=Any)


class BaseRepository(Generic[ModelType]):
    """
    Base repository class for common database operations.
    """
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get(self, id: UUID) -> Optional[ModelType]:
        """Retrieve a single record by its ID."""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_multi(self, *, offset: int = 0, limit: int = 100) -> List[ModelType]:
        """Retrieve multiple records with pagination."""
        stmt = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def create(self, obj_in: dict) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        """Update an existing record."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def delete(self, db_obj: ModelType) -> None:
        """Delete a record."""
        await self.session.delete(db_obj)
        await self.session.commit()