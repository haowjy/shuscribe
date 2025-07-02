"""
Comprehensive tests for AgentService with memory repositories
"""

import pytest
from uuid import uuid4
from datetime import datetime, UTC
from typing import Dict, Any, List

from src.schemas.db.agent import (
    AgentConversation, AgentConversationCreate, AgentConversationUpdate,
    AgentExecution, AgentExecutionCreate, AgentExecutionUpdate,
    AgentMessage
)
from src.schemas.db.workspace import Workspace
from src.services.agent.agent_service import AgentService
from src.database.factory import RepositoryContainer


@pytest.fixture
async def agent_service(repository_container: RepositoryContainer) -> AgentService:
    """Provide AgentService with memory repositories."""
    return AgentService(
        agent_repository=repository_container.agent,
        workspace_repository=repository_container.workspace
    )


@pytest.fixture
async def sample_workspace(repository_container: RepositoryContainer) -> Workspace:
    """Create a sample workspace for agent operations."""
    from src.schemas.db.user import UserCreate
    from src.schemas.db.workspace import WorkspaceCreate
    
    user = await repository_container.user.create_user(UserCreate(
        email="agent_user@example.com",
        display_name="Agent User"
    ))
    
    return await repository_container.workspace.create_workspace(WorkspaceCreate(
        owner_id=user.id,
        name="Agent Workspace",
        description="Workspace for agent testing"
    ))


@pytest.fixture
async def sample_conversation(agent_service: AgentService, sample_workspace: Workspace) -> AgentConversation:
    """Create a sample agent conversation for testing."""
    conversation_data = AgentConversationCreate(
        workspace_id=sample_workspace.id,
        agent_type="wikigen",
        conversation_id="test_conversation",
        messages=[
            AgentMessage(
                role="user",
                content="Please generate a wiki for my story",
                timestamp=datetime.now(UTC)
            )
        ],
        metadata={"purpose": "wiki_generation", "priority": "high"}
    )
    return await agent_service.create_conversation(conversation_data)


@pytest.fixture
async def sample_execution(agent_service: AgentService, sample_workspace: Workspace) -> AgentExecution:
    """Create a sample agent execution for testing."""
    execution_data = AgentExecutionCreate(
        workspace_id=sample_workspace.id,
        agent_type="wikigen",
        execution_id="test_execution",
        input_data={"chapters": [1, 2, 3], "arc": "introduction"},
        output_data={},
        status="pending",
        metadata={"auto_started": True}
    )
    return await agent_service.create_execution(execution_data)


class TestConversationManagement:
    """Test agent conversation CRUD operations"""
    
    async def test_create_conversation_success(self, agent_service: AgentService, sample_workspace: Workspace):
        """Test creating a new agent conversation"""
        messages = [
            AgentMessage(
                role="user",
                content="Generate character profiles for my story",
                timestamp=datetime.now(UTC)
            ),
            AgentMessage(
                role="assistant", 
                content="I'll help you create character profiles. Let me analyze your story.",
                timestamp=datetime.now(UTC)
            )
        ]
        
        conversation_data = AgentConversationCreate(
            workspace_id=sample_workspace.id,
            agent_type="character_analyzer",
            conversation_id="char_analysis_001",
            messages=messages,
            metadata={"analysis_type": "character", "depth": "detailed"}
        )
        
        conversation = await agent_service.create_conversation(conversation_data)
        
        assert conversation.id is not None
        assert conversation.workspace_id == sample_workspace.id
        assert conversation.agent_type == "character_analyzer"
        assert conversation.conversation_id == "char_analysis_001"
        assert len(conversation.messages) == 2
        assert conversation.messages[0].role == "user"
        assert conversation.messages[1].role == "assistant"
        assert conversation.metadata["analysis_type"] == "character"
        assert conversation.created_at is not None
    
    async def test_create_conversation_workspace_not_found(self, agent_service: AgentService):
        """Test error when creating conversation for non-existent workspace"""
        fake_workspace_id = uuid4()
        conversation_data = AgentConversationCreate(
            workspace_id=fake_workspace_id,
            agent_type="test_agent",
            conversation_id="test_conv"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await agent_service.create_conversation(conversation_data)
        
        assert f"Workspace {fake_workspace_id} not found" in str(exc_info.value)
    
    async def test_get_conversation_by_id(self, agent_service: AgentService, sample_conversation: AgentConversation):
        """Test retrieving conversation by ID"""
        retrieved = await agent_service.get_conversation(sample_conversation.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_conversation.id
        assert retrieved.agent_type == sample_conversation.agent_type
        assert retrieved.conversation_id == sample_conversation.conversation_id
        assert len(retrieved.messages) == len(sample_conversation.messages)
    
    async def test_get_conversation_not_found(self, agent_service: AgentService):
        """Test retrieving non-existent conversation returns None"""
        fake_id = uuid4()
        conversation = await agent_service.get_conversation(fake_id)
        assert conversation is None
    
    async def test_update_conversation_success(self, agent_service: AgentService, sample_conversation: AgentConversation):
        """Test updating conversation with new messages"""
        new_message = AgentMessage(
            role="assistant",
            content="I've analyzed your story and identified key themes.",
            timestamp=datetime.now(UTC)
        )
        
        update_data = AgentConversationUpdate(
            messages=sample_conversation.messages + [new_message],
            metadata={"purpose": "wiki_generation", "priority": "high", "status": "in_progress"}
        )
        
        updated = await agent_service.update_conversation(sample_conversation.id, update_data)
        
        assert len(updated.messages) == 2
        assert updated.messages[1].content == "I've analyzed your story and identified key themes."
        assert updated.metadata["status"] == "in_progress"
    
    async def test_update_conversation_not_found(self, agent_service: AgentService):
        """Test error when updating non-existent conversation"""
        fake_id = uuid4()
        update_data = AgentConversationUpdate(metadata={"test": "value"})
        
        with pytest.raises(ValueError) as exc_info:
            await agent_service.update_conversation(fake_id, update_data)
        
        assert f"Conversation {fake_id} not found" in str(exc_info.value)
    
    async def test_delete_conversation_success(self, agent_service: AgentService, sample_conversation: AgentConversation):
        """Test deleting a conversation"""
        result = await agent_service.delete_conversation(sample_conversation.id)
        assert result is True
        
        # Verify it's gone
        retrieved = await agent_service.get_conversation(sample_conversation.id)
        assert retrieved is None
    
    async def test_delete_conversation_not_found(self, agent_service: AgentService):
        """Test deleting non-existent conversation returns False"""
        fake_id = uuid4()
        result = await agent_service.delete_conversation(fake_id)
        assert result is False
    
    async def test_get_conversations_by_workspace(self, agent_service: AgentService, sample_workspace: Workspace):
        """Test getting all conversations for a workspace"""
        # Create multiple conversations
        agent_types = ["wikigen", "character_analyzer", "plot_analyzer"]
        created_conversations = []
        
        for i, agent_type in enumerate(agent_types):
            conversation = await agent_service.create_conversation(AgentConversationCreate(
                workspace_id=sample_workspace.id,
                agent_type=agent_type,
                conversation_id=f"conv_{i}",
                messages=[AgentMessage(
                    role="user",
                    content=f"Test message {i}",
                    timestamp=datetime.now(UTC)
                )]
            ))
            created_conversations.append(conversation)
        
        # Get all conversations
        conversations = await agent_service.get_conversations_by_workspace(sample_workspace.id)
        
        assert len(conversations) == 3
        agent_types_found = [c.agent_type for c in conversations]
        assert "wikigen" in agent_types_found
        assert "character_analyzer" in agent_types_found
        assert "plot_analyzer" in agent_types_found
    
    async def test_get_conversations_by_agent_type(self, agent_service: AgentService, sample_workspace: Workspace):
        """Test filtering conversations by agent type"""
        # Create conversations of different types
        await agent_service.create_conversation(AgentConversationCreate(
            workspace_id=sample_workspace.id,
            agent_type="wikigen",
            conversation_id="wiki_conv_1"
        ))
        
        await agent_service.create_conversation(AgentConversationCreate(
            workspace_id=sample_workspace.id,
            agent_type="character_analyzer",
            conversation_id="char_conv_1"
        ))
        
        await agent_service.create_conversation(AgentConversationCreate(
            workspace_id=sample_workspace.id,
            agent_type="wikigen",
            conversation_id="wiki_conv_2"
        ))
        
        # Get only wikigen conversations
        wikigen_conversations = await agent_service.get_conversations_by_agent_type(
            sample_workspace.id, "wikigen"
        )
        
        assert len(wikigen_conversations) == 2
        assert all(c.agent_type == "wikigen" for c in wikigen_conversations)
        conv_ids = [c.conversation_id for c in wikigen_conversations]
        assert "wiki_conv_1" in conv_ids
        assert "wiki_conv_2" in conv_ids


class TestExecutionManagement:
    """Test agent execution CRUD operations"""
    
    async def test_create_execution_success(self, agent_service: AgentService, sample_workspace: Workspace):
        """Test creating a new agent execution"""
        execution_data = AgentExecutionCreate(
            workspace_id=sample_workspace.id,
            agent_type="arc_splitter",
            execution_id="arc_split_001",
            input_data={"story_content": "Full story text...", "target_arcs": 3},
            output_data={},
            status="pending",
            metadata={"auto_retry": True, "max_attempts": 3}
        )
        
        execution = await agent_service.create_execution(execution_data)
        
        assert execution.id is not None
        assert execution.workspace_id == sample_workspace.id
        assert execution.agent_type == "arc_splitter"
        assert execution.execution_id == "arc_split_001"
        assert execution.input_data["target_arcs"] == 3
        assert execution.status == "pending"
        assert execution.metadata["auto_retry"] is True
        assert execution.created_at is not None
    
    async def test_create_execution_workspace_not_found(self, agent_service: AgentService):
        """Test error when creating execution for non-existent workspace"""
        fake_workspace_id = uuid4()
        execution_data = AgentExecutionCreate(
            workspace_id=fake_workspace_id,
            agent_type="test_agent",
            execution_id="test_exec"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await agent_service.create_execution(execution_data)
        
        assert f"Workspace {fake_workspace_id} not found" in str(exc_info.value)
    
    async def test_get_execution_by_id(self, agent_service: AgentService, sample_execution: AgentExecution):
        """Test retrieving execution by ID"""
        retrieved = await agent_service.get_execution(sample_execution.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_execution.id
        assert retrieved.agent_type == sample_execution.agent_type
        assert retrieved.execution_id == sample_execution.execution_id
        assert retrieved.status == sample_execution.status
    
    async def test_update_execution_success(self, agent_service: AgentService, sample_execution: AgentExecution):
        """Test updating execution status and results"""
        update_data = AgentExecutionUpdate(
            status="running",
            output_data={"progress": 0.5, "current_step": "analyzing_arcs"},
            metadata={"auto_started": True, "last_checkpoint": "step_2"}
        )
        
        updated = await agent_service.update_execution(sample_execution.id, update_data)
        
        assert updated.status == "running"
        assert updated.output_data["progress"] == 0.5
        assert updated.output_data["current_step"] == "analyzing_arcs"
        assert updated.metadata["last_checkpoint"] == "step_2"
    
    async def test_update_execution_not_found(self, agent_service: AgentService):
        """Test error when updating non-existent execution"""
        fake_id = uuid4()
        update_data = AgentExecutionUpdate(status="completed")
        
        with pytest.raises(ValueError) as exc_info:
            await agent_service.update_execution(fake_id, update_data)
        
        assert f"Execution {fake_id} not found" in str(exc_info.value)
    
    async def test_get_executions_by_workspace(self, agent_service: AgentService, sample_workspace: Workspace):
        """Test getting all executions for a workspace"""
        # Create multiple executions
        execution_types = ["arc_splitter", "wiki_planner", "article_writer"]
        
        for i, exec_type in enumerate(execution_types):
            await agent_service.create_execution(AgentExecutionCreate(
                workspace_id=sample_workspace.id,
                agent_type=exec_type,
                execution_id=f"exec_{i}",
                input_data={"test": f"data_{i}"},
                status="pending"
            ))
        
        # Get all executions
        executions = await agent_service.get_executions_by_workspace(sample_workspace.id)
        
        assert len(executions) == 3
        agent_types = [e.agent_type for e in executions]
        assert "arc_splitter" in agent_types
        assert "wiki_planner" in agent_types
        assert "article_writer" in agent_types
    
    async def test_get_executions_by_status(self, agent_service: AgentService, sample_workspace: Workspace):
        """Test filtering executions by status"""
        # Create executions with different statuses
        await agent_service.create_execution(AgentExecutionCreate(
            workspace_id=sample_workspace.id,
            agent_type="test_agent",
            execution_id="pending_exec",
            status="pending"
        ))
        
        running_exec = await agent_service.create_execution(AgentExecutionCreate(
            workspace_id=sample_workspace.id,
            agent_type="test_agent",
            execution_id="running_exec",
            status="running"
        ))
        
        await agent_service.create_execution(AgentExecutionCreate(
            workspace_id=sample_workspace.id,
            agent_type="test_agent",
            execution_id="completed_exec",
            status="completed"
        ))
        
        # Get only running executions
        running_executions = await agent_service.get_executions_by_status(
            sample_workspace.id, "running"
        )
        
        assert len(running_executions) == 1
        assert running_executions[0].execution_id == "running_exec"
        assert running_executions[0].status == "running"


class TestAgentOrchestration:
    """Test agent workflow orchestration"""
    
    async def test_start_agent_workflow(self, agent_service: AgentService, sample_workspace: Workspace):
        """Test starting a complete agent workflow"""
        workflow_data = {
            "workflow_type": "full_wiki_generation",
            "input_chapters": [1, 2, 3, 4, 5],
            "target_articles": 10,
            "priority": "high"
        }
        
        # Start workflow (this would create initial execution)
        execution = await agent_service.create_execution(AgentExecutionCreate(
            workspace_id=sample_workspace.id,
            agent_type="workflow_orchestrator",
            execution_id="wiki_workflow_001",
            input_data=workflow_data,
            status="pending",
            metadata={"workflow_type": "full_wiki_generation"}
        ))
        
        assert execution.agent_type == "workflow_orchestrator"
        assert execution.input_data["workflow_type"] == "full_wiki_generation"
        assert execution.status == "pending"
    
    async def test_update_workflow_progress(self, agent_service: AgentService, sample_execution: AgentExecution):
        """Test updating workflow execution progress"""
        # Simulate workflow progression
        progress_updates = [
            {"status": "running", "progress": 0.25, "current_step": "arc_splitting"},
            {"status": "running", "progress": 0.50, "current_step": "wiki_planning"},
            {"status": "running", "progress": 0.75, "current_step": "article_writing"},
            {"status": "completed", "progress": 1.0, "current_step": "finished"}
        ]
        
        for update in progress_updates:
            updated = await agent_service.update_execution(
                sample_execution.id,
                AgentExecutionUpdate(
                    status=update["status"],
                    output_data={"progress": update["progress"], "step": update["current_step"]}
                )
            )
            
            assert updated.status == update["status"]
            assert updated.output_data["progress"] == update["progress"]
        
        # Final execution should be completed
        final = await agent_service.get_execution(sample_execution.id)
        assert final is not None
        assert final.status == "completed"
        assert final.output_data["progress"] == 1.0
    
    async def test_handle_workflow_error(self, agent_service: AgentService, sample_execution: AgentExecution):
        """Test handling workflow execution errors"""
        error_data = {
            "error": "API rate limit exceeded",
            "error_code": "RATE_LIMIT",
            "retry_after": 3600,
            "partial_results": {"completed_steps": ["arc_splitting"]}
        }
        
        # Update execution with error
        error_update = await agent_service.update_execution(
            sample_execution.id,
            AgentExecutionUpdate(
                status="error",
                output_data=error_data,
                metadata={"error_handled": True, "retry_scheduled": True}
            )
        )
        
        assert error_update.status == "error"
        assert error_update.output_data["error_code"] == "RATE_LIMIT"
        assert error_update.metadata["error_handled"] is True


class TestAgentStatistics:
    """Test agent usage statistics"""
    
    async def test_get_agent_statistics(self, agent_service: AgentService, sample_workspace: Workspace):
        """Test retrieving comprehensive agent statistics"""
        # Create conversations and executions
        for i in range(3):
            await agent_service.create_conversation(AgentConversationCreate(
                workspace_id=sample_workspace.id,
                agent_type="wikigen",
                conversation_id=f"wiki_conv_{i}"
            ))
        
        for i in range(2):
            await agent_service.create_execution(AgentExecutionCreate(
                workspace_id=sample_workspace.id,
                agent_type="wikigen",
                execution_id=f"wiki_exec_{i}",
                status="completed" if i == 0 else "running"
            ))
        
        await agent_service.create_execution(AgentExecutionCreate(
            workspace_id=sample_workspace.id,
            agent_type="character_analyzer",
            execution_id="char_exec_1",
            status="error"
        ))
        
        # Get statistics
        stats = await agent_service.get_agent_statistics(sample_workspace.id)
        
        assert stats["total_conversations"] == 3
        assert stats["total_executions"] == 3
        assert stats["completed_executions"] == 1
        assert stats["running_executions"] == 1
        assert stats["error_executions"] == 1
        assert stats["workspace_id"] == sample_workspace.id


class TestIntegration:
    """Integration tests for agent workflows"""
    
    async def test_full_agent_workflow(self, agent_service: AgentService, sample_workspace: Workspace):
        """Test complete agent interaction workflow"""
        # 1. Start with user conversation
        conversation = await agent_service.create_conversation(AgentConversationCreate(
            workspace_id=sample_workspace.id,
            agent_type="wikigen",
            conversation_id="wiki_session_001",
            messages=[
                AgentMessage(
                    role="user",
                    content="Generate a comprehensive wiki for my fantasy novel",
                    timestamp=datetime.now(UTC)
                )
            ],
            metadata={"request_type": "full_wiki", "story_genre": "fantasy"}
        ))
        
        # 2. Agent responds and starts execution
        conversation = await agent_service.update_conversation(conversation.id, AgentConversationUpdate(
            messages=conversation.messages + [
                AgentMessage(
                    role="assistant",
                    content="I'll analyze your story and create a comprehensive wiki. Starting analysis...",
                    timestamp=datetime.now(UTC)
                )
            ]
        ))
        
        # 3. Create execution for the work
        execution = await agent_service.create_execution(AgentExecutionCreate(
            workspace_id=sample_workspace.id,
            agent_type="wikigen",
            execution_id="wiki_gen_001",
            input_data={
                "story_chapters": list(range(1, 11)),
                "article_types": ["character", "location", "concept"],
                "detail_level": "comprehensive"
            },
            status="running"
        ))
        
        # 4. Simulate execution progress
        progress_steps = [
            {"progress": 0.2, "step": "analyzing_characters"},
            {"progress": 0.5, "step": "extracting_locations"},
            {"progress": 0.8, "step": "identifying_concepts"},
            {"progress": 1.0, "step": "generating_articles"}
        ]
        
        for step in progress_steps:
            await agent_service.update_execution(execution.id, AgentExecutionUpdate(
                output_data={
                    "progress": step["progress"],
                    "current_step": step["step"],
                    "articles_generated": int(step["progress"] * 15)
                }
            ))
        
        # 5. Complete execution
        final_execution = await agent_service.update_execution(execution.id, AgentExecutionUpdate(
            status="completed",
            output_data={
                "progress": 1.0,
                "articles_generated": 15,
                "character_articles": 6,
                "location_articles": 5,
                "concept_articles": 4,
                "total_words": 5000
            }
        ))
        
        # 6. Update conversation with results
        await agent_service.update_conversation(conversation.id, AgentConversationUpdate(
            messages=conversation.messages + [
                AgentMessage(
                    role="assistant",
                    content="Wiki generation completed! I've created 15 articles: 6 characters, 5 locations, and 4 concepts.",
                    timestamp=datetime.now(UTC)
                )
            ],
            metadata={"request_type": "full_wiki", "story_genre": "fantasy", "status": "completed"}
        ))
        
        # 7. Verify final state
        final_conversation = await agent_service.get_conversation(conversation.id)
        assert final_conversation is not None
        assert len(final_conversation.messages) == 3
        assert final_conversation.metadata["status"] == "completed"
        
        final_exec = await agent_service.get_execution(execution.id)
        assert final_exec is not None
        assert final_exec.status == "completed"
        assert final_exec.output_data["articles_generated"] == 15
        
        # 8. Check statistics
        stats = await agent_service.get_agent_statistics(sample_workspace.id)
        assert stats["total_conversations"] == 1
        assert stats["total_executions"] == 1
        assert stats["completed_executions"] == 1
    
    async def test_agent_error_recovery(self, agent_service: AgentService, sample_workspace: Workspace):
        """Test agent error handling and recovery"""
        # 1. Start execution that will fail
        execution = await agent_service.create_execution(AgentExecutionCreate(
            workspace_id=sample_workspace.id,
            agent_type="wikigen",
            execution_id="error_test_001",
            input_data={"chapters": [1, 2, 3]},
            status="running"
        ))
        
        # 2. Simulate error
        await agent_service.update_execution(execution.id, AgentExecutionUpdate(
            status="error",
            output_data={
                "error": "API timeout during character analysis",
                "error_code": "TIMEOUT",
                "partial_results": {"analyzed_chapters": [1, 2]}
            }
        ))
        
        # 3. Create retry execution
        retry_execution = await agent_service.create_execution(AgentExecutionCreate(
            workspace_id=sample_workspace.id,
            agent_type="wikigen",
            execution_id="error_test_001_retry",
            input_data={
                "chapters": [3],  # Only process failed chapter
                "resume_from": "error_test_001"
            },
            status="running",
            metadata={"retry_attempt": 1, "original_execution": execution.id}
        ))
        
        # 4. Complete retry successfully
        await agent_service.update_execution(retry_execution.id, AgentExecutionUpdate(
            status="completed",
            output_data={
                "progress": 1.0,
                "recovered_from_error": True,
                "total_articles": 3
            }
        ))
        
        # 5. Verify error recovery
        original = await agent_service.get_execution(execution.id)
        retry = await agent_service.get_execution(retry_execution.id)
        
        assert original is not None
        assert retry is not None
        assert original.status == "error"
        assert retry.status == "completed"
        assert retry.output_data["recovered_from_error"] is True if retry.output_data else False
        assert retry.metadata["original_execution"] == execution.id if retry.metadata else None