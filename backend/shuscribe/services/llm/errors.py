from typing import Optional, Dict, Any, List
import time
from enum import Enum
from pydantic import BaseModel, Field

class ErrorCategory(str, Enum):
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    CONTEXT_LENGTH = "context_length"
    CONTENT_FILTER = "content_filter"
    MODEL_ERROR = "model_error"
    INVALID_REQUEST = "invalid_request"
    SERVICE_ERROR = "service_error"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


class RetryConfig(BaseModel):
    enabled: bool = Field(default=False, description="Whether retries are enabled")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    min_delay: float = Field(default=1.0, description="Minimum delay between retries in seconds")
    max_delay: float = Field(default=30.0, description="Maximum delay between retries in seconds")
    backoff_factor: float = Field(default=2.0, description="Exponential backoff multiplier")
    retry_on: List[ErrorCategory] = Field(
        default_factory=lambda: [
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.SERVICE_ERROR,
            ErrorCategory.NETWORK_ERROR
        ],
        description="Error categories to retry on"
    )
    
    
class LLMProviderException(Exception):
    """Base exception for all LLM provider errors"""
    
    def __init__(
        self,
        message: str,
        code: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        provider: str = "unknown",
        retry_after: Optional[float] = None,
        raw_error: Optional[Any] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.category = category
        self.provider = provider
        self.retry_after = retry_after
        self.raw_error = raw_error
        self.request_id = request_id
        self.details = details or {}
        self.timestamp = time.time()
        
        super().__init__(message)
    
    def is_retryable(self) -> bool:
        """Determine if this error can be retried"""
        return self.category in [
            ErrorCategory.RATE_LIMIT, 
            ErrorCategory.SERVICE_ERROR,
            ErrorCategory.NETWORK_ERROR
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to a dictionary for API responses"""
        return {
            "message": self.message,
            "code": self.code,
            "category": self.category,
            "provider": self.provider,
            "retry_after": self.retry_after,
            "request_id": self.request_id,
            "details": self.details,
            "timestamp": self.timestamp
        }

# Specific exception classes
class AuthenticationError(LLMProviderException):
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            code="authentication_error",
            category=ErrorCategory.AUTHENTICATION,
            **kwargs
        )

class RateLimitError(LLMProviderException):
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            code="rate_limit_exceeded",
            category=ErrorCategory.RATE_LIMIT,
            **kwargs
        )
