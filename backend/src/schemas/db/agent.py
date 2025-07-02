"""
Agent domain schemas for tracking AI agent conversations and executions.
"""

from datetime import datetime, UTC
from typing import Dict, Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from src.schemas.base import BaseSchema


class AgentMessage(BaseModel):
    """Single message in an agent conversation"""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentConversation(BaseSchema):
    """Complete conversation with an AI agent"""
    id: UUID
    workspace_id: UUID
    agent_type: str  # "arc_splitter", "wiki_planner", "article_writer", etc.
    conversation_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)  # Agent-specific context
    messages: List[AgentMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None


class AgentConversationCreate(BaseModel):
    """Data for creating a new agent conversation"""
    workspace_id: UUID
    agent_type: str
    conversation_id: Optional[str] = None  # Optional, can be auto-generated
    context: Dict[str, Any] = Field(default_factory=dict)
    messages: List[AgentMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    initial_message: Optional[AgentMessage] = None


class AgentConversationUpdate(BaseModel):
    """Data for updating an agent conversation"""
    agent_type: Optional[str] = None
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    messages: Optional[List[AgentMessage]] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentMetrics(BaseModel):
    """Metrics for agent execution"""
    tokens_used: int
    execution_time_ms: int
    model_name: str
    provider: str
    cost_estimate: float = 0.0
    
    # Additional metrics
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    thinking_tokens: Optional[int] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tokens_used": 1500,
                "execution_time_ms": 2300,
                "model_name": "gpt-4",
                "provider": "openai",
                "cost_estimate": 0.045,
                "input_tokens": 500,
                "output_tokens": 1000,
            }
        }
    )


class AgentExecution(BaseSchema):
    """Record of a single agent execution"""
    id: UUID
    workspace_id: UUID
    agent_type: str
    execution_id: Optional[str] = None
    conversation_id: Optional[UUID] = None
    
    # Input/Output
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Status tracking
    status: str = "pending"  # "pending", "running", "completed", "failed"
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Metrics
    metrics: Optional[AgentMetrics] = None
    
    # Timestamps
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class AgentExecutionCreate(BaseModel):
    """Data for creating a new agent execution"""
    workspace_id: UUID
    agent_type: str
    execution_id: Optional[str] = None  # Optional, can be auto-generated  
    conversation_id: Optional[UUID] = None  # Optional, can be auto-linked
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    metrics: Optional[AgentMetrics] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class AgentExecutionUpdate(BaseModel):
    """Data for updating an agent execution"""
    agent_type: Optional[str] = None
    execution_id: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    metrics: Optional[AgentMetrics] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class AgentExecutionResult(BaseModel):
    """Result data for updating an execution"""
    output_data: Dict[str, Any]
    status: str  # "completed" or "failed"
    error_message: Optional[str] = None
    metrics: AgentMetrics
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UserFeedback(BaseModel):
    """User feedback on agent execution"""
    execution_id: UUID
    rating: Optional[int] = Field(None, ge=1, le=5)  # 1-5 rating
    feedback_text: Optional[str] = None
    corrections: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# Agent type enumeration for consistency
class AgentType:
    """Standard agent types in the system"""
    # WikiGen agents
    ARC_SPLITTER = "arc_splitter"
    WIKI_PLANNER = "wiki_planner"
    ARTICLE_WRITER = "article_writer"
    CHAPTER_BACKLINKER = "chapter_backlinker"
    GENERAL_SUMMARIZER = "general_summarizer"
    
    # Future agent types
    FACT_CHECKER = "fact_checker"
    CONSISTENCY_CHECKER = "consistency_checker"
    STYLE_EDITOR = "style_editor"
    CHARACTER_DEVELOPER = "character_developer"
    PLOT_ANALYZER = "plot_analyzer"