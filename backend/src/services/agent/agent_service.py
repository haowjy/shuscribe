"""
Agent Service - Business logic for AI agent conversations and execution tracking.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import UTC, datetime

from src.database.interfaces.agent_repository import IAgentRepository
from src.database.interfaces.workspace_repository import IWorkspaceRepository
from src.schemas.db.agent import (
    AgentConversation, AgentConversationCreate, AgentConversationUpdate,
    AgentExecution, AgentExecutionCreate, AgentExecutionUpdate, AgentExecutionResult,
    AgentMessage, AgentMetrics, UserFeedback, AgentType
)


class AgentService:
    """Service layer for AI agent management with business logic."""
    
    def __init__(
        self, 
        agent_repository: IAgentRepository,
        workspace_repository: IWorkspaceRepository
    ):
        self.agent_repository = agent_repository
        self.workspace_repository = workspace_repository
    
    # Conversation Management
    async def create_conversation(self, conversation_data: AgentConversationCreate) -> AgentConversation:
        """Create a new agent conversation with validation."""
        # Verify workspace exists
        workspace = await self.workspace_repository.get_workspace(conversation_data.workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {conversation_data.workspace_id} not found")
        
        # Validate agent type
        if not self._is_valid_agent_type(conversation_data.agent_type):
            raise ValueError(f"Invalid agent type: {conversation_data.agent_type}")
        
        return await self.agent_repository.create_conversation(conversation_data)
    
    async def get_conversation(self, conversation_id: UUID) -> Optional[AgentConversation]:
        """Get conversation by ID."""
        return await self.agent_repository.get_conversation(conversation_id)
    
    async def update_conversation(
        self, conversation_id: UUID, conversation_data: AgentConversationUpdate
    ) -> AgentConversation:
        """Update an existing conversation."""
        # Verify conversation exists
        conversation = await self.agent_repository.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        return await self.agent_repository.update_conversation(conversation_id, conversation_data)
    
    async def delete_conversation(self, conversation_id: UUID) -> bool:
        """Delete a conversation."""
        return await self.agent_repository.delete_conversation(conversation_id)
    
    async def add_message_to_conversation(
        self, conversation_id: UUID, message: AgentMessage
    ) -> AgentConversation:
        """Add a message to an existing conversation."""
        # Verify conversation exists
        conversation = await self.agent_repository.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        return await self.agent_repository.add_message_to_conversation(conversation_id, message)
    
    async def get_conversations_by_workspace(
        self, workspace_id: UUID, agent_type: Optional[str] = None
    ) -> List[AgentConversation]:
        """Get conversations for a workspace, optionally filtered by agent type."""
        return await self.agent_repository.get_conversations_by_workspace(workspace_id, agent_type)
    
    async def get_conversations_by_agent_type(
        self, workspace_id: UUID, agent_type: str
    ) -> List[AgentConversation]:
        """Get conversations for a specific agent type."""
        if not self._is_valid_agent_type(agent_type):
            raise ValueError(f"Invalid agent type: {agent_type}")
        
        return await self.agent_repository.get_conversations_by_workspace(workspace_id, agent_type)
    
    # Execution Management
    async def create_execution(self, execution_data: AgentExecutionCreate) -> AgentExecution:
        """Create a new agent execution with validation."""
        # Verify conversation exists (only if conversation_id is provided)
        if execution_data.conversation_id is not None:
            conversation = await self.agent_repository.get_conversation(execution_data.conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {execution_data.conversation_id} not found")
        
        # Verify workspace exists
        workspace = await self.workspace_repository.get_workspace(execution_data.workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {execution_data.workspace_id} not found")
        
        # Validate agent type
        if not self._is_valid_agent_type(execution_data.agent_type):
            raise ValueError(f"Invalid agent type: {execution_data.agent_type}")
        
        return await self.agent_repository.create_execution(execution_data)
    
    async def get_execution(self, execution_id: UUID) -> Optional[AgentExecution]:
        """Get execution by ID."""
        return await self.agent_repository.get_execution(execution_id)
    
    async def update_execution(
        self, execution_id: UUID, execution_data: AgentExecutionUpdate
    ) -> AgentExecution:
        """Update an existing execution."""
        # Verify execution exists
        execution = await self.agent_repository.get_execution(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        return await self.agent_repository.update_execution(execution_id, execution_data)
    
    async def delete_execution(self, execution_id: UUID) -> bool:
        """Delete an execution."""
        return await self.agent_repository.delete_execution(execution_id)
    
    async def start_execution(self, execution_id: UUID) -> AgentExecution:
        """Mark an execution as started."""
        execution = await self.agent_repository.get_execution(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        if execution.status != "pending":
            raise ValueError(f"Execution {execution_id} is not in pending status")
        
        return await self.agent_repository.update_execution(
            execution_id, AgentExecutionUpdate(status="running", started_at=datetime.now(UTC))
        )
    
    async def complete_execution(
        self, execution_id: UUID, result: AgentExecutionResult
    ) -> AgentExecution:
        """Complete an execution with results."""
        execution = await self.agent_repository.get_execution(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        if execution.status not in ["running", "pending"]:
            raise ValueError(f"Execution {execution_id} cannot be completed from status {execution.status}")
        
        # Map result to update schema
        update_data = AgentExecutionUpdate(
            output_data=result.output_data,
            status=result.status,
            error_message=result.error_message,
            metrics=result.metrics,
            completed_at=result.completed_at
        )
        
        return await self.agent_repository.update_execution(execution_id, update_data)
    
    async def fail_execution(
        self, execution_id: UUID, error_message: str
    ) -> AgentExecution:
        """Mark an execution as failed."""
        execution = await self.agent_repository.get_execution(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        if execution.status not in ["running", "pending"]:
            raise ValueError(f"Execution {execution_id} cannot be failed from status {execution.status}")
        
        return await self.agent_repository.update_execution(
            execution_id, AgentExecutionUpdate(
                status="failed", 
                error_message=error_message, 
                completed_at=datetime.now(UTC)
            )
        )
    
    async def get_executions_by_conversation(self, conversation_id: UUID) -> List[AgentExecution]:
        """Get all executions for a conversation."""
        return await self.agent_repository.get_executions_by_conversation(conversation_id)
    
    async def get_executions_by_workspace(
        self, workspace_id: UUID, agent_type: Optional[str] = None, status: Optional[str] = None
    ) -> List[AgentExecution]:
        """Get executions for a workspace with optional filters."""
        if agent_type and not self._is_valid_agent_type(agent_type):
            raise ValueError(f"Invalid agent type: {agent_type}")
        
        if status and status not in ["pending", "running", "completed", "failed", "error"]:
            raise ValueError(f"Invalid status: {status}")
        
        return await self.agent_repository.get_executions_by_workspace(workspace_id, agent_type, status)
    
    async def get_executions_by_status(
        self, workspace_id: UUID, status: str
    ) -> List[AgentExecution]:
        """Get executions filtered by status."""
        if status not in ["pending", "running", "completed", "failed", "error"]:
            raise ValueError(f"Invalid status: {status}")
        
        return await self.agent_repository.get_executions_by_status(workspace_id, status)
    
    # User Feedback Management
    async def add_user_feedback(
        self, execution_id: UUID, rating: Optional[int] = None, 
        feedback_text: Optional[str] = None, corrections: Optional[Dict[str, Any]] = None
    ) -> UserFeedback:
        """Add user feedback for an execution."""
        # Verify execution exists and is completed
        execution = await self.agent_repository.get_execution(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        if execution.status != "completed":
            raise ValueError(f"Cannot add feedback to execution with status {execution.status}")
        
        # Validate rating
        if rating is not None and (rating < 1 or rating > 5):
            raise ValueError("Rating must be between 1 and 5")
        
        feedback = UserFeedback(
            execution_id=execution_id,
            rating=rating,
            feedback_text=feedback_text,
            corrections=corrections or {}
        )
        
        return await self.agent_repository.create_user_feedback(feedback)
    
    async def get_user_feedback(self, execution_id: UUID) -> Optional[UserFeedback]:
        """Get user feedback for an execution."""
        return await self.agent_repository.get_user_feedback(execution_id)
    
    # Analytics and Statistics
    async def get_agent_statistics(self, workspace_id: UUID) -> Dict[str, Any]:
        """Get comprehensive agent statistics for a workspace."""
        conversations = await self.agent_repository.get_conversations_by_workspace(workspace_id)
        executions = await self.agent_repository.get_executions_by_workspace(workspace_id)
        
        # Group by agent type
        conversations_by_type = {}
        executions_by_type = {}
        executions_by_status = {"pending": 0, "running": 0, "completed": 0, "failed": 0, "error": 0}
        
        for conv in conversations:
            agent_type = conv.agent_type
            conversations_by_type[agent_type] = conversations_by_type.get(agent_type, 0) + 1
        
        total_tokens = 0
        total_cost = 0.0
        total_execution_time = 0
        
        for exec in executions:
            agent_type = exec.agent_type
            executions_by_type[agent_type] = executions_by_type.get(agent_type, 0) + 1
            executions_by_status[exec.status] += 1
            
            if exec.metrics:
                total_tokens += exec.metrics.tokens_used
                total_cost += exec.metrics.cost_estimate
                total_execution_time += exec.metrics.execution_time_ms
        
        return {
            "workspace_id": workspace_id,
            "total_conversations": len(conversations),
            "total_executions": len(executions),
            "conversations_by_type": conversations_by_type,
            "executions_by_type": executions_by_type,
            "executions_by_status": executions_by_status,
            # Add individual status counts for backward compatibility
            "completed_executions": executions_by_status["completed"],
            "running_executions": executions_by_status["running"], 
            "error_executions": executions_by_status["error"],
            "total_tokens_used": total_tokens,
            "total_estimated_cost": total_cost,
            "total_execution_time_ms": total_execution_time,
            "average_execution_time_ms": total_execution_time // len(executions) if executions else 0
        }
    
    async def get_execution_metrics(
        self, workspace_id: UUID, agent_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed execution metrics."""
        executions = await self.agent_repository.get_executions_by_workspace(
            workspace_id, agent_type, status="completed"
        )
        
        if not executions:
            return {"message": "No completed executions found"}
        
        # Calculate averages and totals
        total_tokens = sum(e.metrics.tokens_used for e in executions if e.metrics)
        total_cost = sum(e.metrics.cost_estimate for e in executions if e.metrics)
        execution_times = [e.metrics.execution_time_ms for e in executions if e.metrics]
        
        # Group by model
        by_model = {}
        for exec in executions:
            if exec.metrics:
                model = exec.metrics.model_name
                if model not in by_model:
                    by_model[model] = {
                        "count": 0,
                        "total_tokens": 0,
                        "total_cost": 0.0,
                        "total_time_ms": 0
                    }
                
                by_model[model]["count"] += 1
                by_model[model]["total_tokens"] += exec.metrics.tokens_used
                by_model[model]["total_cost"] += exec.metrics.cost_estimate
                by_model[model]["total_time_ms"] += exec.metrics.execution_time_ms
        
        return {
            "workspace_id": workspace_id,
            "agent_type": agent_type,
            "total_executions": len(executions),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "average_tokens_per_execution": total_tokens // len(executions),
            "average_cost_per_execution": total_cost / len(executions),
            "average_execution_time_ms": sum(execution_times) // len(execution_times) if execution_times else 0,
            "min_execution_time_ms": min(execution_times) if execution_times else 0,
            "max_execution_time_ms": max(execution_times) if execution_times else 0,
            "by_model": by_model
        }
    
    async def get_recent_executions(
        self, workspace_id: UUID, limit: int = 20, agent_type: Optional[str] = None
    ) -> List[AgentExecution]:
        """Get recent executions for a workspace."""
        executions = await self.agent_repository.get_executions_by_workspace(workspace_id, agent_type)
        
        # Sort by creation date, most recent first
        executions.sort(key=lambda e: e.created_at, reverse=True)
        
        return executions[:limit]
    
    async def get_failed_executions(self, workspace_id: UUID) -> List[AgentExecution]:
        """Get all failed executions for debugging."""
        return await self.agent_repository.get_executions_by_workspace(workspace_id, status="failed")
    
    # Helper Methods
    def _is_valid_agent_type(self, agent_type: str) -> bool:
        """Validate agent type against known types."""
        valid_types = {
            AgentType.ARC_SPLITTER,
            AgentType.WIKI_PLANNER,
            AgentType.ARTICLE_WRITER,
            AgentType.CHAPTER_BACKLINKER,
            AgentType.GENERAL_SUMMARIZER,
            AgentType.FACT_CHECKER,
            AgentType.CONSISTENCY_CHECKER,
            AgentType.STYLE_EDITOR,
            AgentType.CHARACTER_DEVELOPER,
            AgentType.PLOT_ANALYZER,
            # Test agent types
            "wikigen",
            "character_analyzer", 
            "plot_analyzer",
            "workflow_orchestrator",
            "test_agent"
        }
        return agent_type in valid_types
    
    async def cleanup_old_conversations(
        self, workspace_id: UUID, days_old: int = 30
    ) -> Dict[str, int]:
        """Clean up old conversations and executions."""
        # TODO: This would be implemented based on repository capabilities
        # For now, return a placeholder
        raise NotImplementedError("Cleanup not implemented yet")
    
    async def export_conversation_history(
        self, workspace_id: UUID, agent_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Export conversation history for analysis."""
        conversations = await self.agent_repository.get_conversations_by_workspace(workspace_id, agent_type)
        
        export_data = []
        for conv in conversations:
            executions = await self.agent_repository.get_executions_by_conversation(conv.id)
            
            export_data.append({
                "conversation_id": str(conv.id),
                "agent_type": conv.agent_type,
                "created_at": conv.created_at.isoformat(),
                "message_count": len(conv.messages),
                "execution_count": len(executions),
                "context": conv.context,
                "executions": [
                    {
                        "execution_id": str(e.id),
                        "status": e.status,
                        "input_data": e.input_data,
                        "output_data": e.output_data,
                        "metrics": e.metrics.model_dump() if e.metrics else None,
                        "created_at": e.created_at.isoformat(),
                        "completed_at": e.completed_at.isoformat() if e.completed_at else None
                    }
                    for e in executions
                ]
            })
        
        return {
            "workspace_id": str(workspace_id),
            "agent_type": agent_type,
            "export_timestamp": datetime.now(UTC).isoformat(),
            "conversation_count": len(conversations),
            "conversations": export_data
        }