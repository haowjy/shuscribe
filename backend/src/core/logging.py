# backend/src/core/logging.py
"""
Logging configuration
"""
import logging
import sys
from typing import Optional, List

# Assuming src.config provides settings, if not, create a dummy class for testing
try:
    from src.config import settings
except ImportError:
    class DummySettings:
        LOG_LEVEL = "INFO" # Default level for production/main app
        DEBUG = False
    settings = DummySettings()

def configure_console_logging(
    log_level: str = "INFO",
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    logger_names: Optional[List[str]] = None
) -> None:
    """
    Configures logging to stream to stdout with a specified format and level.
    Optionally sets levels for specific logger names.
    This function can be called multiple times safely by clearing handlers.
    """
    # Remove any existing handlers to prevent duplicate output, especially for stdout
    for handler in logging.root.handlers[:]:
        if isinstance(handler, logging.StreamHandler) and handler.stream is sys.stdout:
            logging.root.removeHandler(handler)
            handler.close()

    # Create a new handler for stdout
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)
    
    # Add the handler to the root logger
    logging.root.addHandler(console_handler)
    logging.root.setLevel(getattr(logging, log_level.upper()))

    # Optionally set specific levels for given logger names
    if logger_names:
        for name in logger_names:
            logging.getLogger(name).setLevel(getattr(logging, log_level.upper()))

def setup_application_logging(log_level: Optional[str] = None) -> None:
    """
    Setup application-specific logging levels and silence noisy third-party loggers.
    This works on top of whatever basic console logging is already configured.
    """    
    level = log_level or settings.LOG_LEVEL
    
    # Set the default level for our custom 'shuscribe' logger
    app_logger = logging.getLogger("shuscribe")
    app_logger.setLevel(getattr(logging, level.upper()))
    
    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    if settings.DEBUG:
        app_logger.info("Debug logging enabled")