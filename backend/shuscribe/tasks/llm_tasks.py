# shuscribe/tasks/llm_tasks.py

from typing import Any, Dict, List, Optional
from celery import shared_task
import httpx
import json
import asyncio
import logging

from shuscribe.services.llm.providers.provider import Message, MessageRole
from shuscribe.services.llm.session import LLMSession

logger = logging.getLogger(__name__)

@shared_task
def process_llm_generation(
    provider_name: str,
    messages_data: List[Dict],
    model: str,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    top_p: float = 1.0,
    frequency_penalty: float = 0.0,
    presence_penalty: float = 0.0,
    stop: Optional[List[str]] = None,
    callback_url: Optional[str] = None,
    api_key: Optional[str] = None,
):
    """Process LLM generation in background using Celery."""
    
    async def _process():
        # Convert messages to internal format
        messages = [
            Message(
                role=MessageRole(msg["role"]),
                content=msg["content"],
                name=msg.get("name")
            )
            for msg in messages_data
        ]
        
        try:
            # Get a session using the context manager for proper cleanup
            async with LLMSession.session_scope() as session:
                # Get the appropriate provider (reusing clients when possible)
                provider = await session.get_provider(provider_name, api_key)
                
                # Generate the response
                response = await provider.generate(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    stop=stop
                )
                
                result = {
                    "success": True,
                    "text": response.text,
                    "model": response.model,
                    "usage": response.usage,
                    "finish_reason": response.finish_reason,
                    "tool_calls": response.tool_calls if hasattr(response, "tool_calls") else None,
                    "parsed_response": response.parsed_response.dict() if hasattr(response, "parsed_response") and response.parsed_response else None
                }
        except Exception as e:
            logger.exception(f"Error in LLM generation task: {str(e)}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        # Call webhook if provided
        if callback_url:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        callback_url,
                        json=result,
                        headers={"Content-Type": "application/json"}
                    )
            except Exception as e:
                logger.exception(f"Error sending callback to {callback_url}: {str(e)}")
        
        return result
    
    # Run async function in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_process())
    finally:
        loop.close()

@shared_task
def process_llm_structured_output(
    provider_name: str,
    messages_data: List[Dict],
    model: str,
    schema_definition: Dict,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    top_p: float = 1.0,
    frequency_penalty: float = 0.0,
    presence_penalty: float = 0.0,
    stop: Optional[List[str]] = None,
    callback_url: Optional[str] = None,
    api_key: Optional[str] = None,
):
    """Process structured output generation in background using Celery."""
    from pydantic import create_model, Field
    
    async def _process():
        # Convert messages to internal format
        messages = [
            Message(
                role=MessageRole(msg["role"]),
                content=msg["content"],
                name=msg.get("name")
            )
            for msg in messages_data
        ]
        
        try:
            # Dynamically create Pydantic model from schema definition
            model_fields = {}
            for field_name, field_info in schema_definition["properties"].items():
                field_type = str
                if field_info.get("type") == "integer":
                    field_type = int
                elif field_info.get("type") == "number":
                    field_type = float
                elif field_info.get("type") == "boolean":
                    field_type = bool
                elif field_info.get("type") == "array":
                    if field_info.get("items", {}).get("type") == "string":
                        field_type = List[str]
                    elif field_info.get("items", {}).get("type") == "integer":
                        field_type = List[int]
                    else:
                        field_type = List[Any]
                
                required = field_name in schema_definition.get("required", [])
                
                model_fields[field_name] = (field_type, Field(...) if required else Field(None))
            
            DynamicModel = create_model("DynamicModel", **model_fields)
            
            # Get a session using the context manager for proper cleanup
            async with LLMSession.session_scope() as session:
                # Get the appropriate provider (reusing clients when possible)
                provider = await session.get_provider(provider_name, api_key)
                
                # Check if provider supports structured output
                if not provider.supports_structured_output:
                    raise ValueError(f"Provider '{provider_name}' does not support structured output")
                
                # Parse structured output
                response = await provider.parse(
                    messages=messages,
                    model=model,
                    response_format=DynamicModel,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    stop=stop
                )
                
                # Convert parsed response to dict for JSON serialization
                parsed_dict = response.parsed_response.dict() if response.parsed_response else None
                
                result = {
                    "success": True,
                    "text": response.text,
                    "model": response.model,
                    "usage": response.usage,
                    "finish_reason": response.finish_reason,
                    "parsed_response": parsed_dict
                }
        except Exception as e:
            logger.exception(f"Error in LLM structured output task: {str(e)}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        # Call webhook if provided
        if callback_url:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        callback_url,
                        json=result,
                        headers={"Content-Type": "application/json"}
                    )
            except Exception as e:
                logger.exception(f"Error sending callback to {callback_url}: {str(e)}")
        
        return result
    
    # Run async function in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_process())
    finally:
        loop.close()