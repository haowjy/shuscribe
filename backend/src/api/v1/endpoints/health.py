# backend/src/api/v1/endpoints/health.py
"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime
from src.config import settings
from src.database.supabase_connection import get_supabase_client

router = APIRouter()


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}


@router.get("/status")
async def status():
    """Detailed status endpoint with database check"""
    if settings.SKIP_DATABASE:
        db_status = "skipped (in-memory mode)"
    else:
        try:
            # Test Supabase connection
            client = get_supabase_client()
            client.table('users').select('id').limit(1).execute()
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {e}"
    
    return {
        "status": "healthy" if db_status in ["healthy", "skipped (in-memory mode)"] else "degraded",
        "service": "shuscribe-api",
        "version": "0.1.0",
        "database": db_status,
        "database_type": "supabase" if not settings.SKIP_DATABASE else "in-memory",
        "timestamp": datetime.utcnow().isoformat()
    }
