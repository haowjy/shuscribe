"""
HTTP Request/Response Schemas

This module aggregates Pydantic models used for defining API endpoint
request and response bodies.
"""

from .user import (
    APIKeyRequest,
    APIKeyResponse
)

__all__ = [
    "APIKeyRequest",
    "APIKeyResponse",
]
