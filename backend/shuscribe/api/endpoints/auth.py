# shuscribe/api/endpoints/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Body
import httpx

from shuscribe.core.config import get_settings
from shuscribe.schemas.user import User, UserUpdate
from shuscribe.auth.dependencies import get_current_user, supabase_token_scheme

router = APIRouter()

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get information about the currently authenticated user"""
    return current_user

@router.patch("/me", response_model=User)
async def update_user_profile(
    update_data: UserUpdate = Body(...),
    current_user: User = Depends(get_current_user),
    token: str = Depends(supabase_token_scheme)
):
    """Update the current user's profile information"""
    settings = get_settings()
    
    # Update user metadata in Supabase Auth
    update_metadata = {}
    
    if update_data.display_name is not None:
        update_metadata["display_name"] = update_data.display_name
    
    if update_data.full_name is not None:
        update_metadata["full_name"] = update_data.full_name
    
    if update_data.settings is not None:
        # Merge with existing settings rather than replacing
        merged_settings = {**current_user.settings, **update_data.settings}
        update_metadata["settings"] = merged_settings
    
    if update_metadata:
        try:
            # Use the standard user update endpoint
            url = f"{settings.SUPABASE_URL}/auth/v1/user"
            headers = {
                "apikey": settings.SUPABASE_KEY,
                "Authorization": f"Bearer {token}"
            }
            payload = {
                "data": update_metadata  # Note: the key is "data" not "user_metadata"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.put(url, headers=headers, json=payload)
                
                if response.status_code >= 400:
                    raise Exception(f"Supabase API error: {response.status_code} - {response.text}")
                
                user_data = response.json()
            
            # Update the current user object with new data from the response
            updated_user = current_user.copy(update={
                "display_name": user_data.get("user_metadata", {}).get("display_name", current_user.display_name),
                "full_name": user_data.get("user_metadata", {}).get("full_name", current_user.full_name),
                "settings": user_data.get("user_metadata", {}).get("settings", current_user.settings)
            })
            
            return updated_user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user profile: {str(e)}"
            )
    
    return current_user