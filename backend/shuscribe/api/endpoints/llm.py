# shuscribe/api/endpoints/llm.py

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel
import logging
import json

# Import existing models directly from the LLM service
from shuscribe.services.llm.session import LLMSession
from shuscribe.schemas.llm import Message, GenerationConfig, ThinkingConfig
from shuscribe.services.llm.providers.provider import ProviderName, LLMResponse
from shuscribe.services.llm.streaming import StreamStatus
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
    max_tokens: Optional[int] = None
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
                "max_tokens": 1000,
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

class CapabilitiesResponse(BaseModel):
    """Response for capabilities endpoint"""
    providers: Dict[str, Any]
    models: Dict[str, List[str]]


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
        max_tokens=request.max_tokens,
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

@router.post("/generate_stream")
async def generate_stream(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Stream a response from an LLM
    
    This endpoint sends a request to the specified LLM provider and streams
    the response back chunk by chunk using a server-sent events stream.
    """
    
    config = build_generation_config(request)
    
    # Add user context to the request for tracking and billing
    context_id = f"user_{current_user.id}"
    if config.context_id:
        context_id = f"{context_id}_{config.context_id}"
    config.context_id = context_id
    
    async def stream_generator():
        try:
            async with LLMSession.session_scope() as session:
                # Use generate_stream directly from the session
                async for chunk in session.generate_stream(
                    provider_name=request.provider,
                    model=request.model,
                    messages=request.messages,
                    config=config,
                    api_key=request.api_key
                ):
                    # Add user ID to the chunk for tracking
                    chunk_data = chunk.model_dump()
                    chunk_data["user_id"] = str(current_user.id)
                    
                    # Stream each chunk as JSON, encoded as bytes
                    yield json.dumps(chunk_data).encode("utf-8") + b"\n"
                    
                    # If the stream is complete, break
                    if chunk.status == StreamStatus.COMPLETE:
                        break
        except Exception as e:
            # Handle errors in streaming
            error_detail = {"error": str(e)}
            if isinstance(e, LLMProviderException):
                error_detail = {
                    "error": e.message,
                    "code": e.code,
                    "category": str(e.category),
                    "provider": e.provider,
                    "retry_after": e.retry_after if hasattr(e, "retry_after") else None
                }
            
            yield json.dumps({"error": error_detail, "status": "error", "user_id": str(current_user.id)}).encode("utf-8")
    
    # Return a streaming response
    return StreamingResponse(
        stream_generator(),
        media_type="application/x-ndjson"
    )


@router.get("/streams", response_model=List[StreamSessionInfo])
async def list_streams(current_user: User = Depends(get_current_user)):
    """List all active streaming sessions for the current user"""
    try:
        user_id = str(current_user.id)
        
        async with LLMSession.session_scope() as session:
            # Use the user-specific method
            user_sessions = await session.get_user_streaming_sessions(user_id)
            return user_sessions
    except Exception as e:
        logger.exception("Unexpected error in list_streams endpoint")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)}
        )

@router.post("/stream/{action}/{session_id}")
async def manage_stream(
    action: str, 
    session_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Manage an existing streaming session
    
    Actions:
    - pause: Pause the stream
    - resume: Resume a paused stream
    - cancel: Cancel the stream
    - cleanup: Clean up resources for the stream
    """
    if action not in ["pause", "resume", "cancel", "cleanup"]:
        raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
    
    try:
        user_id = str(current_user.id)
        
        async with LLMSession.session_scope() as session:
            # Verify that the streaming session exists
            stream_session = session.get_streaming_session(session_id)
            if not stream_session:
                raise HTTPException(status_code=404, detail=f"Stream session {session_id} not found")
            
            # Verify that the session belongs to the current user
            if getattr(stream_session, 'user_id', None) != user_id:
                raise HTTPException(status_code=403, detail="You do not have permission to manage this stream")
            
            result = False
            
            # Perform the requested action
            if action == "pause":
                result = await session.pause_streaming_session(session_id)
            elif action == "resume":
                result = await session.resume_streaming_session(session_id)
            elif action == "cancel":
                result = await session.cancel_streaming_session(session_id)
            elif action == "cleanup":
                # Add cleanup to background tasks to avoid blocking
                background_tasks.add_task(session.cleanup_streaming_session, session_id)
                result = True
                
            if not result and action != "cleanup":
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to {action} stream session {session_id}"
                )
                
            return {"success": True, "action": action, "session_id": session_id}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in manage_stream endpoint ({action})")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)}
        )

