# shuscribe/main.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import logging

from shuscribe.api.router import api_router
from shuscribe.core.config import get_settings

from dotenv import load_dotenv

# Load environment variables at startup
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="ShuScribe API",
    description="Narrative Wiki Generator API",
    version="0.1.0",
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router with /api prefix
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to ShuScribe API"}

@asynccontextmanager
async def lifespan(app: FastAPI): # https://fastapi.tiangolo.com/advanced/events/#lifespan-function
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")
