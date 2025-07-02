"""
Story management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from src.api.dependencies import (
    get_story_service_dependency,
    get_current_user_id_dependency
)
from src.services.story.story_service import StoryService
from src.schemas.db.story import (
    Chapter, ChapterCreate, ChapterUpdate, ChapterStatus,
    StoryMetadata, StoryMetadataCreate, StoryMetadataUpdate
)

router = APIRouter()


@router.post("/chapters", response_model=Chapter)
async def create_chapter(
    chapter_data: ChapterCreate,
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    story_service: StoryService = Depends(get_story_service_dependency)
):
    """Create a new chapter"""
    try:
        return await story_service.create_chapter(chapter_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chapter: {str(e)}")


@router.get("/chapters/{chapter_id}", response_model=Chapter)
async def get_chapter(
    chapter_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    story_service: StoryService = Depends(get_story_service_dependency)
):
    """Get chapter by ID"""
    chapter = await story_service.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.get("/workspaces/{workspace_id}/chapters", response_model=List[Chapter])
async def get_chapters_by_workspace(
    workspace_id: UUID,
    published_only: bool = False,
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    story_service: StoryService = Depends(get_story_service_dependency)
):
    """Get chapters for a workspace"""
    try:
        return await story_service.get_chapters_by_workspace(workspace_id, published_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chapters: {str(e)}")


@router.put("/chapters/{chapter_id}", response_model=Chapter)
async def update_chapter(
    chapter_id: UUID,
    chapter_data: ChapterUpdate,
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    story_service: StoryService = Depends(get_story_service_dependency)
):
    """Update chapter"""
    try:
        return await story_service.update_chapter(chapter_id, chapter_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update chapter: {str(e)}")


@router.post("/workspaces/{workspace_id}/metadata", response_model=StoryMetadata)
async def create_story_metadata(
    workspace_id: UUID,
    metadata_data: StoryMetadataCreate,
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    story_service: StoryService = Depends(get_story_service_dependency)
):
    """Create story metadata"""
    try:
        # Ensure workspace_id matches the URL parameter
        if metadata_data.workspace_id != workspace_id:
            raise HTTPException(status_code=400, detail="Workspace ID mismatch")
        
        return await story_service.create_story_metadata(metadata_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create metadata: {str(e)}")


@router.get("/workspaces/{workspace_id}/metadata", response_model=StoryMetadata)
async def get_story_metadata(
    workspace_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    story_service: StoryService = Depends(get_story_service_dependency)
):
    """Get story metadata for workspace"""
    metadata = await story_service.get_story_metadata_by_workspace(workspace_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Story metadata not found")
    return metadata