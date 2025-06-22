# backend/src/core/exceptions.py
"""
Custom application exceptions
"""
from typing import Any, Dict, Optional


class ShuScribeException(Exception):
    """Base exception for ShuScribe application"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(ShuScribeException):
    """Raised when validation fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=400)


class NotFoundError(ShuScribeException):
    """Raised when a resource is not found"""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, status_code=404)


class AuthenticationError(ShuScribeException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(ShuScribeException):
    """Raised when authorization fails"""
    
    def __init__(self, message: str = "Not authorized to perform this action"):
        super().__init__(message, status_code=403)


class ProcessingError(ShuScribeException):
    """Raised when story processing fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=422)


class LLMError(ShuScribeException):
    """Raised when LLM operations fail"""
    
    def __init__(self, provider: str, message: str, details: Optional[Dict[str, Any]] = None):
        full_message = f"LLM Error ({provider}): {message}"
        super().__init__(full_message, details, status_code=502)