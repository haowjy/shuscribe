# backend/src/core/logging.py
"""
Logging configuration
"""
import logging
import sys
from typing import Optional

from src.config import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """Setup application logging"""
    
    level = log_level or settings.LOG_LEVEL
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Set our application logger
    logger = logging.getLogger("shuscribe")
    logger.setLevel(getattr(logging, level.upper()))
    
    if settings.DEBUG:
        logger.info("Debug logging enabled")