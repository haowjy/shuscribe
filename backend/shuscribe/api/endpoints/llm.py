# shuscribe/api/endpoints/llm.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any, Type
from pydantic import create_model, Field

from shuscribe.services.llm.providers.provider import Message
from shuscribe.services.llm.factory import get_provider_class
from shuscribe.schemas.llm import (
    GenerationRequest, 
    GenerationResponse,
    ProviderConfig
)

router = APIRouter()

# @router.post("/generate", response_model=GenerationResponse)
# async def generate_completion(request: GenerationRequest):
#     try:
#         provider_class = get_provider_class(request.provider)
#         async with LLMSession.session_scope() as session:
#             provider = await session.get_provider(request.provider, request.provider_config.api_key)
#             result = await provider.generate(
#                 messages=request.messages,
#                 model=request.model,
#                 # other parameters
#             )
#             return GenerationResponse(
#                 text=result.text,
#                 model=result.model,
#                 usage=result.usage,
#                 # other fields
#             )
#     except LLMProviderException as e:
#         # Convert to appropriate HTTP response
#         raise HTTPException(
#             status_code=get_status_code_for_error(e.category),
#             detail=e.to_dict()
#         )

# @router.post("/stream", response_model=StreamResponse)
# async def stream_completion(request: StreamRequest):
#     # TODO: Implement this
#     pass