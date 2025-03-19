# /Users/jimmyyao/gitrepos/shuscribe/backend/shuscribe/main.py
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import logging

from shuscribe.api.router import api_router
from shuscribe.core.config import get_settings

from dotenv import load_dotenv
import os

# Load environment variables at startup
load_dotenv()

# Debug environment variables
print("===== ENVIRONMENT VARIABLES =====")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_KEY: {os.getenv('SUPABASE_KEY', 'FOUND BUT NOT SHOWN')[:5]}..." if os.getenv('SUPABASE_KEY') else "SUPABASE_KEY: NOT FOUND")
print(f"SUPABASE_SERVICE_KEY: {'FOUND BUT NOT SHOWN' if os.getenv('SUPABASE_SERVICE_KEY') else 'NOT FOUND'}")
print(f"CORS_ORIGINS: {os.getenv('CORS_ORIGINS')}")
print("=================================")

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
