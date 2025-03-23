# shuscribe/api/endpoints/llm.py

import asyncio
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Literal, Optional
from pydantic import BaseModel
import logging
from sse_starlette.sse import EventSourceResponse

from shuscribe.schemas.llm import Message, GenerationConfig, ThinkingConfig
from shuscribe.schemas.provider import ProviderName

from shuscribe.services.llm.session import LLMSession
from shuscribe.services.llm.providers.provider import LLMResponse
from shuscribe.services.llm.streaming import StreamChunk, StreamStatus
from shuscribe.services.llm.errors import LLMProviderException, ErrorCategory, RetryConfig

# Import user auth dependencies
from shuscribe.auth.dependencies import get_current_user
from shuscribe.schemas.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

# Minimal request model that maps to parameters needed for generation
class GenerateRequest(BaseModel):
    """Request model for LLM generation"""
    provider: ProviderName
    model: str
    messages: List[Message | str]  # Directly using the Message class
    
    # API key is required - provide your own API key
    api_key: str
    
    # Generation config options
    temperature: Optional[float] = 0.7
    max_output_tokens: Optional[int] = None
    top_p: Optional[float] = 1.0
    system_prompt: Optional[str] = None
    stop_sequences: Optional[List[str]] = None
    
    # Thinking mode options
    enable_thinking: Optional[bool] = False
    thinking_effort: Optional[Literal["low", "medium", "high"]] = "low"
    thinking_budget: Optional[int] = 3200
    
    # Retry options
    enable_retries: Optional[bool] = False
    max_retries: Optional[int] = 3
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider": "anthropic",
                "model": "claude-3-5-haiku-20241022",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello."
                    },
                    {
                        "role": "assistant",
                        "content": "Hello. How can I help you today?"
                    },
                    "What is a narrative wiki generator?"
                ],
                "temperature": 0.7,
                "max_output_tokens": 1000,
                "enable_thinking": True
            }
        }

class StreamSessionInfo(BaseModel):
    """Information about an active streaming session"""
    session_id: str
    provider: Optional[str]
    model: Optional[str]
    status: str
    accumulated_text_length: int
    created_at: float
    last_active: float
    user_id: str


def build_generation_config(request: GenerateRequest) -> GenerationConfig:
    """Build generation config from request parameters"""
    # Set up thinking config if enabled
    thinking_config = None
    if request.enable_thinking:
        thinking_config = ThinkingConfig(
            enabled=True,
            budget_tokens=request.thinking_budget,
            effort=request.thinking_effort
        )
    
    # Set up retry config if enabled
    retry_config = None
    if request.enable_retries:
        retry_config = RetryConfig(
            enabled=True,
            max_retries=request.max_retries or 0,
            retry_on=[
                ErrorCategory.RATE_LIMIT,
                ErrorCategory.SERVICE_ERROR,
                ErrorCategory.NETWORK_ERROR
            ]
        )
    
    # Create the config object
    return GenerationConfig(
        temperature=request.temperature,
        max_output_tokens=request.max_output_tokens,
        top_p=request.top_p,
        system_prompt=request.system_prompt,
        stop_sequences=request.stop_sequences,
        thinking_config=thinking_config,
        retry_config=retry_config
    )

@router.post("/generate", response_model=LLMResponse)
async def generate(
    request: GenerateRequest, 
    current_user: User = Depends(get_current_user)
):
    """Generate a complete response from an LLM"""
    try:
        logger.info(f"User {current_user.id} making LLM request with provider {request.provider}")

        config = build_generation_config(request)
        user_id = str(current_user.id)
        
        # Add user context to the request for tracking and billing
        if config and not config.context_id:
            config.context_id = f"user_{user_id}"
        
        async with LLMSession.session_scope() as session:
            return await session.generate(
                provider_name=request.provider,
                model=request.model,
                messages=request.messages,
                config=config,
                api_key=request.api_key,  # API key comes directly from request
                user_id=user_id
            )
            
    except LLMProviderException as e:
        # Map provider exception categories to HTTP status codes
        status_code = 500
        if e.category == ErrorCategory.AUTHENTICATION:
            status_code = 401
        elif e.category == ErrorCategory.RATE_LIMIT:
            status_code = 429
        elif e.category == ErrorCategory.INVALID_REQUEST:
            status_code = 400
        
        # Raise HTTP exception with details from provider exception
        raise HTTPException(
            status_code=status_code,
            detail={
                "error": e.message,
                "code": e.code,
                "category": str(e.category),
                "provider": e.provider,
                "retry_after": e.retry_after,
                "details": e.details
            }
        )
    except Exception as e:
        logger.exception("Unexpected error in generate endpoint")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "code": "unexpected_error"}
        )


@router.post("/streams", response_model=dict)
async def create_stream(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new streaming session.
    
    Args:
        request: Contains provider, model, messages, config, and optionally api_key.
        current_user: Authenticated user from dependency.
    
    Returns:
        dict: Contains the session_id for the created session.
    """
    user_id = str(current_user.id)
    async with LLMSession.session_scope() as session:
        session_id, _ = await session.create_streaming_session(
            provider_name=request.provider,
            model=request.model,
            messages=request.messages,
            config=build_generation_config(request),
            api_key=request.api_key,
            user_id=user_id
        )
        return {"session_id": session_id}


@router.get("/streams/{session_id}")
async def get_stream(
    session_id: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    user_id = str(current_user.id)
    async with LLMSession.session_scope() as session:
        stream_session = session.get_streaming_session(session_id)
        if not stream_session or stream_session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Stream session not found or access denied")

        async def sse_generator():
            try:
                # Send initial chunk with accumulated_text
                initial_chunk = StreamChunk(
                    text="",
                    accumulated_text=stream_session.accumulated_text,
                    status=stream_session.status,
                    session_id=session_id
                )
                yield {"data": initial_chunk.model_dump_json()}

                # Stream subsequent chunks
                async for chunk in stream_session:
                    # For the final chunk (COMPLETE or ERROR), include the accumulated_text
                    if chunk.status in (StreamStatus.COMPLETE, StreamStatus.ERROR):
                        stream_chunk = StreamChunk(
                            text=chunk.text,
                            accumulated_text=stream_session.accumulated_text,  # Include accumulated_text for final chunk
                            usage=chunk.usage,
                            status=chunk.status,
                            session_id=session_id,
                            error=chunk.error,
                            tool_calls=chunk.tool_calls,
                            metadata=chunk.metadata
                        )
                    else:
                        # For intermediate chunks, omit accumulated_text for efficiency
                        stream_chunk = StreamChunk(
                            text=chunk.text, 
                            accumulated_text="",  # Omit for non-final chunks
                            usage=None, # no usage for intermediate chunks
                            status=chunk.status,
                            session_id=session_id,
                            error=chunk.error,
                            tool_calls=chunk.tool_calls,
                            metadata=chunk.metadata
                        )
                    yield {"data": stream_chunk.model_dump_json()}
                    if chunk.status in (StreamStatus.COMPLETE, StreamStatus.ERROR):
                        break
            except asyncio.CancelledError:
                pass  # Handle client disconnect

        return EventSourceResponse(sse_generator())
    
@router.post("/streams/{session_id}/cancel")
async def cancel_stream(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    user_id = str(current_user.id)
    async with LLMSession.session_scope() as session:
        stream_session = session.get_streaming_session(session_id)
        if not stream_session or stream_session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Stream session not found or access denied")
        
        await session.cancel_streaming_session(session_id)
    return {"message": "Stream cancelled successfully"}

# @router.post("/streams/{session_id}/full")
# TODO: get the full response from the stream based on the session_id
# async def full_stream(
#     session_id: str,
#     current_user: User = Depends(get_current_user)
# ):
#     user_id = str(current_user.id)
#     async with LLMSession.session_scope() as session:
#         stream_session = session.get_streaming_session(session_id)
#         if not stream_session or stream_session.user_id != user_id:
#             raise HTTPException(status_code=404, detail="Stream session not found or access denied")
        
#         async def sse_generator():
#             try:
#                 async for chunk in stream_session:
#                     yield {"data": chunk.model_dump_json()}
#             except asyncio.CancelledError:
#                 pass
#         return EventSourceResponse(sse_generator())