# backend/src/database/connection.py
"""
Database connection and session management for Supabase + SQLAlchemy
"""
import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from src.config import settings
from src.database.models import Base

logger = logging.getLogger(__name__)

# Global engine and session factory
engine = None
async_session_factory = None


def get_database_url() -> str:
    """Get the database URL for Supabase connection"""
    if settings.DATABASE_BACKEND == "memory":
        # In-memory SQLite for testing
        return "sqlite+aiosqlite:///:memory:"
    
    # Use Supabase PostgreSQL
    supabase_url = settings.SUPABASE_URL
    if not supabase_url or supabase_url == "https://your-project.supabase.co":
        logger.warning("SUPABASE_URL not configured, falling back to local PostgreSQL")
        return settings.DATABASE_URL
    
    # Extract project ID from Supabase URL
    # Format: https://[project-id].supabase.co
    project_id = supabase_url.replace("https://", "").replace(".supabase.co", "")
    
    # Use service key for backend connections (not anon key)
    # If no service key, use the anon key (less secure but works for development)
    db_password = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
    
    # Construct PostgreSQL connection string for Supabase
    return f"postgresql+asyncpg://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres"


def init_database() -> None:
    """Initialize database engine and session factory"""
    global engine, async_session_factory
    
    database_url = get_database_url()
    logger.info(f"Initializing database connection to: {database_url.split('@')[0]}@[REDACTED]")
    
    # Create async engine
    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,  # Log SQL queries in debug mode
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,   # Recycle connections every hour
    )
    
    # Create session factory
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    logger.info("Database connection initialized successfully")


async def create_tables() -> None:
    """Create all tables (no migrations approach)"""
    if not engine:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    try:
        async with engine.begin() as conn:
            # Drop all tables first (for development)
            await conn.run_sync(Base.metadata.drop_all)
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session
    Use this in FastAPI endpoints as a dependency
    """
    if not async_session_factory:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database session
    Use this in repository classes or service functions
    """
    if not async_session_factory:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_database() -> None:
    """Close database connection"""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")


async def health_check() -> bool:
    """Check if database connection is healthy"""
    if not engine:
        return False
    
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


# Helper function for repositories that need manual session management
def get_session_factory() -> Optional[async_sessionmaker[AsyncSession]]:
    """Get the session factory for manual session management"""
    return async_session_factory