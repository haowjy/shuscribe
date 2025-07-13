# backend/src/schemas/base.py
"""
Base Pydantic schemas
"""
from datetime import datetime
from typing import Optional, Generic, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode for SQLAlchemy
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields"""
    created_at: datetime
    updated_at: Optional[datetime] = None


class UUIDSchema(BaseSchema):
    """Schema with UUID primary key"""
    id: UUID


class PaginationParams(BaseSchema):
    """Pagination parameters"""
    page: int = 1
    page_size: int = Field(default=20)
    
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseSchema):
    """Paginated response wrapper"""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(cls, items: list, total: int, pagination: PaginationParams):
        total_pages = (total + pagination.page_size - 1) // pagination.page_size
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )


# Type variable for generic response wrapper
T = TypeVar('T')


class ApiResponse(BaseSchema, Generic[T]):
    """API response wrapper matching frontend ApiResponse<T> interface"""
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None
    status: int
    
    @classmethod
    def success(cls, data: T, message: Optional[str] = None, status: int = 200):
        """Create successful response"""
        return cls(data=data, error=None, message=message, status=status)
    
    @classmethod
    def create_error(cls, error: str, message: Optional[str] = None, status: int = 400):
        """Create error response"""
        return cls(data=None, error=error, message=message, status=status)


class ApiError(BaseSchema):
    """API error response matching frontend ApiError interface"""
    error: str
    message: str
    details: Optional[dict] = None
    request_id: Optional[str] = None