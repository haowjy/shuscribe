# backend/src/database/connection.py
"""
SQLAlchemy database connection and session management
"""
import logging
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text # For simple DB connection test

from src.config import settings
from src.database.base import Base # Import our Base
from src.core.exceptions import ShuScribeException # Import custom exception

logger = logging.getLogger(__name__)

# Globally declared, but initialized conditionally
engine: Optional[AsyncEngine] = None
AsyncSessionLocal: Optional[sessionmaker] = None

if not settings.SKIP_DATABASE:
    try:
        # Create async engine
        engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)

        # Create an async session maker
        AsyncSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False, # Do not expire objects after commit
        )
        logger.info("Database engine and sessionmaker initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize database engine due to: {e}. "
                     "Database features will be unavailable.", exc_info=settings.DEBUG)
        # Ensure engine and session local are None if initialization failed
        engine = None
        AsyncSessionLocal = None
else:
    logger.warning("Database connection skipped due to SKIP_DATABASE setting.")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes to get a database session"""
    if settings.SKIP_DATABASE:
        raise ShuScribeException(
            "Database connection explicitly skipped via configuration. Cannot provide a session.",
            status_code=503 # Service Unavailable
        )
    if engine is None or AsyncSessionLocal is None:
        raise ShuScribeException(
            "Database engine or sessionmaker failed to initialize during startup. Cannot provide a session.",
            status_code=503 # Service Unavailable
        )
            
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initializes the database by creating all tables (for dev/tests)"""
    if settings.SKIP_DATABASE:
        logger.warning("Database `create_all()` skipped because SKIP_DATABASE is true.")
        return
    
    if engine is None:
        logger.error("Database `create_all()` cannot proceed: engine is not initialized.")
        # Optionally raise an error or just return, depending on desired strictness
        raise ShuScribeException("Database engine not initialized, cannot run `create_all`.")

    logger.info("Attempting to create database tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}", exc_info=True)
        # Re-raise the exception to indicate a critical startup failure in development
        raise


# NOTE: For production, you should use Alembic for migrations instead of create_all()