# backend/src/api/v1/router.py
"""
Main API router for v1 endpoints
"""
from fastapi import APIRouter

from src.api.v1.endpoints import health
from src.api.v1.endpoints import llm

# Create the main router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
# CHANGED TAG:
api_router.include_router(llm.router, prefix="/llm", tags=["LLM Catalog & Config"])

# TODO: Add other routers as we build them
# api_router.include_router(stories.router, prefix="/stories", tags=["stories"])
# api_router.include_router(wiki.router, prefix="/wiki", tags=["wiki"])
# api_router.include_router(progress.router, prefix="/progress", tags=["progress"])