# shuscribe/api/endpoints/pipeline.py

from typing import List
import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from shuscribe.schemas.pipeline import WikiGenPipelineConfig, StreamStatus
from shuscribe.services.llm.session import LLMSession
from shuscribe.schemas.user import User
from shuscribe.auth.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/pipelines", response_model=dict)
async def create_pipeline(
    config: WikiGenPipelineConfig,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new pipeline execution session.
    
    Args:
        config: Configuration for the pipeline execution.
        current_user: Authenticated user from dependency.
    
    Returns:
        dict: Contains the pipeline_id for the created pipeline.
    """
    user_id = str(current_user.id)
    async with LLMSession.session_scope() as session:
        pipeline_id, _ = await session.create_pipeline_session(
            pipeline_config=config,
            user_id=user_id
        )
        return {"pipeline_id": pipeline_id}


@router.get("/pipelines/{pipeline_id}")
async def get_pipeline(
    pipeline_id: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Stream pipeline events.
    
    Args:
        pipeline_id: The ID of the pipeline to stream.
        request: The request object.
        current_user: Authenticated user from dependency.
    
    Returns:
        EventSourceResponse: A server-sent events response.
    """
    user_id = str(current_user.id)
    async with LLMSession.session_scope() as session:
        pipeline_session = session.get_pipeline_session(pipeline_id)
        if not pipeline_session or pipeline_session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Pipeline session not found or access denied")

        async def sse_generator():
            try:
                # Stream chunks
                async for chunk in pipeline_session:
                    yield {"data": chunk.model_dump_json()}
                    if chunk.status in (StreamStatus.COMPLETE, StreamStatus.ERROR):
                        break
            except asyncio.CancelledError:
                pass  # Handle client disconnect

        return EventSourceResponse(sse_generator())


@router.get("/pipelines", response_model=List[dict])
async def list_pipelines(
    current_user: User = Depends(get_current_user)
):
    """
    List all pipelines for the current user.
    
    Args:
        current_user: Authenticated user from dependency.
    
    Returns:
        List[dict]: List of pipeline information.
    """
    user_id = str(current_user.id)
    async with LLMSession.session_scope() as session:
        return await session.get_user_pipeline_sessions(user_id)
    