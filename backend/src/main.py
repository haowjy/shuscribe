# backend/src/main.py
"""
ShuScribe FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1.router import api_router
from src.config import settings
from src.core.exceptions import ShuScribeException
from src.core.logging import configure_console_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    configure_console_logging(log_level="DEBUG")
    logging.info("ShuScribe backend starting up...")
    
    # Initialize database connection and repositories
    from src.database.connection import init_database, create_tables, close_database
    from src.database.factory import init_repositories
    
    try:
        # Initialize database connection
        init_database()
        logging.info("Database connection initialized")
        
        # Create tables if needed (no migrations approach)
        if settings.DATABASE_BACKEND != "memory":
            await create_tables()
            logging.info("Database tables created")
        
        # Initialize repositories
        init_repositories(backend=settings.DATABASE_BACKEND)
        logging.info(f"Repositories initialized with {settings.DATABASE_BACKEND} backend")
        
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        # Continue with memory backend as fallback
        logging.warning("Falling back to memory backend")
        init_repositories(backend="memory")
    
    yield
    
    # Shutdown
    await close_database()
    logging.info("ShuScribe backend shutting down...")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title="ShuScribe API",
        description="Intelligent spoiler-free wiki generator for serialized fiction",
        version="0.1.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Global exception handler
    @app.exception_handler(ShuScribeException)
    async def shuscribe_exception_handler(request: Request, exc: ShuScribeException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "details": exc.details,
                "type": exc.__class__.__name__,
            },
        )
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    return app


# Create the app instance
app = create_application()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ShuScribe API",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else "disabled",
    }
    
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0",
    }