# shuscribe/api/endpoints/auth.py

from datetime import datetime
import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, Dict, Any

from shuscribe.auth.client import supabase_auth
from shuscribe.schemas.auth import User, UserCreate, UserUpdate, Token
from shuscribe.auth.dependencies import get_current_user
from shuscribe.services.auth import UserService, get_user_service

router = APIRouter()

@router.post("/signup", response_model=User)
async def signup(user_create: UserCreate):  # Changed variable name here
    try:
        # Create user in Supabase
        response = await supabase_auth.sign_up(
            email=user_create.email,
            password=user_create.password,
            user_data={
                "display_name": user_create.display_name,
                "full_name": user_create.full_name,
                "settings": {}
            }
        )
        
        # Check for errors
        if "error" in response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response["error"]["message"]
            )
        
        # Extract user from response - using a different variable name
        user_data = response.get("user", {})  # This is now a new variable, not overwriting anything
        
        # Create User object
        user = User(
            id=user_data.get("id"),
            email=user_data.get("email"),
            created_at=user_data.get("created_at"),
            display_name=user_data.get("user_metadata", {}).get("display_name"),
            full_name=user_data.get("user_metadata", {}).get("full_name"),
            settings=user_data.get("user_metadata", {}).get("settings", {})
        )
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    try:
        # Sign in with Supabase
        response = await supabase_auth.sign_in(
            email=form_data.username,  # OAuth2 uses username field for email
            password=form_data.password
        )
        
        # Check for errors
        if "error" in response:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract token
        access_token = response.get("access_token")
        
        return Token(
            access_token=access_token or "",
            token_type="bearer"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get information about the currently authenticated user"""
    return current_user

@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update the current user's information"""
    try:
        # Update user fields
        if user_update.display_name is not None:
            current_user.display_name = user_update.display_name
            
        if user_update.full_name is not None:
            current_user.full_name = user_update.full_name
            
        if user_update.settings is not None:
            # Merge settings instead of replacing
            current_user.settings.update(user_update.settings)
            
        # Save changes using the service
        await user_service.save_user(current_user)
        
        return current_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update user: {str(e)}"
        )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str):
    """Refresh an access token using a refresh token"""
    try:
        response = await supabase_auth.refresh_token(refresh_token)
        
        # Check for errors
        if "error" in response:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract new token
        access_token = response.get("access_token", "")
        
        return Token(
            access_token=access_token,
            token_type="bearer"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )