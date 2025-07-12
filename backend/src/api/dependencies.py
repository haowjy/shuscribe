# backend/src/api/dependencies.py
"""
FastAPI dependencies for authentication and authorization
"""
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status, Depends

from src.services.auth.supabase_auth import get_supabase_auth_service


async def get_auth_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Extract authentication token from Authorization header
    
    This is a simple token extraction that doesn't validate the token.
    Use require_auth() or get_optional_user_context() for token validation.
    """
    if not authorization:
        return None
    
    if not authorization.startswith("Bearer "):
        return None
    
    return authorization[7:]  # Remove "Bearer " prefix


async def get_current_user_context(token: Optional[str] = None) -> dict:
    """
    Get current user context from token
    
    Note: This is a simple wrapper that doesn't validate the token.
    Use require_auth() or get_optional_user_context() for proper JWT validation.
    """
    return {
        "token": token,
        "authenticated": token is not None,
    }


async def require_auth(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Require authentication - validates Supabase JWT token locally and returns user context
    
    Uses fast local JWT validation (< 1ms) instead of API calls to Supabase.
    Validates token signature, expiration, and audience claims.
    
    Use this dependency when an endpoint requires authentication.
    
    Returns:
        Dict containing user information: {
            'user_id': str,
            'email': str, 
            'token': str,
            'authenticated': bool,
            'expires_at': datetime,
            'metadata': dict
        }
    
    Raises:
        HTTPException: If token is missing, invalid, expired, or has invalid signature
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token required"
        )
    
    # Validate token locally using JWT validation and get user context
    auth_service = get_supabase_auth_service()
    user_context = await auth_service.validate_token(token)
    
    return user_context


async def get_optional_user_context(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Get user context if available, but don't require authentication
    
    Use this dependency when an endpoint can work with or without authentication.
    
    Returns:
        Dict containing user information if token is valid, or minimal context if not:
        - With valid token: Same as require_auth()
        - Without token: {'authenticated': False, 'user_id': None, 'email': None}
    """
    if not authorization or not authorization.startswith("Bearer "):
        return {
            'authenticated': False,
            'user_id': None,
            'email': None,
            'token': None,
            'metadata': {}
        }
    
    token = authorization[7:]  # Remove "Bearer " prefix
    if not token:
        return {
            'authenticated': False,
            'user_id': None,
            'email': None,
            'token': None,
            'metadata': {}
        }
    
    try:
        # Try to validate token locally using JWT validation
        auth_service = get_supabase_auth_service()
        user_context = await auth_service.validate_token(token)
        return user_context
    except HTTPException:
        # Token is invalid, but that's OK for optional auth
        return {
            'authenticated': False,
            'user_id': None,
            'email': None,
            'token': token,  # Keep token for logging purposes
            'metadata': {}
        }


async def get_current_user_id(user_context: Dict[str, Any] = Depends(require_auth)) -> str:
    """
    Extract user ID from authenticated user context.
    
    Use this dependency when you only need the user ID for database operations.
    This dependency requires authentication (uses require_auth internally).
    
    Args:
        user_context: User context from require_auth dependency
        
    Returns:
        str: The authenticated user's ID
    """
    return user_context['user_id']


async def get_optional_user_id(user_context: Dict[str, Any] = Depends(get_optional_user_context)) -> Optional[str]:
    """
    Extract user ID from optional user context.
    
    Use this dependency when you need the user ID but authentication is optional.
    
    Args:
        user_context: User context from get_optional_user_context dependency
        
    Returns:
        str | None: The user's ID if authenticated, None otherwise
    """
    return user_context.get('user_id')