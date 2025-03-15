# shuscribe/api/endpoints/llm.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any, Type
from pydantic import create_model, Field

from shuscribe.services.llm.providers.provider import Message, MessageRole
from shuscribe.services.llm.factory import get_provider_class
from shuscribe.schemas.llm import (
    GenerationRequest, 
    GenerationResponse,
    ProviderConfig
)

router = APIRouter()

@router.post("/generate", response_model=GenerationResponse)
async def generate_completion(request: GenerationRequest):
    """Generate a completion from an LLM."""
    
    # Get the appropriate provider class
    try:
        provider_class = get_provider_class(request.provider)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Initialize the provider with the user's API key if provided
    api_key = request.provider_config.api_key if request.provider_config else None
    provider = provider_class(api_key=api_key)
    
    # Convert to internal message format
    messages = [
        Message(
            role=MessageRole(msg.role),
            content=msg.content,
            name=msg.name
        )
        for msg in request.messages
    ]
    
    # Handle streaming if requested
    if request.stream:
        async def generate_stream():
            try:
                async for chunk in provider.generate_stream(
                    messages=messages,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    top_p=request.top_p,
                    frequency_penalty=request.frequency_penalty,
                    presence_penalty=request.presence_penalty,
                    stop=request.stop
                ):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
                yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream"
        )
    
    # Regular synchronous generation
    try:
        response = await provider.generate(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
            stop=request.stop
        )
        
        return {
            "text": response.text,
            "model": response.model,
            "usage": response.usage,
            "finish_reason": response.finish_reason,
            "tool_calls": response.tool_calls
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse")
async def parse_structured_output(request: dict):
    """Generate a structured output from an LLM."""
    
    # Extract basic request parameters
    provider_name = request.pop("provider")
    model = request.pop("model")
    messages_data = request.pop("messages")
    schema_definition = request.pop("schema_definition")
    
    # Get the appropriate provider class
    try:
        provider_class = get_provider_class(provider_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Check if provider supports structured output
    provider = provider_class(api_key=request.get("provider_config", {}).get("api_key"))
    if not provider.supports_structured_output:
        raise HTTPException(
            status_code=400, 
            detail=f"Provider '{provider_name}' does not support structured output"
        )
    
    # Convert messages to internal format
    messages = [
        Message(
            role=MessageRole(msg["role"]),
            content=msg["content"],
            name=msg.get("name")
        )
        for msg in messages_data
    ]
    
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
    
    # Parse the structured output
    try:
        response = await provider.parse(
            messages=messages,
            model=model,
            response_format=DynamicModel,
            **request
        )
        
        # Convert parsed response to dict for JSON serialization
        parsed_dict = response.parsed_response.dict() if response.parsed_response else None
        
        return {
            "text": response.text,
            "model": response.model,
            "usage": response.usage,
            "finish_reason": response.finish_reason,
            "parsed_response": parsed_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))