"""
Common response schemas used across multiple API endpoints
"""
from typing import List, Optional, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field

from src.schemas.base import BaseSchema

T = TypeVar('T')


class PaginatedResponse(BaseSchema, Generic[T]):
    """Standard paginated response"""
    model_config = {"populate_by_name": True}
    
    data: List[T]
    pagination: Dict[str, Any] = Field(default_factory=lambda: {
        "total": 0,
        "limit": 20,
        "offset": 0,
        "has_more": False,
        "next_offset": None
    })
    
    @classmethod
    def create(cls, data: List[T], total: int, limit: int, offset: int):
        """Create paginated response with calculated pagination info"""
        has_more = offset + limit < total
        next_offset = offset + limit if has_more else None
        
        return cls(
            data=data,
            pagination={
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": has_more,
                "next_offset": next_offset
            }
        )


class SuccessResponse(BaseSchema):
    """Standard success response"""
    model_config = {"populate_by_name": True}
    
    success: bool = True
    message: str


class ErrorResponse(BaseSchema):
    """Standard error response"""
    model_config = {"populate_by_name": True}
    
    success: bool = False
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


class ValidationErrorResponse(BaseSchema):
    """Validation error response"""
    model_config = {"populate_by_name": True}
    
    success: bool = False
    error: str = "validation_error"
    message: str
    field_errors: Dict[str, List[str]] = Field(default_factory=dict)


class TagResponse(BaseSchema):
    """Tag operation response"""
    model_config = {"populate_by_name": True}
    
    success: bool
    message: str
    tags: List[str] = Field(default_factory=list)


class ReferenceSearchResponse(BaseSchema):
    """Response for @-reference search"""
    model_config = {"populate_by_name": True}
    
    results: List[Dict[str, Any]] = Field(default_factory=list)
    total: int
    query: str
    limit: int
    has_more: bool


class HealthCheckResponse(BaseSchema):
    """Health check response"""
    model_config = {"populate_by_name": True}
    
    status: str  # 'healthy' | 'unhealthy'
    timestamp: str
    version: str
    services: Dict[str, str] = Field(default_factory=dict)  # service_name -> status


class MetricsResponse(BaseSchema):
    """Metrics response"""
    model_config = {"populate_by_name": True}
    
    total_requests: int
    average_response_time: float
    error_rate: float
    uptime: str