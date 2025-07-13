# backend/src/main.py
"""
ShuScribe FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1.router import api_router
from src.config import settings
from src.core.exceptions import ShuScribeException
from src.core.logging import configure_console_logging, setup_application_logging
from src.schemas.base import ApiResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    configure_console_logging(log_level="DEBUG")
    setup_application_logging()
    
    # Disable hpack debug messages
    logging.getLogger("hpack.hpack").setLevel(logging.WARNING)
    
    logging.info("ShuScribe backend starting up...")
    
    # Initialize database connection and repositories
    from src.database.connection import init_database, create_tables, close_database
    from src.database.factory import init_repositories
    
    try:
        # Initialize database connection
        logging.info(f"Starting initialization with DATABASE_BACKEND={settings.DATABASE_BACKEND}")
        init_database()
        logging.info("Database connection initialized")
        
        # Create tables if needed (no migrations approach)
        if settings.DATABASE_BACKEND != "memory":
            await create_tables()
            logging.info("Database tables created")
        
        # Initialize repositories
        init_repositories(backend=settings.DATABASE_BACKEND)
        logging.info(f"Repositories initialized with {settings.DATABASE_BACKEND} backend")
        
        # Seed database in development
        if settings.DATABASE_BACKEND in ["database", "memory"]:
            from src.database.seeder import should_seed_database, seed_development_database
            
            if should_seed_database():
                logging.info("Starting database seeding for development environment...")
                try:
                    seed_results = await seed_development_database()
                    
                    if "error" in seed_results:
                        logging.warning(f"Database seeding failed: {seed_results['error']}")
                    else:
                        logging.info(f"Database seeding completed successfully: "
                                   f"{seed_results.get('projects_created', 0)} projects created")
                        
                        if seed_results.get('errors'):
                            logging.warning(f"Seeding completed with {len(seed_results['errors'])} errors")
                            
                except Exception as e:
                    logging.error(f"Database seeding failed with exception: {e}")
            else:
                logging.info("Database seeding disabled by configuration")
        
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        if "Network is unreachable" in str(e):
            logging.warning("Network connectivity issue detected (likely IPv6 vs WSL2). This is a known issue with Supabase direct connections in WSL2 environments.")
            logging.warning("For production use, consider using Supabase pooler connection or enabling IPv4 add-on.")
        logging.warning("Falling back to memory backend for development")
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
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Request: {request.method} {request.url} headers: {dict(request.headers)}")
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Global exception handler for ShuScribe exceptions
    @app.exception_handler(ShuScribeException)
    async def shuscribe_exception_handler(request: Request, exc: ShuScribeException):
        # Create error response in ApiResponse format matching frontend expectations
        error_response = ApiResponse.create_error(
            error=exc.message,
            status=exc.status_code,
            message=exc.message  # Frontend expects both error and message fields
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(),
        )
    
    # Global exception handler for HTTP exceptions (FastAPI default)
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # Create error response in ApiResponse format matching frontend expectations
        error_response = ApiResponse.create_error(
            error=exc.detail,
            status=exc.status_code,
            message=exc.detail  # Frontend expects both error and message fields
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(),
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