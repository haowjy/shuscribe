# backend/src/api/v1/endpoints/health.py
"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from src.database.connection import get_db_session

router = APIRouter()


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}


@router.get("/status")
async def status(session: AsyncSession = Depends(get_db_session)):
    """Detailed status endpoint with database check"""
    try:
        # Test database connection
        await session.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {e}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "shuscribe-api",
        "version": "0.1.0",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }
