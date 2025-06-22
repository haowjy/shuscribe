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
from src.utils.logging import setup_logging


# backend/src/main.py - Update lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    setup_logging()
    logging.info("ShuScribe backend starting up...")
    
    # Initialize database (for development only)
    if settings.ENVIRONMENT == "development":
        from src.database.connection import init_db
        await init_db()
        logging.info("Database initialized")
    
    yield
    
    # Shutdown
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