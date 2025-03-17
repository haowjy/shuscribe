from fastapi import APIRouter

from shuscribe.api.endpoints.llm import router as llm_router
from shuscribe.api.endpoints.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(llm_router, prefix="/llm", tags=["llm"])

@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.get("/test")
async def test():
    return {"message": "Test"}

