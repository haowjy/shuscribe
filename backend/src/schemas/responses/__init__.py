"""
Response schemas for all API endpoints
"""
from .documents import (
    DocumentContent,
    DocumentMeta,
    DocumentResponse,
    DocumentReference,
    DocumentListResponse,
    DocumentSearchResponse,
    DeleteResponse,
    BulkOperationResponse
)
from .projects import (
    ProjectCollaborator,
    ProjectSettings,
    ProjectDetails,
    ProjectSummary,
    FileTreeItemResponse,
    FileTreeMetadata,
    FileTreeResponse,
    ProjectListResponse,
    ProjectSearchResponse,
    ProjectStatsResponse
)
from .common import (
    PaginatedResponse,
    SuccessResponse,
    ErrorResponse,
    ValidationErrorResponse,
    TagResponse,
    ReferenceSearchResponse,
    HealthCheckResponse,
    MetricsResponse
)
from .writing import (
    SearchAllResult,
    TaggedContentResult
)
from .llm import (
    ChatCompletionResponse,
    ChatCompletionStreamChunk,
    APIKeyValidationResponse,
    StoredAPIKeyResponse,
    ModelCapabilityResponse,
    ProviderResponse,
    ListProvidersResponse,
    ListModelsResponse,
    DeleteAPIKeyResponse,
    ListUserAPIKeysResponse,
    LLMUsageStatsResponse
)

__all__ = [
    # Document responses
    "DocumentContent",
    "DocumentMeta",
    "DocumentResponse",
    "DocumentReference",
    "DocumentListResponse",
    "DocumentSearchResponse",
    "DeleteResponse",
    "BulkOperationResponse",
    
    # Project responses
    "ProjectCollaborator",
    "ProjectSettings",
    "ProjectDetails",
    "ProjectSummary",
    "FileTreeItemResponse",
    "FileTreeMetadata",
    "FileTreeResponse",
    "ProjectListResponse",
    "ProjectSearchResponse",
    "ProjectStatsResponse",
    
    # Common responses
    "PaginatedResponse",
    "SuccessResponse",
    "ErrorResponse",
    "ValidationErrorResponse",
    "TagResponse",
    "ReferenceSearchResponse",
    "HealthCheckResponse",
    "MetricsResponse",
    
    # Writing responses
    "SearchAllResult",
    "TaggedContentResult",
    
    # LLM responses
    "ChatCompletionResponse",
    "ChatCompletionStreamChunk",
    "APIKeyValidationResponse",
    "StoredAPIKeyResponse",
    "ModelCapabilityResponse",
    "ProviderResponse",
    "ListProvidersResponse",
    "ListModelsResponse",
    "DeleteAPIKeyResponse",
    "ListUserAPIKeysResponse",
    "LLMUsageStatsResponse",
]