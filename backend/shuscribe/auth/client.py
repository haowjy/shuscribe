# /Users/jimmyyao/gitrepos/shuscribe/backend/shuscribe/auth/client.py

from supabase import create_client, Client
from shuscribe.core.config import get_settings
from functools import lru_cache
import httpx
import logging

logger = logging.getLogger(__name__)

@lru_cache()
def get_supabase_client() -> Client:
    """Create a cached Supabase client"""
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

@lru_cache()
def get_supabase_admin_client() -> Client:
    """Create a cached Supabase admin client with service role key"""
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

class SupabaseAuthClient:
    """Client for Supabase Auth Operations"""
    
    async def get_user(self, token: str):
        """Get user details from a JWT token"""
        settings = get_settings()
        
        try:
            logger.info(f"Attempting to get user with token starting with: {token[:10]}...")
            
            # URL is now properly formatted with https:// from environment variables
            url = f"{settings.SUPABASE_URL}/auth/v1/user"
            
            logger.info(f"Making request to URL: {url}")
            
            headers = {
                "apikey": settings.SUPABASE_KEY,
                "Authorization": f"Bearer {token}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                
                logger.info(f"Response status: {response.status_code}")
                
                if response.status_code >= 400:
                    logger.error(f"Error response body: {response.text}")
                    return None
                    
                return response.json()
        except Exception as e:
            logger.error(f"Exception in get_user: {str(e)}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return None

# Create a global instance
supabase_auth = SupabaseAuthClient()