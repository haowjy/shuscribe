"""
Comprehensive tests for WorkspaceService with memory repositories
"""

import pytest
from uuid import uuid4
from typing import Dict, Any, List

from src.schemas.db.workspace import Workspace, WorkspaceCreate, WorkspaceUpdate, Arc
from src.schemas.db.user import User
from src.services.workspace.workspace_service import WorkspaceService
from src.database.factory import RepositoryContainer


@pytest.fixture
async def workspace_service(repository_container: RepositoryContainer) -> WorkspaceService:
    """Provide WorkspaceService with memory repository."""
    return WorkspaceService(workspace_repository=repository_container.workspace)


@pytest.fixture
async def sample_user(repository_container: RepositoryContainer) -> User:
    """Create a sample user for workspace ownership."""
    from src.schemas.db.user import UserCreate
    return await repository_container.user.create_user(UserCreate(
        email="workspace_owner@example.com",
        display_name="Workspace Owner"
    ))


@pytest.fixture
async def sample_workspace(workspace_service: WorkspaceService, sample_user: User) -> Workspace:
    """Create a sample workspace for testing."""
    workspace_data = WorkspaceCreate(
        owner_id=sample_user.id,
        name="Sample Workspace",
        description="A workspace for testing",
        arcs=[
            Arc(
                name="Act 1",
                description="The beginning",
                start_chapter=1,
                end_chapter=10
            )
        ]
    )
    return await workspace_service.create_workspace(workspace_data)


class TestWorkspaceManagement:
    """Test workspace CRUD operations"""
    
    async def test_create_workspace_success(self, workspace_service: WorkspaceService, sample_user: User):
        """Test creating a new workspace"""
        workspace_data = WorkspaceCreate(
            owner_id=sample_user.id,
            name="New Workspace",
            description="A brand new workspace",
            arcs=[
                Arc(
                    name="Introduction",
                    description="Setting up the story",
                    start_chapter=1,
                    end_chapter=5
                ),
                Arc(
                    name="Rising Action",
                    description="Building tension",
                    start_chapter=6,
                    end_chapter=15
                )
            ],
            settings={"theme": "dark", "auto_save": True}
        )
        
        workspace = await workspace_service.create_workspace(workspace_data)
        
        assert workspace.id is not None
        assert workspace.owner_id == sample_user.id
        assert workspace.name == "New Workspace"
        assert workspace.description == "A brand new workspace"
        assert len(workspace.arcs) == 2
        assert workspace.arcs[0].name == "Introduction"
        assert workspace.arcs[1].name == "Rising Action"
        assert workspace.settings["theme"] == "dark"
        assert workspace.created_at is not None
    
    async def test_create_workspace_minimal(self, workspace_service: WorkspaceService, sample_user: User):
        """Test creating workspace with minimal data"""
        workspace_data = WorkspaceCreate(
            owner_id=sample_user.id,
            name="Minimal Workspace"
        )
        
        workspace = await workspace_service.create_workspace(workspace_data)
        
        assert workspace.name == "Minimal Workspace"
        assert workspace.description == ""
        assert len(workspace.arcs) == 0
        assert workspace.settings == {}
    
    async def test_get_workspace_by_id(self, workspace_service: WorkspaceService, sample_workspace: Workspace):
        """Test retrieving workspace by ID"""
        retrieved = await workspace_service.get_workspace(sample_workspace.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_workspace.id
        assert retrieved.name == sample_workspace.name
        assert len(retrieved.arcs) == len(sample_workspace.arcs)
    
    async def test_get_workspace_not_found(self, workspace_service: WorkspaceService):
        """Test retrieving non-existent workspace returns None"""
        fake_id = uuid4()
        workspace = await workspace_service.get_workspace(fake_id)
        assert workspace is None
    
    async def test_update_workspace_success(self, workspace_service: WorkspaceService, sample_workspace: Workspace):
        """Test updating workspace information"""
        update_data = WorkspaceUpdate(
            name="Updated Workspace",
            description="Updated description",
            settings={"new_setting": "value"}
        )
        
        updated = await workspace_service.update_workspace(sample_workspace.id, update_data)
        
        assert updated.name == "Updated Workspace"
        assert updated.description == "Updated description"
        assert updated.settings["new_setting"] == "value"
        assert updated.owner_id == sample_workspace.owner_id  # Unchanged
    
    async def test_update_workspace_arcs(self, workspace_service: WorkspaceService, sample_workspace: Workspace):
        """Test updating workspace arcs"""
        new_arcs = [
            Arc(
                name="New Arc 1",
                description="First new arc",
                start_chapter=1,
                end_chapter=8
            ),
            Arc(
                name="New Arc 2", 
                description="Second new arc",
                start_chapter=9,
                end_chapter=16
            )
        ]
        
        update_data = WorkspaceUpdate(arcs=new_arcs)
        updated = await workspace_service.update_workspace(sample_workspace.id, update_data)
        
        assert len(updated.arcs) == 2
        assert updated.arcs[0].name == "New Arc 1"
        assert updated.arcs[1].name == "New Arc 2"
        assert updated.arcs[0].start_chapter == 1
        assert updated.arcs[1].end_chapter == 16
    
    async def test_update_workspace_not_found(self, workspace_service: WorkspaceService):
        """Test error when updating non-existent workspace"""
        fake_id = uuid4()
        update_data = WorkspaceUpdate(name="New Name")
        
        with pytest.raises(ValueError) as exc_info:
            await workspace_service.update_workspace(fake_id, update_data)
        
        assert f"Workspace {fake_id} not found" in str(exc_info.value)
    
    async def test_delete_workspace_success(self, workspace_service: WorkspaceService, sample_workspace: Workspace):
        """Test deleting a workspace"""
        result = await workspace_service.delete_workspace(sample_workspace.id)
        assert result is True
        
        # Verify it's gone
        retrieved = await workspace_service.get_workspace(sample_workspace.id)
        assert retrieved is None
    
    async def test_delete_workspace_not_found(self, workspace_service: WorkspaceService):
        """Test deleting non-existent workspace returns False"""
        fake_id = uuid4()
        result = await workspace_service.delete_workspace(fake_id)
        assert result is False


class TestWorkspaceQueries:
    """Test workspace query operations"""
    
    async def test_get_workspaces_by_user(self, workspace_service: WorkspaceService, sample_user: User):
        """Test getting all workspaces for a user"""
        # Create multiple workspaces
        for i in range(3):
            await workspace_service.create_workspace(WorkspaceCreate(
                owner_id=sample_user.id,
                name=f"Workspace {i}",
                description=f"Description {i}"
            ))
        
        # Get workspaces for our user
        workspaces = await workspace_service.get_workspaces_by_user(sample_user.id)
        
        assert len(workspaces) == 3
        assert all(w.owner_id == sample_user.id for w in workspaces)
        names = [w.name for w in workspaces]
        assert "Workspace 0" in names
        assert "Workspace 1" in names
        assert "Workspace 2" in names
    
    async def test_get_workspace_by_name(self, workspace_service: WorkspaceService, sample_user: User):
        """Test finding workspace by name for specific user"""
        workspace1 = await workspace_service.create_workspace(WorkspaceCreate(
            owner_id=sample_user.id,
            name="Unique Name",
            description="First workspace"
        ))
        
        await workspace_service.create_workspace(WorkspaceCreate(
            owner_id=sample_user.id,
            name="Another Name",
            description="Second workspace"
        ))
        
        # Find by name
        found = await workspace_service.get_workspace_by_name(sample_user.id, "Unique Name")
        
        assert found is not None
        assert found.id == workspace1.id
        assert found.name == "Unique Name"
    
    async def test_get_workspace_by_name_not_found(self, workspace_service: WorkspaceService, sample_user: User):
        """Test searching for non-existent workspace name"""
        workspace = await workspace_service.get_workspace_by_name(sample_user.id, "Nonexistent")
        assert workspace is None
    
    
    async def test_get_workspaces_by_status(self, workspace_service: WorkspaceService, sample_user: User):
        """Test filtering workspaces by status"""
        # Create workspaces with different statuses
        active_ws = await workspace_service.create_workspace(WorkspaceCreate(
            owner_id=sample_user.id,
            name="Active Workspace",
            settings={"status": "active"}
        ))
        
        archived_ws = await workspace_service.create_workspace(WorkspaceCreate(
            owner_id=sample_user.id,
            name="Archived Workspace",
            settings={"status": "archived"}
        ))
        
        # Get active workspaces
        active_list = await workspace_service.get_workspaces_by_status("active", sample_user.id)
        assert len(active_list) >= 1
        assert any(w.id == active_ws.id for w in active_list)
        
        # Get archived workspaces
        archived_list = await workspace_service.get_workspaces_by_status("archived", sample_user.id)
        assert len(archived_list) >= 1
        assert any(w.id == archived_ws.id for w in archived_list)


class TestArcManagement:
    """Test arc-related operations"""
    
    async def test_get_arcs_by_workspace(self, workspace_service: WorkspaceService, sample_workspace: Workspace):
        """Test retrieving arcs for a workspace"""
        arcs = await workspace_service.get_arcs_by_workspace(sample_workspace.id)
        
        assert len(arcs) == 1
        assert arcs[0].name == "Act 1"
        assert arcs[0].start_chapter == 1
        assert arcs[0].end_chapter == 10
    
    async def test_get_arcs_by_chapter_range(self, workspace_service: WorkspaceService, sample_user: User):
        """Test finding arcs that overlap with chapter range"""
        # Create workspace with multiple arcs
        workspace = await workspace_service.create_workspace(WorkspaceCreate(
            owner_id=sample_user.id,
            name="Multi-Arc Workspace",
            arcs=[
                Arc(name="Arc 1", start_chapter=1, end_chapter=10),
                Arc(name="Arc 2", start_chapter=11, end_chapter=20),
                Arc(name="Arc 3", start_chapter=21, end_chapter=35)
            ]
        ))
        
        # Find arcs overlapping chapters 5-15
        overlapping = await workspace_service.get_arcs_by_chapter_range(
            workspace.id, 5, 15
        )
        
        assert len(overlapping) == 2
        arc_names = [arc.name for arc in overlapping]
        assert "Arc 1" in arc_names
        assert "Arc 2" in arc_names
        assert "Arc 3" not in arc_names


class TestProcessingState:
    """Test workspace processing state management"""
    
    async def test_update_processing_state(self, workspace_service: WorkspaceService, sample_workspace: Workspace):
        """Test updating workspace processing state"""
        state_data = {
            "current_step": "wiki_generation",
            "progress": 0.75,
            "last_error": None
        }
        
        updated = await workspace_service.update_processing_state(
            sample_workspace.id, state_data
        )
        
        assert updated.settings["current_step"] == "wiki_generation"
        assert updated.settings["progress"] == 0.75
        assert updated.settings["last_error"] is None
    
    async def test_update_last_processed_chapter(self, workspace_service: WorkspaceService, sample_workspace: Workspace):
        """Test updating last processed chapter number"""
        updated = await workspace_service.update_last_processed_chapter(
            sample_workspace.id, 15
        )
        
        assert updated.settings["last_processed_chapter"] == 15
    
    async def test_update_status(self, workspace_service: WorkspaceService, sample_workspace: Workspace):
        """Test updating workspace status"""
        updated = await workspace_service.update_status(sample_workspace.id, "processing")
        
        assert updated.settings["status"] == "processing"
    
    async def test_update_processing_state_not_found(self, workspace_service: WorkspaceService):
        """Test error when updating processing state for non-existent workspace"""
        fake_id = uuid4()
        
        with pytest.raises(ValueError) as exc_info:
            await workspace_service.update_processing_state(fake_id, {"step": "test"})
        
        assert f"Workspace {fake_id} not found" in str(exc_info.value)


class TestValidation:
    """Test workspace validation rules"""
    
    async def test_validate_arc_sequence(self, workspace_service: WorkspaceService):
        """Test validation of arc chapter sequences"""
        # This would be a more complex validation method
        # For now, just test that arcs can be created with overlapping chapters
        # In a real implementation, you might want to validate non-overlapping sequences
        
        arcs = [
            Arc(name="Arc 1", start_chapter=1, end_chapter=10),
            Arc(name="Arc 2", start_chapter=11, end_chapter=20),
            Arc(name="Arc 3", start_chapter=21, end_chapter=30)
        ]
        
        # This test would use a validation method if implemented
        # For now, just verify arcs can be created
        assert len(arcs) == 3
        assert arcs[0].end_chapter < arcs[1].start_chapter
        assert arcs[1].end_chapter < arcs[2].start_chapter


class TestIntegration:
    """Integration tests for workspace workflows"""
    
    async def test_full_workspace_lifecycle(self, workspace_service: WorkspaceService, sample_user: User):
        """Test complete workspace creation and management workflow"""
        # 1. Create workspace with arcs
        workspace = await workspace_service.create_workspace(WorkspaceCreate(
            owner_id=sample_user.id,
            name="Novel Project",
            description="A new novel project",
            arcs=[
                Arc(name="Setup", start_chapter=1, end_chapter=5),
                Arc(name="Conflict", start_chapter=6, end_chapter=15),
                Arc(name="Resolution", start_chapter=16, end_chapter=20)
            ]
        ))
        
        # 2. Update processing state
        await workspace_service.update_status(workspace.id, "active")
        await workspace_service.update_last_processed_chapter(workspace.id, 0)
        
        # 3. Simulate progression
        await workspace_service.update_last_processed_chapter(workspace.id, 10)
        await workspace_service.update_processing_state(workspace.id, {
            "current_step": "chapter_analysis",
            "progress": 0.5
        })
        
        # 4. Update workspace details
        updated = await workspace_service.update_workspace(workspace.id, WorkspaceUpdate(
            description="An evolving novel project with rich character development"
        ))
        
        # 5. Verify final state
        final = await workspace_service.get_workspace(workspace.id)
        assert final is not None
        assert final.name == "Novel Project"
        assert final.description == "An evolving novel project with rich character development"
        assert final.settings["status"] == "active"
        assert final.settings["last_processed_chapter"] == 10
        assert final.settings["current_step"] == "chapter_analysis"
        assert final.settings["progress"] == 0.5
        assert len(final.arcs) == 3
        
        # 6. Test arc queries
        arcs = await workspace_service.get_arcs_by_workspace(workspace.id)
        assert len(arcs) == 3
        
        # 7. Test chapter range queries
        mid_arcs = await workspace_service.get_arcs_by_chapter_range(workspace.id, 8, 12)
        assert len(mid_arcs) == 1
        assert mid_arcs[0].name == "Conflict"
    
    async def test_workspace_isolation(self, workspace_service: WorkspaceService, sample_user: User):
        """Test that workspaces are properly isolated"""
        # Create two workspaces
        ws1 = await workspace_service.create_workspace(WorkspaceCreate(
            owner_id=sample_user.id,
            name="Workspace 1",
            arcs=[Arc(name="Arc 1A", start_chapter=1, end_chapter=10)]
        ))
        
        ws2 = await workspace_service.create_workspace(WorkspaceCreate(
            owner_id=sample_user.id,
            name="Workspace 2",
            arcs=[Arc(name="Arc 2A", start_chapter=1, end_chapter=5)]
        ))
        
        # Update processing state for each
        await workspace_service.update_status(ws1.id, "processing")
        await workspace_service.update_status(ws2.id, "active")
        
        # Verify isolation
        ws1_final = await workspace_service.get_workspace(ws1.id)
        ws2_final = await workspace_service.get_workspace(ws2.id)
        
        assert ws1_final is not None
        assert ws2_final is not None
        assert ws1_final.settings["status"] == "processing"
        assert ws2_final.settings["status"] == "active"
        
        ws1_arcs = await workspace_service.get_arcs_by_workspace(ws1.id)
        ws2_arcs = await workspace_service.get_arcs_by_workspace(ws2.id)
        
        assert len(ws1_arcs) == 1
        assert len(ws2_arcs) == 1
        assert ws1_arcs[0].name == "Arc 1A"
        assert ws2_arcs[0].name == "Arc 2A"