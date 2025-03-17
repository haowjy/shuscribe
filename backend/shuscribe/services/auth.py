# shuscribe/services/auth.py

from typing import Optional
from fastapi import Request

from shuscribe.schemas.auth import User
from shuscribe.auth.client import supabase_auth

class UserService:
    """Service for user operations"""
    
    def __init__(self, request: Request | None = None):
        self.request = request
    
    async def get_token(self) -> Optional[str]:
        """Get the current token from the request context"""
        if not self.request:
            return None
            
        # Extract token from authorization header
        auth_header = self.request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
            
        return auth_header.replace("Bearer ", "")
    
    async def save_user(self, user: User) -> User:
        """Save user changes back to Supabase"""
        token = await self.get_token()
        if not token:
            raise ValueError("No authentication token available")
            
        user_metadata = {
            "display_name": user.display_name,
            "full_name": user.full_name,
            "settings": user.settings
        }
        
        # Update user in Supabase
        await supabase_auth.update_user(token, {"user_metadata": user_metadata})
        return user

# Factory function to get service with request context
async def get_user_service(request: Request) -> UserService:
    return UserService(request)