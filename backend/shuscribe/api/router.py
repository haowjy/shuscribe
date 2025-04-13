# shuscribe/api/router.py

from fastapi import APIRouter, Depends

from shuscribe.api.endpoints.llm import router as llm_router
from shuscribe.api.endpoints.auth import router as auth_router
from shuscribe.api.endpoints.pipeline import router as pipeline_router
from shuscribe.auth.dependencies import get_current_user
from shuscribe.schemas.user import User

api_router = APIRouter()

# Include existing routers
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(llm_router, prefix="/llm", tags=["llm"])
api_router.include_router(pipeline_router, prefix="/llm", tags=["pipeline"])

# Root endpoint for API
@api_router.get("/")
async def api_root():
    return {
        "message": "ShuScribe API is running",
        "endpoints": {
            "auth": "/api/auth",
            "llm": "/api/llm"
        }
    }

# Test authentication endpoint at API root level
@api_router.get("/whoami", summary="Test current authenticated user")
async def whoami(current_user: User = Depends(get_current_user)):
    """
    Test endpoint to verify user authentication is working correctly
    """
    return {
        "authenticated": True,
        "user_id": str(current_user.id),
        "email": current_user.email,
        "display_name": current_user.display_name or "Not set"
    }

# Public test endpoint
@api_router.get("/test", summary="Public test endpoint")
async def test():
    return {"message": "Public test endpoint - no authentication required"}