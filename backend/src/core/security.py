# backend/src/core/security.py
"""
Authentication and authorization using Supabase
"""
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
from typing import Optional

from src.config import settings
from src.core.exceptions import AuthenticationError

security = HTTPBearer()

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UUID:
    """Extract user ID from Supabase JWT token"""
    try:
        # Decode JWT token from Supabase
        payload = jwt.decode(
            credentials.credentials,
            # You'll need Supabase's public key here
            options={"verify_signature": False}  # For now - fix in production
        )
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token: no user ID")
        return UUID(user_id)
    except Exception as e:
        raise AuthenticationError(f"Invalid token: {e}")