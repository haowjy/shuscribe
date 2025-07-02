from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from src.schemas.db.agent import (
    AgentConversation,
    AgentConversationCreate,
    AgentConversationUpdate,
    AgentMessage,
    AgentExecution,
    AgentExecutionCreate,
    AgentExecutionUpdate,
    AgentExecutionResult,
    AgentMetrics,
    UserFeedback
)


class IAgentRepository(ABC):
    """Abstract interface for agent repository - pure CRUD + simple queries"""

    # Agent Conversation CRUD
    @abstractmethod
    async def create_conversation(
        self, conversation_data: AgentConversationCreate
    ) -> AgentConversation:
        """Create a new agent conversation"""
        pass

    @abstractmethod
    async def get_conversation(self, conversation_id: UUID) -> Optional[AgentConversation]:
        """Get a specific conversation by ID"""
        pass

    @abstractmethod
    async def update_conversation(
        self, conversation_id: UUID, conversation_data: AgentConversationUpdate
    ) -> AgentConversation:
        """Update a conversation's context or metadata"""
        pass

    @abstractmethod
    async def delete_conversation(self, conversation_id: UUID) -> bool:
        """Delete a conversation"""
        pass

    # Simple Conversation Queries
    @abstractmethod
    async def get_conversations_by_workspace(
        self, 
        workspace_id: UUID, 
        agent_type: Optional[str] = None,
        offset: int = 0,
        limit: int = 50
    ) -> List[AgentConversation]:
        """Get conversations for a workspace, optionally filtered by agent type"""
        pass

    @abstractmethod
    async def get_conversations_by_agent_type(
        self, workspace_id: UUID, agent_type: str
    ) -> List[AgentConversation]:
        """Get all conversations for a specific agent type"""
        pass

    # Agent Message Operations
    @abstractmethod
    async def add_message_to_conversation(
        self, conversation_id: UUID, message: AgentMessage
    ) -> AgentConversation:
        """Add a message to an existing conversation"""
        pass

    @abstractmethod
    async def get_conversation_messages(
        self, conversation_id: UUID
    ) -> List[AgentMessage]:
        """Get all messages for a conversation"""
        pass

    # Agent Execution CRUD
    @abstractmethod
    async def create_execution(
        self, execution_data: AgentExecutionCreate
    ) -> AgentExecution:
        """Create a new agent execution record"""
        pass

    @abstractmethod
    async def get_execution(self, execution_id: UUID) -> Optional[AgentExecution]:
        """Get a specific execution by ID"""
        pass

    @abstractmethod
    async def update_execution(
        self, execution_id: UUID, execution_data: AgentExecutionUpdate
    ) -> AgentExecution:
        """Update an execution record"""
        pass

    @abstractmethod
    async def delete_execution(self, execution_id: UUID) -> bool:
        """Delete an execution record"""
        pass

    # Simple Execution Queries
    @abstractmethod
    async def get_executions_by_workspace(
        self,
        workspace_id: UUID,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[AgentExecution]:
        """Get executions with optional filters"""
        pass

    @abstractmethod
    async def get_executions_by_conversation(
        self, conversation_id: UUID
    ) -> List[AgentExecution]:
        """Get all executions for a conversation"""
        pass

    @abstractmethod
    async def get_executions_by_status(
        self, workspace_id: UUID, status: str
    ) -> List[AgentExecution]:
        """Get executions filtered by status"""
        pass

    @abstractmethod
    async def get_executions_by_date_range(
        self, 
        workspace_id: UUID, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[AgentExecution]:
        """Get executions within a date range"""
        pass

    # User Feedback CRUD
    @abstractmethod
    async def create_user_feedback(
        self, feedback_data: UserFeedback
    ) -> UserFeedback:
        """Store user feedback for an execution"""
        pass

    @abstractmethod
    async def get_user_feedback(
        self, execution_id: UUID
    ) -> Optional[UserFeedback]:
        """Get user feedback for a specific execution"""
        pass

    @abstractmethod
    async def update_user_feedback(
        self, execution_id: UUID, feedback_data: UserFeedback
    ) -> UserFeedback:
        """Update user feedback"""
        pass

    @abstractmethod
    async def delete_user_feedback(self, execution_id: UUID) -> bool:
        """Delete user feedback"""
        pass

    # Simple Feedback Queries
    @abstractmethod
    async def get_feedback_by_workspace(
        self, workspace_id: UUID
    ) -> List[UserFeedback]:
        """Get all feedback for a workspace"""
        pass

    @abstractmethod
    async def get_feedback_by_rating(
        self, workspace_id: UUID, min_rating: int, max_rating: int
    ) -> List[UserFeedback]:
        """Get feedback within a rating range"""
        pass

    # Cleanup Operations
    @abstractmethod
    async def delete_old_conversations(
        self, workspace_id: UUID, cutoff_date: datetime
    ) -> int:
        """Delete conversations older than cutoff date, return count deleted"""
        pass

    @abstractmethod
    async def delete_old_executions(
        self, workspace_id: UUID, cutoff_date: datetime
    ) -> int:
        """Delete executions older than cutoff date, return count deleted"""
        pass

    # Bulk Operations
    @abstractmethod
    async def bulk_create_executions(
        self, executions: List[AgentExecutionCreate]
    ) -> List[AgentExecution]:
        """Create multiple executions in one operation"""
        pass

    @abstractmethod
    async def bulk_update_execution_status(
        self, execution_ids: List[UUID], status: str
    ) -> List[AgentExecution]:
        """Update status for multiple executions"""
        pass