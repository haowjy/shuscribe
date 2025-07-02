"""Memory-based agent repository implementation for testing and development."""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import UTC, datetime

from src.database.interfaces.agent_repository import IAgentRepository
from src.schemas.db.agent import (
    AgentConversation,
    AgentConversationCreate,
    AgentConversationUpdate,
    AgentMessage,
    AgentExecution,
    AgentExecutionCreate,
    AgentExecutionUpdate,
    AgentMetrics,
    UserFeedback
)


class MemoryAgentRepository(IAgentRepository):
    """In-memory implementation of agent repository for testing."""
    
    def __init__(self):
        self._conversations: Dict[UUID, AgentConversation] = {}
        self._executions: Dict[UUID, AgentExecution] = {}
        self._user_feedback: Dict[UUID, UserFeedback] = {}  # execution_id -> feedback
    
    # Agent Conversation CRUD
    async def create_conversation(
        self, conversation_data: AgentConversationCreate
    ) -> AgentConversation:
        """Create a new agent conversation"""
        conversation_id = uuid4()
        now = datetime.now(UTC)
        
        conversation = AgentConversation(
            id=conversation_id,
            workspace_id=conversation_data.workspace_id,
            agent_type=conversation_data.agent_type,
            conversation_id=conversation_data.conversation_id,
            context=conversation_data.context,
            messages=conversation_data.messages,
            metadata=conversation_data.metadata,
            created_at=now,
            updated_at=now
        )
        
        self._conversations[conversation_id] = conversation
        return conversation
    
    async def get_conversation(self, conversation_id: UUID) -> Optional[AgentConversation]:
        """Get a specific conversation by ID"""
        return self._conversations.get(conversation_id)
    
    async def update_conversation(
        self, conversation_id: UUID, conversation_data: AgentConversationUpdate
    ) -> AgentConversation:
        """Update a conversation's context or metadata"""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Build update dict manually to preserve object types
        update_dict = {}
        if conversation_data.agent_type is not None:
            update_dict['agent_type'] = conversation_data.agent_type
        if conversation_data.conversation_id is not None:
            update_dict['conversation_id'] = conversation_data.conversation_id
        if conversation_data.context is not None:
            update_dict['context'] = conversation_data.context
        if conversation_data.messages is not None:
            update_dict['messages'] = conversation_data.messages
        if conversation_data.metadata is not None:
            update_dict['metadata'] = conversation_data.metadata
        
        update_dict['updated_at'] = datetime.now(UTC)
        
        updated_conversation = conversation.model_copy(update=update_dict)
        self._conversations[conversation_id] = updated_conversation
        return updated_conversation
    
    async def delete_conversation(self, conversation_id: UUID) -> bool:
        """Delete a conversation"""
        if conversation_id in self._conversations:
            # Clean up related executions
            executions_to_delete = [
                exec_id for exec_id, execution in self._executions.items()
                if execution.conversation_id == conversation_id
            ]
            for exec_id in executions_to_delete:
                del self._executions[exec_id]
                # Clean up feedback for those executions
                self._user_feedback.pop(exec_id, None)
            
            del self._conversations[conversation_id]
            return True
        return False
    
    # Simple Conversation Queries
    async def get_conversations_by_workspace(
        self, 
        workspace_id: UUID, 
        agent_type: Optional[str] = None,
        offset: int = 0,
        limit: int = 50
    ) -> List[AgentConversation]:
        """Get conversations for a workspace, optionally filtered by agent type"""
        conversations = []
        for conversation in self._conversations.values():
            if conversation.workspace_id == workspace_id:
                if agent_type is None or conversation.agent_type == agent_type:
                    conversations.append(conversation)
        
        # Sort by created_at descending (newest first)
        conversations.sort(key=lambda c: c.created_at, reverse=True)
        return conversations[offset:offset + limit]
    
    async def get_conversations_by_agent_type(
        self, workspace_id: UUID, agent_type: str
    ) -> List[AgentConversation]:
        """Get all conversations for a specific agent type"""
        conversations = []
        for conversation in self._conversations.values():
            if (conversation.workspace_id == workspace_id and 
                conversation.agent_type == agent_type):
                conversations.append(conversation)
        
        conversations.sort(key=lambda c: c.created_at, reverse=True)
        return conversations
    
    # Agent Message Operations
    async def add_message_to_conversation(
        self, conversation_id: UUID, message: AgentMessage
    ) -> AgentConversation:
        """Add a message to an existing conversation"""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Add message to the conversation
        updated_messages = conversation.messages.copy()
        updated_messages.append(message)
        
        updated_conversation = conversation.model_copy(update={
            'messages': updated_messages,
            'updated_at': datetime.now(UTC)
        })
        
        self._conversations[conversation_id] = updated_conversation
        return updated_conversation
    
    async def get_conversation_messages(
        self, conversation_id: UUID
    ) -> List[AgentMessage]:
        """Get all messages for a conversation"""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return []
        return conversation.messages
    
    # Agent Execution CRUD
    async def create_execution(
        self, execution_data: AgentExecutionCreate
    ) -> AgentExecution:
        """Create a new agent execution record"""
        execution_id = uuid4()
        now = datetime.now(UTC)
        
        execution = AgentExecution(
            id=execution_id,
            workspace_id=execution_data.workspace_id,
            agent_type=execution_data.agent_type,
            execution_id=execution_data.execution_id,
            conversation_id=execution_data.conversation_id,
            input_data=execution_data.input_data,
            output_data=execution_data.output_data,
            status=execution_data.status,
            error_message=execution_data.error_message,
            metadata=execution_data.metadata,
            metrics=execution_data.metrics,
            created_at=now,
            started_at=execution_data.started_at,
            completed_at=execution_data.completed_at
        )
        
        self._executions[execution_id] = execution
        return execution
    
    async def get_execution(self, execution_id: UUID) -> Optional[AgentExecution]:
        """Get a specific execution by ID"""
        return self._executions.get(execution_id)
    
    async def update_execution(
        self, execution_id: UUID, execution_data: AgentExecutionUpdate
    ) -> AgentExecution:
        """Update an execution record"""
        execution = self._executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        # Build update dict manually to preserve object types
        update_dict = {}
        if execution_data.agent_type is not None:
            update_dict['agent_type'] = execution_data.agent_type
        if execution_data.execution_id is not None:
            update_dict['execution_id'] = execution_data.execution_id
        if execution_data.input_data is not None:
            update_dict['input_data'] = execution_data.input_data
        if execution_data.output_data is not None:
            update_dict['output_data'] = execution_data.output_data
        if execution_data.status is not None:
            update_dict['status'] = execution_data.status
        if execution_data.error_message is not None:
            update_dict['error_message'] = execution_data.error_message
        if execution_data.metadata is not None:
            update_dict['metadata'] = execution_data.metadata
        if execution_data.metrics is not None:
            update_dict['metrics'] = execution_data.metrics
        if execution_data.started_at is not None:
            update_dict['started_at'] = execution_data.started_at
        if execution_data.completed_at is not None:
            update_dict['completed_at'] = execution_data.completed_at
        
        # Set completed_at if status is changing to completed
        if (update_dict.get('status') in ['completed', 'failed'] and 
            execution.status not in ['completed', 'failed'] and
            'completed_at' not in update_dict):
            update_dict['completed_at'] = datetime.now(UTC)
        
        updated_execution = execution.model_copy(update=update_dict)
        self._executions[execution_id] = updated_execution
        return updated_execution
    
    async def delete_execution(self, execution_id: UUID) -> bool:
        """Delete an execution record"""
        if execution_id in self._executions:
            # Clean up related feedback
            self._user_feedback.pop(execution_id, None)
            del self._executions[execution_id]
            return True
        return False
    
    # Simple Execution Queries
    async def get_executions_by_workspace(
        self,
        workspace_id: UUID,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[AgentExecution]:
        """Get executions with optional filters"""
        executions = []
        for execution in self._executions.values():
            if execution.workspace_id == workspace_id:
                if agent_type is None or execution.agent_type == agent_type:
                    if status is None or execution.status == status:
                        executions.append(execution)
        
        # Sort by created_at descending (newest first)
        executions.sort(key=lambda e: e.created_at, reverse=True)
        return executions[offset:offset + limit]
    
    async def get_executions_by_conversation(
        self, conversation_id: UUID
    ) -> List[AgentExecution]:
        """Get all executions for a conversation"""
        executions = []
        for execution in self._executions.values():
            if execution.conversation_id == conversation_id:
                executions.append(execution)
        
        executions.sort(key=lambda e: e.created_at)
        return executions
    
    async def get_executions_by_status(
        self, workspace_id: UUID, status: str
    ) -> List[AgentExecution]:
        """Get executions filtered by status"""
        executions = []
        for execution in self._executions.values():
            if (execution.workspace_id == workspace_id and 
                execution.status == status):
                executions.append(execution)
        
        executions.sort(key=lambda e: e.created_at, reverse=True)
        return executions
    
    async def get_executions_by_date_range(
        self, 
        workspace_id: UUID, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[AgentExecution]:
        """Get executions within a date range"""
        executions = []
        for execution in self._executions.values():
            if (execution.workspace_id == workspace_id and
                start_date <= execution.created_at <= end_date):
                executions.append(execution)
        
        executions.sort(key=lambda e: e.created_at)
        return executions
    
    # User Feedback CRUD
    async def create_user_feedback(
        self, feedback_data: UserFeedback
    ) -> UserFeedback:
        """Store user feedback for an execution"""
        # UserFeedback already has an execution_id, so we use that as the key
        feedback = feedback_data.model_copy()
        self._user_feedback[feedback.execution_id] = feedback
        return feedback
    
    async def get_user_feedback(
        self, execution_id: UUID
    ) -> Optional[UserFeedback]:
        """Get user feedback for a specific execution"""
        return self._user_feedback.get(execution_id)
    
    async def update_user_feedback(
        self, execution_id: UUID, feedback_data: UserFeedback
    ) -> UserFeedback:
        """Update user feedback"""
        feedback = self._user_feedback.get(execution_id)
        if not feedback:
            raise ValueError(f"User feedback not found for execution {execution_id}")
        
        # For feedback updates, we replace the entire feedback object
        updated_feedback = feedback_data.model_copy()
        self._user_feedback[execution_id] = updated_feedback
        return updated_feedback
    
    async def delete_user_feedback(self, execution_id: UUID) -> bool:
        """Delete user feedback"""
        if execution_id in self._user_feedback:
            del self._user_feedback[execution_id]
            return True
        return False
    
    # Simple Feedback Queries
    async def get_feedback_by_workspace(
        self, workspace_id: UUID
    ) -> List[UserFeedback]:
        """Get all feedback for a workspace"""
        feedback_list = []
        for feedback in self._user_feedback.values():
            # Need to check if the execution belongs to this workspace
            execution = self._executions.get(feedback.execution_id)
            if execution and execution.workspace_id == workspace_id:
                feedback_list.append(feedback)
        
        feedback_list.sort(key=lambda f: f.created_at, reverse=True)
        return feedback_list
    
    async def get_feedback_by_rating(
        self, workspace_id: UUID, min_rating: int, max_rating: int
    ) -> List[UserFeedback]:
        """Get feedback within a rating range"""
        feedback_list = []
        for feedback in self._user_feedback.values():
            execution = self._executions.get(feedback.execution_id)
            if (execution and execution.workspace_id == workspace_id and
                feedback.rating is not None and
                min_rating <= feedback.rating <= max_rating):
                feedback_list.append(feedback)
        
        feedback_list.sort(key=lambda f: f.created_at, reverse=True)
        return feedback_list
    
    # Cleanup Operations
    async def delete_old_conversations(
        self, workspace_id: UUID, cutoff_date: datetime
    ) -> int:
        """Delete conversations older than cutoff date, return count deleted"""
        conversations_to_delete = []
        for conversation_id, conversation in self._conversations.items():
            if (conversation.workspace_id == workspace_id and 
                conversation.created_at < cutoff_date):
                conversations_to_delete.append(conversation_id)
        
        for conversation_id in conversations_to_delete:
            await self.delete_conversation(conversation_id)
        
        return len(conversations_to_delete)
    
    async def delete_old_executions(
        self, workspace_id: UUID, cutoff_date: datetime
    ) -> int:
        """Delete executions older than cutoff date, return count deleted"""
        executions_to_delete = []
        for execution_id, execution in self._executions.items():
            if (execution.workspace_id == workspace_id and 
                execution.created_at < cutoff_date):
                executions_to_delete.append(execution_id)
        
        for execution_id in executions_to_delete:
            await self.delete_execution(execution_id)
        
        return len(executions_to_delete)
    
    # Bulk Operations
    async def bulk_create_executions(
        self, executions: List[AgentExecutionCreate]
    ) -> List[AgentExecution]:
        """Create multiple executions in one operation"""
        created_executions = []
        for execution_data in executions:
            execution = await self.create_execution(execution_data)
            created_executions.append(execution)
        return created_executions
    
    async def bulk_update_execution_status(
        self, execution_ids: List[UUID], status: str
    ) -> List[AgentExecution]:
        """Update status for multiple executions"""
        updated_executions = []
        for execution_id in execution_ids:
            execution = self._executions.get(execution_id)
            if execution:
                update_data = AgentExecutionUpdate(status=status)
                updated_execution = await self.update_execution(execution_id, update_data)
                updated_executions.append(updated_execution)
        return updated_executions