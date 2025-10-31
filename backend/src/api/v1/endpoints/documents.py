# backend/src/api/v1/endpoints/documents.py
"""
Document API endpoints matching frontend expectations
"""
import logging
from typing import List  # noqa: F401 (kept for future pagination typing)
from datetime import datetime, UTC

from fastapi import APIRouter, HTTPException, status, Depends
 

from src.database.factory import get_repositories
from src.database.interfaces.models import Document, Tag
from src.schemas.responses.tags import TagInfo
from src.schemas.responses.documents import (
    DocumentResponse,
    DocumentContent as ResponseDocumentContent,
    DeleteResponse,
)
from src.schemas.requests.documents import CreateDocumentRequest, UpdateDocumentRequest
from src.api.dependencies import get_current_user_id
from src.utils.path_utils import validate_document_path, ensure_folder_hierarchy_exists
from src.utils.md_indexing import count_words as count_words_from_text, derive_index_markdown

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================


def tag_to_info(tag: Tag | str) -> TagInfo:
    """Convert Tag model or tag ID string to TagInfo response"""
    if isinstance(tag, str):
        # For domain models where only tag IDs are stored, we only know the ID here.
        # Name/icon/color should be hydrated by tag endpoints if needed.
        return TagInfo(id=tag, name=tag, icon=None, color=None)
    else:
        return TagInfo(id=tag.id, name=tag.name, icon=tag.icon, color=tag.color)


"""
NOTE: Request/response schemas are defined in src/schemas/{requests,responses}/documents.py.
This module only adapts them to repo inputs/outputs.
"""


 


# ============================================================================
# Helper Functions
# ============================================================================


def _compute_word_count_from_content(text: str) -> int:
    return count_words_from_text(text)


 


def document_to_response(document: Document) -> DocumentResponse:
    """Convert Document model to DocumentResponse"""
    # Handle tags - in domain models they are tag IDs (List[str])
    tags = [tag_to_info(tag_id) for tag_id in getattr(document, "tag_ids", [])]

    index_md = derive_index_markdown(getattr(document, "content", ""))
    content = ResponseDocumentContent(
        content=getattr(document, "content", ""),
        format="md",
        word_count=getattr(document, "word_count", 0),
        preview=(getattr(document, "content", "")[:200] if getattr(document, "content", "") else None),
        summary=None,
        index_markdown_present=bool(index_md),
        last_indexed_at=(
            document.last_indexed_at.isoformat()
            if getattr(document, "last_indexed_at", None) and hasattr(document.last_indexed_at, "isoformat")
            else str(getattr(document, "last_indexed_at", "")) if getattr(document, "last_indexed_at", None) else None
        ),
    )

    return DocumentResponse(
        id=document.id,
        project_id=document.project_id,
        title=document.title,
        path=document.path,
        content=content,
        tags=tags,
        word_count=document.word_count,
        created_at=(
            document.created_at.isoformat()
            if document.created_at and hasattr(document.created_at, "isoformat")
            else str(document.created_at) if document.created_at else ""
        ),
        updated_at=(
            document.updated_at.isoformat()
            if document.updated_at and hasattr(document.updated_at, "isoformat")
            else str(document.updated_at) if document.updated_at else ""
        ),
        version=document.version,
        is_locked=document.is_locked,
        locked_by=document.locked_by,
        file_tree_id=document.file_tree_id,
    )



# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, user_id: str = Depends(get_current_user_id)) -> DocumentResponse:
    """
    Get document by ID

    Matches frontend expectation: GET /documents/{documentId}
    """
    try:
        repos = get_repositories()
        document = await repos.document.get_by_id(document_id)

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Document with ID {document_id} not found"
            )

        logger.info(f"Retrieved document: {document.title} (ID: {document_id})")
        return document_to_response(document)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document {document_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("", response_model=DocumentResponse)
async def create_document(
    request: CreateDocumentRequest, user_id: str = Depends(get_current_user_id)
) -> DocumentResponse:
    """
    Create a new document

    Matches frontend expectation: POST /documents

    Important field distinctions:
    - title: Display name for the document (e.g., "Chapter 1: The Beginning" or "story.md")
    - path: Organizational path in file tree (e.g., "/chapters/chapter-1") - used for structure
    - content: Plaintext Markdown (no JSX)
    
    The system now automatically creates missing folders from the document path.
    For example, if path="/characters/locations/taverns/prancing-pony", the folders
    "/characters", "/characters/locations", and "/characters/locations/taverns"
    will be created automatically if they don't exist.
    """
    try:
        repos = get_repositories()

        # Validate document path
        is_valid_path, path_error = validate_document_path(request.path)
        if not is_valid_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Invalid document path: {path_error}"
            )

        # Verify project exists
        project = await repos.project.get_by_id(request.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with ID {request.project_id} not found"
            )

        # Auto-create folder hierarchy from path
        parent_folder_id = await ensure_folder_hierarchy_exists(
            request.project_id, 
            request.path, 
            repos.file_tree
        )

        # Read content from wrapper
        incoming_content = request.content.content if request.content is not None else ""

        # Compute word count and index markdown from plaintext content
        word_count = _compute_word_count_from_content(incoming_content)
        index_md = derive_index_markdown(incoming_content)

        # Prepare document data
        document_data = {
            "project_id": request.project_id,
            "title": request.title,
            "path": request.path,
            "content": incoming_content,
            # Note: tags will be assigned after document creation via relationship
            "word_count": word_count,
            "index_markdown": index_md,
            "last_indexed_at": datetime.now(UTC).replace(tzinfo=None),
            "version": "1.0.0",
            "is_locked": False,
            "file_tree_id": parent_folder_id,  # Auto-determined from path
        }

        # Create document
        document = await repos.document.create(document_data)

        # Assign tag relationships if provided
        if request.tag_ids:
            await repos.document.update(document.id, {"tag_ids": request.tag_ids})
            updated_document = await repos.document.get_by_id(document.id)
            if updated_document:
                document = updated_document

        # Update project document count
        await repos.project.update(
            request.project_id,
            {
                "document_count": project.document_count + 1,
                "word_count": project.word_count + word_count,
            },
        )

        logger.info(f"Created document: {document.title} (ID: {document.id}) for project {request.project_id}")
        return document_to_response(document)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str, request: UpdateDocumentRequest, user_id: str = Depends(get_current_user_id)
) -> DocumentResponse:
    """
    Update an existing document

    Matches frontend expectation: PUT /documents/{documentId}

    Important field distinctions:
    - title: Display name for the document (e.g., "Chapter 1: The Beginning" or "story.md")
    - content: Plaintext Markdown (no JSX)
    """
    try:
        repos = get_repositories()

        # Check if document exists
        existing_document = await repos.document.get_by_id(document_id)
        if not existing_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Document with ID {document_id} not found"
            )

        # Prepare updates
        updates = {}
        old_word_count = existing_document.word_count
        new_word_count = old_word_count

        if request.title is not None:
            updates["title"] = request.title
        if request.content is not None:
            updates["content"] = request.content.content or ""
            new_word_count = _compute_word_count_from_content(request.content.content or "")
            updates["word_count"] = new_word_count
            updates["index_markdown"] = derive_index_markdown(request.content.content or "")
            updates["last_indexed_at"] = datetime.now(UTC).replace(tzinfo=None)
        if request.tag_ids is not None:
            updates["tag_ids"] = request.tag_ids
        if request.version is not None:
            updates["version"] = request.version

        # Update document
        updated_document = await repos.document.update(document_id, updates)

        if updated_document is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update document: Updated document not returned",
            )

        # Update project word count if content changed
        if new_word_count != old_word_count:
            project = await repos.project.get_by_id(existing_document.project_id)
            if project:
                await repos.project.update(
                    existing_document.project_id,
                    {
                        "word_count": project.word_count - old_word_count + new_word_count,
                    },
                )

        logger.info(f"Updated document: {document_id} for project {existing_document.project_id}")
        return document_to_response(updated_document)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document {document_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{document_id}", response_model=DeleteResponse)
async def delete_document(document_id: str, user_id: str = Depends(get_current_user_id)) -> DeleteResponse:
    """
    Delete a document

    Matches frontend expectation: DELETE /documents/{documentId}
    """
    try:
        repos = get_repositories()

        # Check if document exists and get its project ID and word count for project update
        existing_document = await repos.document.get_by_id(document_id)
        if not existing_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Document with ID {document_id} not found"
            )

        # Delete document
        success = await repos.document.delete(document_id)

        if success:
            # Update project document count and word count
            project = await repos.project.get_by_id(existing_document.project_id)
            if project:
                await repos.project.update(
                    existing_document.project_id,
                    {
                        "document_count": project.document_count - 1,
                        "word_count": project.word_count - existing_document.word_count,
                    },
                )

            logger.info(f"Deleted document: {document_id} from project {existing_document.project_id}")
            return DeleteResponse(success=True, message="Document deleted", deleted_count=1)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete document")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
