"""
HTTP Request/Response Schemas

This module aggregates Pydantic models used for defining API endpoint
request and response bodies.
"""

from .documents import (
    CreateDocumentRequest, 
    UpdateDocumentRequest, 
    BulkDocumentRequest, 
    DocumentSearchRequest,
    DocumentContent
)
from .projects import (
    CreateProjectRequest,
    UpdateProjectRequest,
    CreateFileTreeItemRequest,
    UpdateFileTreeItemRequest,
    MoveFileTreeItemRequest,
    ProjectSearchRequest,
    ProjectCollaborator,
    ProjectSettings
)
from .common import (
    PaginationRequest,
    SearchRequest,
    TagRequest,
    BulkOperationRequest,
    ReferenceSearchRequest
)
from .user import (
    APIKeyRequest,
    APIKeyResponse
)
from .llm import (
    ChatCompletionRequest,
    ValidateAPIKeyRequest,
    StoreAPIKeyRequest,
    DeleteAPIKeyRequest,
    ListProvidersRequest,
    ListModelsRequest
)

__all__ = [
    # Document requests
    "CreateDocumentRequest",
    "UpdateDocumentRequest", 
    "BulkDocumentRequest",
    "DocumentSearchRequest",
    "DocumentContent",
    
    # Project requests
    "CreateProjectRequest",
    "UpdateProjectRequest",
    "CreateFileTreeItemRequest",
    "UpdateFileTreeItemRequest",
    "MoveFileTreeItemRequest",
    "ProjectSearchRequest",
    "ProjectCollaborator",
    "ProjectSettings",
    
    # Common requests
    "PaginationRequest",
    "SearchRequest",
    "TagRequest",
    "BulkOperationRequest",
    "ReferenceSearchRequest",
    
    # User requests
    "APIKeyRequest",
    "APIKeyResponse",
    
    # LLM requests
    "ChatCompletionRequest",
    "ValidateAPIKeyRequest",
    "StoreAPIKeyRequest",
    "DeleteAPIKeyRequest",
    "ListProvidersRequest",
    "ListModelsRequest",
]
