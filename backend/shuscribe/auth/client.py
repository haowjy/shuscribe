# /Users/jimmyyao/gitrepos/shuscribe/backend/shuscribe/auth/client.py

import httpx
from jose import jwt
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from shuscribe.core.config import settings

logger = logging.getLogger(__name__)

class SupabaseAuthClient:
    """Client for interacting with Supabase Auth"""
    
    def __init__(self):
        self.base_url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.jwt_secret = settings.SUPABASE_JWT_SECRET
        
    async def sign_up(self, email: str, password: str, user_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Register a new user"""
        url = f"{self.base_url}/auth/v1/signup"
        
        headers = {
            "apikey": self.key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "email": email,
            "password": password,
            "data": user_data or {}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code >= 400:
                logger.error(f"Failed to sign up user: {response.text}")
                response.raise_for_status()
                
            return response.json()
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in a user with email and password"""
        url = f"{self.base_url}/auth/v1/token?grant_type=password"
        
        headers = {
            "apikey": self.key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "email": email,
            "password": password
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code >= 400:
                logger.error(f"Failed to sign in user: {response.text}")
                response.raise_for_status()
                
            return response.json()
    
    async def get_user(self, token: str) -> Dict[str, Any]:
        """Get user details from token"""
        url = f"{self.base_url}/auth/v1/user"
        
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {token}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code >= 400:
                logger.error(f"Failed to get user: {response.text}")
                response.raise_for_status()
                
            return response.json()
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and verify a JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.SUPABASE_JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except Exception as e:
            logger.error(f"Failed to decode token: {str(e)}")
            raise ValueError("Invalid token")
    
    async def update_user(self, token: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user data"""
        url = f"{self.base_url}/auth/v1/user"
        
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=user_data, headers=headers)
            
            if response.status_code >= 400:
                logger.error(f"Failed to update user: {response.text}")
                response.raise_for_status()
                
            return response.json()
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an access token"""
        url = f"{self.base_url}/auth/v1/token?grant_type=refresh_token"
        
        headers = {
            "apikey": self.key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "refresh_token": refresh_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code >= 400:
                logger.error(f"Failed to refresh token: {response.text}")
                response.raise_for_status()
                
            return response.json()

# Create a global client instance
supabase_auth = SupabaseAuthClient()