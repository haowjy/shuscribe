# backend/src/database/connection.py
"""
Database connection and session management for Supabase + SQLAlchemy
"""
import logging
from typing import AsyncGenerator, Optional, Dict, Any
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
    """Get the database URL for connection"""
    if settings.DATABASE_BACKEND == "memory":
        # In-memory SQLite for testing
        return "sqlite+aiosqlite:///:memory:"
    
    # Use configured DATABASE_URL directly (it already has the correct credentials)
    return settings.DATABASE_URL


def init_database() -> None:
    """Initialize database engine and session factory"""
    global engine, async_session_factory
    
    database_url = get_database_url()
    logger.info(f"Initializing database connection to: {database_url.split('@')[0]}@[REDACTED]")
    logger.debug(f"Database backend: {settings.DATABASE_BACKEND}")
    logger.debug(f"Full database URL (password redacted): {database_url.replace(database_url.split('@')[0].split(':')[-1], '[REDACTED]')}")
    
    try:
        # Create async engine with configurable timeouts
        connect_args = {}
        if database_url.startswith("postgresql"):
            connect_args = {
                "command_timeout": settings.DATABASE_COMMAND_TIMEOUT,
                "server_settings": {
                    "application_name": "shuscribe_backend",
                    "jit": "off"  # Disable JIT for better connection stability
                }
            }
        
        engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,  # Log SQL queries in debug mode
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,   # Recycle connections every hour
            pool_timeout=settings.DATABASE_POOL_TIMEOUT,  # Timeout for getting connection from pool
            pool_size=settings.DATABASE_POOL_SIZE,  # Base number of connections in pool
            max_overflow=settings.DATABASE_MAX_OVERFLOW,  # Additional connections beyond pool_size
            pool_reset_on_return='commit',  # Ensure clean connections on return to pool
            connect_args=connect_args
        )
        
        # Create session factory
        async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        logger.info("Database connection initialized successfully")
        logger.info(f"Connection pool configured: size={settings.DATABASE_POOL_SIZE}, max_overflow={settings.DATABASE_MAX_OVERFLOW}, total_max={settings.DATABASE_POOL_SIZE + settings.DATABASE_MAX_OVERFLOW}")
        
    except Exception as e:
        logger.error(f"Failed to initialize database engine: {e}")
        logger.error(f"Error type: {type(e)}")
        raise


async def create_tables(drop_existing: bool = False) -> None:
    """
    Create all tables (no migrations approach)
    
    Args:
        drop_existing: If True, drop existing tables first. Use with caution!
    """
    if not engine:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    logger.info("Starting table creation process...")
    logger.debug(f"Table prefix configured: '{settings.table_prefix}'")
    
    try:
        logger.info("Attempting to connect to database for table creation...")
        async with engine.begin() as conn:
            if drop_existing:
                logger.warning("Dropping existing tables (drop_existing=True)...")
                await conn.run_sync(Base.metadata.drop_all)
                logger.info("Existing tables dropped")
            
            logger.info("Creating tables if they don't exist...")
            # Create all tables (this is idempotent - won't recreate existing tables)
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Tables created/verified successfully")
        
        logger.info("Database tables initialization completed")
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error during table creation: {e}")
        logger.error(f"Error type: {type(e)}")
        raise
    except TimeoutError as e:
        logger.error(f"Database operation timed out during table creation: {e}")
        logger.error("This may be due to network issues or Supabase connectivity problems.")
        logger.error("Consider increasing DATABASE_COMMAND_TIMEOUT in your .env file.")
        logger.error("For WSL2 users: Check IPv6 connectivity and DNS resolution.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during table creation: {e}")
        logger.error(f"Error type: {type(e)}")
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


async def get_pool_status() -> Dict[str, Any]:
    """Get detailed connection pool status for monitoring"""
    if not engine:
        return {"status": "not_initialized", "pool": None}
    
    try:
        pool = engine.pool
        return {
            "status": "healthy",
            "pool": {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "configured_size": settings.DATABASE_POOL_SIZE,
                "max_overflow": settings.DATABASE_MAX_OVERFLOW,
                "total_max": settings.DATABASE_POOL_SIZE + settings.DATABASE_MAX_OVERFLOW,
                "utilization_percent": round((pool.checkedout() / (settings.DATABASE_POOL_SIZE + settings.DATABASE_MAX_OVERFLOW)) * 100, 2)
            }
        }
    except Exception as e:
        logger.error(f"Failed to get pool status: {e}")
        return {"status": "error", "error": str(e), "pool": None}


# Helper function for repositories that need manual session management
def get_session_factory() -> Optional[async_sessionmaker[AsyncSession]]:
    """Get the session factory for manual session management"""
    return async_session_factory


def get_engine():
    """Get the database engine for direct operations"""
    return engine