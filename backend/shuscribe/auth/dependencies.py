# /Users/jimmyyao/gitrepos/shuscribe/backend/shuscribe/auth/dependencies.py

from datetime import datetime
from fastapi import Depends, HTTPException, status
from jose import JWTError
from typing import Optional
import uuid

from shuscribe.auth.client import supabase_auth
from shuscribe.schemas.auth import User, TokenData, oauth2_scheme
from shuscribe.services.auth import UserService, get_user_service

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """Get the currently authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the token
        payload = supabase_auth.decode_token(token)
        
        # Extract user info
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        
        token_data = TokenData(
            sub=sub,
            exp=payload.get("exp", 0),
            email=payload.get("email", ""),
            role=payload.get("role", "")
        )
    except (JWTError, ValueError):
        raise credentials_exception
    
    try:
        # Get user details
        user_data = await supabase_auth.get_user(token)
        
        if not user_data:
            raise credentials_exception
        
        # Create User object
        user = User(
            id=uuid.UUID(user_data.get("id")),
            email=user_data.get("email", ""),
            created_at=user_data.get("created_at", datetime.now()),
            last_sign_in_at=user_data.get("last_sign_in_at"),
            display_name=user_data.get("user_metadata", {}).get("display_name"),
            full_name=user_data.get("user_metadata", {}).get("full_name"),
            settings=user_data.get("user_metadata", {}).get("settings", {})
        )
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error retrieving user: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[User]:
    """
    Dependency to get the current user if authenticated, otherwise None.
    
    This allows endpoints to work with both authenticated and unauthenticated users.
    """
    if not token:
        return None
    
    try:
        return await get_current_user(token)
    except HTTPException:
        return None