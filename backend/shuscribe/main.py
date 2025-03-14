from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shuscribe.api.router import api_router
from shuscribe.core.config import settings

app = FastAPI(
    title="ShuScribe API",
    description="Narrative Wiki Generator API",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to ShuScribe API"}
