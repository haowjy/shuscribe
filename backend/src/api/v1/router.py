# backend/src/api/v1/router.py
"""
Main API router for v1 endpoints
"""
from fastapi import APIRouter

from src.api.v1.endpoints import health, projects, documents, llm

# Create the main router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(llm.router, prefix="/llm", tags=["llm"])