# shuscribe/schemas/llm.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class MessageSchema(BaseModel):
    role: str = Field(..., description="Role of the message sender: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Content of the message")
    name: Optional[str] = Field(None, description="Optional name identifier for the message sender")

class ProviderConfig(BaseModel):
    api_key: Optional[str] = Field(None, description="Provider API key")
    organization_id: Optional[str] = Field(None, description="Optional organization ID")
    
    class Config:
        schema_extra = {
            "example": {
                "api_key": "sk-**********",
                "organization_id": "org-**********"
            }
        }

class GenerationRequest(BaseModel):
    provider: str = Field(..., description="LLM provider (openai, anthropic, etc.)")
    model: str = Field(..., description="Model name to use for generation")
    messages: List[MessageSchema] = Field(..., description="List of messages for the conversation")
    temperature: float = Field(0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    top_p: float = Field(1.0, description="Top-p sampling parameter")
    frequency_penalty: float = Field(0.0, description="Frequency penalty parameter")
    presence_penalty: float = Field(0.0, description="Presence penalty parameter")
    stop: Optional[List[str]] = Field(None, description="List of stop sequences")
    stream: bool = Field(False, description="Whether to stream the response")
    background: bool = Field(False, description="Whether to process in background")
    callback_url: Optional[str] = Field(None, description="Webhook URL for background processing")
    provider_config: Optional[ProviderConfig] = Field(None, description="Provider-specific configuration")
    
    # Structured output options
    response_format: Optional[Dict[str, Any]] = Field(None, description="Response format specification")
    json_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for structured output")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="Tool definitions for function calling")
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Tool choice specification")
    
    class Config:
        schema_extra = {
            "example": {
                "provider": "openai",
                "model": "gpt-4o",
                "messages": [
                    {"role": "user", "content": "Extract the name and age from this text: 'John is 25 years old.'"}
                ],
                "temperature": 0.7,
                "response_format": {"type": "json_object"},
                "json_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"}
                    },
                    "required": ["name", "age"]
                }
            }
        }

class GenerationResponse(BaseModel):
    text: Optional[str] = Field(None, description="Generated text (for non-streaming responses)")
    model: Optional[str] = Field(None, description="Model used for generation")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage statistics")
    finish_reason: Optional[str] = Field(None, description="Reason for finishing generation")
    task_id: Optional[str] = Field(None, description="Task ID for background processing")
    status: Optional[str] = Field(None, description="Status for background processing")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls in the response")