"""
Supabase authentication service using the new API key system (2025+)
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, UTC

from fastapi import HTTPException, status
from supabase import create_client, Client

from src.config import settings
from src.core.exceptions import ShuScribeException

logger = logging.getLogger(__name__)


class SupabaseAuthService:
    """
    Service for validating Supabase authentication tokens using the new API key system (2025+).
    
    Uses Supabase's built-in auth.getUser() for reliable token validation with the new secret key.
    """
    
    def __init__(self):
        """Initialize the auth service with Supabase client using new secret key."""
        if not settings.SUPABASE_URL or settings.SUPABASE_URL == "https://your-project.supabase.co":
            raise ShuScribeException(
                "SUPABASE_URL must be configured. "
                "Set it in your environment variables."
            )
        
        if not settings.supabase_secret_key or settings.supabase_secret_key == "your-service-key-here":
            raise ShuScribeException(
                "SUPABASE_SECRET_KEY must be configured for server-side operations. "
                "Get the new 'sb_secret_*' key from Supabase Dashboard > Settings > API"
            )
        
        # Create Supabase client with new secret key for server-side operations
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.supabase_secret_key
        )
        
        logger.info("SupabaseAuthService initialized with new API key system (sb_secret_*)")
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a Supabase authentication token using auth.getUser().
        
        Uses Supabase's recommended auth.getUser() method with the new secret key system.
        
        Args:
            token: The authentication token from the Authorization header
            
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
            HTTPException: If token is invalid, expired, or malformed
        """
        try:
            # Use Supabase's built-in token validation with new secret key
            response = self.supabase.auth.get_user(token)
            
            if not response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )
            
            user = response.user
            
            # Extract user information
            user_id = user.id
            email = user.email or ""
            
            # Note: Session information not directly available in UserResponse
            # expires_at can be calculated from JWT if needed, but not required for basic auth
            expires_at = None
            
            # Build user context
            user_context = {
                'user_id': user_id,
                'email': email,
                'token': token,
                'authenticated': True,
                'expires_at': expires_at,
                'metadata': {
                    'role': user.role or 'authenticated',
                    'email_verified': user.email_confirmed_at is not None,
                    'phone_verified': user.phone_confirmed_at is not None,
                    'user_metadata': user.user_metadata or {},
                    'app_metadata': user.app_metadata or {},
                    'created_at': user.created_at,
                    'updated_at': user.updated_at,
                    'last_sign_in_at': user.last_sign_in_at,
                    'session_id': None,  # Session info not available in UserResponse
                }
            }
            
            logger.debug(f"Successfully validated token for user {user_id} ({email})")
            return user_context
            
        except Exception as e:
            logger.warning(f"Token validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
    
    def validate_token_sync(self, token: str) -> Dict[str, Any]:
        """
        Synchronous version of validate_token for non-async contexts.
        
        Args:
            token: The authentication token to validate
            
        Returns:
            Dict containing user information (same as validate_token)
            
        Raises:
            HTTPException: If token is invalid, expired, or malformed
        """
        try:
            # Use Supabase's built-in token validation with new secret key
            response = self.supabase.auth.get_user(token)
            
            if not response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )
            
            user = response.user
            user_id = user.id
            email = user.email or ""
            
            # Note: Session information not directly available in UserResponse
            # expires_at can be calculated from JWT if needed, but not required for basic auth
            expires_at = None
            
            user_context = {
                'user_id': user_id,
                'email': email,
                'token': token,
                'authenticated': True,
                'expires_at': expires_at,
                'metadata': {
                    'role': user.role or 'authenticated',
                    'email_verified': user.email_confirmed_at is not None,
                    'phone_verified': user.phone_confirmed_at is not None,
                    'user_metadata': user.user_metadata or {},
                    'app_metadata': user.app_metadata or {},
                    'created_at': user.created_at,
                    'updated_at': user.updated_at,
                    'last_sign_in_at': user.last_sign_in_at,
                    'session_id': None,  # Session info not available in UserResponse
                }
            }
            
            return user_context
            
        except Exception as e:
            logger.warning(f"Token validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )


# Global instance for dependency injection
_supabase_auth_service: Optional[SupabaseAuthService] = None


def get_supabase_auth_service() -> SupabaseAuthService:
    """Get the global Supabase auth service instance."""
    global _supabase_auth_service
    if _supabase_auth_service is None:
        _supabase_auth_service = SupabaseAuthService()
    return _supabase_auth_service