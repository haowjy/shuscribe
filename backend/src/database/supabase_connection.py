# backend/src/database/supabase_connection.py

"""
Supabase client connection and management
"""
import logging
from typing import Optional

from supabase import create_client, Client
from src.config import settings
from src.core.exceptions import ShuScribeException

logger = logging.getLogger(__name__)

# Globally declared, but initialized conditionally
supabase_client: Optional[Client] = None

if not settings.SKIP_DATABASE:
    try:
        # Create Supabase client
        supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Supabase client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client due to: {e}. "
                     "Database features will be unavailable.", exc_info=settings.DEBUG)
        supabase_client = None
else:
    logger.warning("Database connection skipped due to SKIP_DATABASE setting.")


def get_supabase_client() -> Client:
    """Get the Supabase client instance"""
    if settings.SKIP_DATABASE:
        raise ShuScribeException(
            "Database connection explicitly skipped via configuration. Cannot provide Supabase client.",
            status_code=503
        )
    if supabase_client is None:
        raise ShuScribeException(
            "Supabase client failed to initialize during startup. Cannot provide client.",
            status_code=503
        )
    return supabase_client


async def init_db() -> None:
    """Initialize the database (for Supabase, this mainly checks connectivity)"""
    if settings.SKIP_DATABASE:
        logger.warning("Database initialization skipped because SKIP_DATABASE is true.")
        return
    
    if supabase_client is None:
        logger.error("Database initialization cannot proceed: Supabase client is not initialized.")
        raise ShuScribeException("Supabase client not initialized, cannot run initialization.")

    logger.info("Verifying Supabase connection...")
    try:
        # Test the connection by making a simple query
        # This will raise an exception if there are connectivity issues
        supabase_client.table('users').select('id').limit(1).execute()
        logger.info("Supabase connection verified successfully.")
    except Exception as e:
        logger.warning(f"Supabase connection test failed: {e}. This may be normal if tables don't exist yet.")
        # Don't raise an error here since this might be the first time running
        # and tables might not exist yet 