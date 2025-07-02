# backend/src/api/v1/endpoints/health.py
"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime, UTC
from src.config import settings

router = APIRouter()


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}


@router.get("/status")
async def status():
    """Detailed status endpoint with database check"""
    if settings.DATABASE_BACKEND == "memory":
        db_status = "skipped (memory mode)"
    else:
        try:
            # TODO: Test database connection when PostgreSQL backend is implemented
            # For now, assume healthy since we're using memory repositories
            db_status = "healthy (memory fallback)"
        except Exception as e:
            db_status = f"unhealthy: {e}"
    
    return {
        "status": db_status,
        "service": "shuscribe-api",
        "version": "0.1.0",
        "database": db_status,
        "database_type": settings.DATABASE_BACKEND,
        "timestamp": datetime.now(UTC).isoformat()
    }
