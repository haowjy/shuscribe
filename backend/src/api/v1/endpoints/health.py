# backend/src/api/v1/endpoints/health.py
"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime, UTC
from src.config import settings
from src.database.factory import get_repositories, is_initialized
from src.database.connection import health_check

router = APIRouter()


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}


@router.get("/status")
async def status():
    """Detailed status endpoint with database check"""
    # Determine actual backend in use
    configured_backend = settings.DATABASE_BACKEND
    actual_backend = "unknown"
    db_status = "unknown"
    
    try:
        # Check if repositories are initialized and what type they are
        if not is_initialized():
            db_status = "uninitialized"
            actual_backend = "none"
        else:
            repos = get_repositories()
            # Check if we're using database or memory repositories
            from src.database.repositories import DatabaseProjectRepository, MemoryProjectRepository
            
            if isinstance(repos.project, DatabaseProjectRepository):
                actual_backend = "database"
                # Test database connectivity using existing health check function
                try:
                    is_healthy = await health_check()
                    if is_healthy:
                        db_status = "healthy"
                    else:
                        db_status = "unhealthy: database connection failed"
                except Exception as e:
                    db_status = f"unhealthy: {e}"
                    
            elif isinstance(repos.project, MemoryProjectRepository):
                actual_backend = "memory"
                if configured_backend == "memory":
                    db_status = "healthy (memory mode)"
                else:
                    db_status = "healthy (memory fallback)"
            else:
                db_status = "unknown repository type"
                
    except Exception as e:
        db_status = f"error checking repositories: {e}"
    
    return {
        "status": db_status,
        "service": "shuscribe-api",
        "version": "0.1.0",
        "database": db_status,
        "database_type": actual_backend,
        "configured_backend": configured_backend,
        "timestamp": datetime.now(UTC).isoformat()
    }
