# shuscribe/auth/dependencies.py

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import uuid
import datetime as dt

from shuscribe.auth.client import supabase_auth
from shuscribe.core.config import get_settings
from shuscribe.schemas.user import User
import logging

logger = logging.getLogger(__name__)

# Custom bearer token extractor
class SupabaseTokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(SupabaseTokenBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials | None = await super(SupabaseTokenBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization code.",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Create an instance
supabase_token_scheme = SupabaseTokenBearer()




async def get_current_user(token: str = Depends(supabase_token_scheme)) -> User:
    """
    Get the current authenticated user using Supabase's built-in verification
    """
    debug_id = uuid.uuid4().hex[:6]
    logger.info(f"[AUTH:{debug_id}] Authentication attempt started")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    logger.info(f"[AUTH:{debug_id}] Token received - First 10 chars: {token[:10] if token else None}...")
    
    try:
        # Continue with Supabase API verification
        user_data = await supabase_auth.get_user(token)
        
        if not user_data:
            logger.error(f"[AUTH:{debug_id}] Failed to get user data from token")
            raise credentials_exception
        
        # Create User object from response
        user = User(
            id=uuid.UUID(user_data.get("id")),
            email=user_data.get("email", ""),
            created_at=user_data.get("created_at", dt.datetime.now()),
            last_sign_in_at=user_data.get("last_sign_in_at"),
            display_name=user_data.get("user_metadata", {}).get("display_name"),
            full_name=user_data.get("user_metadata", {}).get("full_name"),
            settings=user_data.get("user_metadata", {}).get("settings", {})
        )
        
        return user
    except Exception as e:
        logger.error(f"[AUTH:{debug_id}] Authentication error: {str(e)}")
        import traceback
        logger.error(f"[AUTH:{debug_id}] Stack trace: {traceback.format_exc()}")
        raise credentials_exception
    

async def get_optional_user(token: Optional[str] = Depends(supabase_token_scheme)) -> Optional[User]:
    """Get the current user if authenticated, otherwise None"""
    if not token:
        return None
    
    try:
        return await get_current_user(token)
    except HTTPException:
        return None