# backend/src/api/v1/endpoints/documents.py
"""
Document API endpoints matching frontend expectations
"""
import logging
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, field_validator, Field

from src.database.factory import get_repositories
from src.database.models import Document, Tag
from src.schemas.base import ApiResponse
from src.schemas.responses.tags import TagInfo
from src.api.dependencies import require_auth, get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models (matching frontend API types)
# ============================================================================

class DocumentContent(BaseModel):
    """ProseMirror document content structure"""
    type: str = "doc"
    content: List[Dict[str, Any]] = []
    
    @field_validator('content', mode='before')
    @classmethod
    def validate_content(cls, v):
        """Validate and fix malformed content"""
        if isinstance(v, str):
            # Convert malformed string content to empty content
            return []
        elif not isinstance(v, list):
            # Convert other types to empty content
            return []
        return v
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """Ensure type is always 'doc' for ProseMirror documents"""
        if v != "doc":
            return "doc"
        return v


class DocumentMeta(BaseModel):
    """Document metadata"""
    model_config = {"populate_by_name": True}
    
    id: str
    project_id: str
    title: str
    path: str
    tags: List[str]
    word_count: int
    created_at: str
    updated_at: str
    version: str
    is_locked: bool
    locked_by: str | None = None
    file_tree_id: str | None = None


class DocumentResponse(DocumentMeta):
    """Complete document response including content"""
    content: DocumentContent


class CreateDocumentRequest(BaseModel):
    """Request to create a new document"""
    model_config = {"populate_by_name": True}
    
    project_id: str
    title: str
    path: str
    content: DocumentContent = DocumentContent()
    tags: List[str] = []
    file_tree_parent_id: str | None = None


class UpdateDocumentRequest(BaseModel):
    """Request to update an existing document"""
    title: str | None = None
    content: DocumentContent | None = None
    tags: List[str] | None = None
    version: str | None = None


class DeleteResponse(BaseModel):
    """Response for delete operations"""
    success: bool


# ============================================================================
# Helper Functions
# ============================================================================

def tag_to_info(tag: Tag) -> TagInfo:
    """Convert Tag model to TagInfo response"""
    return TagInfo(
        id=tag.id,
        name=tag.name,
        icon=tag.icon,
        color=tag.color
    )


def document_to_response(document: Document) -> DocumentResponse:
    """Convert Document model to DocumentResponse"""
    # Ensure content has the right structure
    content = document.content or {"type": "doc", "content": []}
    if not isinstance(content, dict):
        content = {"type": "doc", "content": []}
    
    document_content = DocumentContent(
        type=content.get("type", "doc"),
        content=content.get("content", [])
    )
    
    return DocumentResponse(
        id=document.id,
        project_id=document.project_id,
        title=document.title,
        path=document.path,
        content=document_content,
        tags=[tag_to_info(tag) for tag in document.tags],
        word_count=document.word_count,
        created_at=document.created_at.isoformat() if hasattr(document.created_at, 'isoformat') else str(document.created_at),
        updated_at=document.updated_at.isoformat() if hasattr(document.updated_at, 'isoformat') else str(document.updated_at),
        version=document.version,
        is_locked=document.is_locked,
        locked_by=document.locked_by,
        file_tree_id=document.file_tree_id,
    )


def calculate_word_count(content: DocumentContent) -> int:
    """Calculate word count from ProseMirror content"""
    def extract_text(node: Dict[str, Any]) -> str:
        """Recursively extract text from ProseMirror node"""
        text = ""
        
        # Add text from this node
        if "text" in node:
            text += node["text"]
        
        # Recursively process content
        if "content" in node and isinstance(node["content"], list):
            for child in node["content"]:
                child_text = extract_text(child)
                if child_text:
                    if text:
                        text += " " + child_text
                    else:
                        text = child_text
        
        return text
    
    # Extract all text from content
    full_text = ""
    for node in content.content:
        extracted = extract_text(node)
        if extracted:
            if full_text:
                full_text += " " + extracted  # Add space between top-level nodes
            else:
                full_text = extracted
    
    # Count words (split by whitespace, filter empty strings)
    words = [word.strip() for word in full_text.split() if word.strip()]
    return len(words)


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    user_id: str = Depends(get_current_user_id)
) -> DocumentResponse:
    """
    Get document by ID
    
    Matches frontend expectation: GET /documents/{documentId}
    """
    try:
        repos = get_repositories()
        document = await repos.document.get_by_id(document_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        logger.info(f"Retrieved document: {document.title} (ID: {document_id})")
        return document_to_response(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("", response_model=DocumentResponse)
async def create_document(
    request: CreateDocumentRequest,
    user_id: str = Depends(get_current_user_id)
) -> DocumentResponse:
    """
    Create a new document
    
    Matches frontend expectation: POST /documents
    """
    try:
        repos = get_repositories()
        
        # Verify project exists
        project = await repos.project.get_by_id(request.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {request.project_id} not found"
            )
        
        # Calculate word count
        word_count = calculate_word_count(request.content)
        
        # Prepare document data
        document_data = {
            "project_id": request.project_id,
            "title": request.title,
            "path": request.path,
            "content": request.content.model_dump(),
            # Note: tags will be assigned after document creation via relationship
            "word_count": word_count,
            "version": "1.0.0",
            "is_locked": False,
            "file_tree_id": request.file_tree_parent_id,
        }
        
        # Create document
        document = await repos.document.create(document_data)
        
        # Update project document count
        await repos.project.update(request.project_id, {
            "document_count": project.document_count + 1,
            "word_count": project.word_count + word_count,
        })
        
        logger.info(f"Created document: {document.title} (ID: {document.id}) for project {request.project_id}")
        return document_to_response(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str, 
    request: UpdateDocumentRequest,
    user_id: str = Depends(get_current_user_id)
) -> DocumentResponse:
    """
    Update an existing document
    
    Matches frontend expectation: PUT /documents/{documentId}
    """
    try:
        repos = get_repositories()
        
        # Check if document exists
        existing_document = await repos.document.get_by_id(document_id)
        if not existing_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        # Prepare updates
        updates = {}
        old_word_count = existing_document.word_count
        new_word_count = old_word_count
        
        if request.title is not None:
            updates["title"] = request.title
        if request.content is not None:
            updates["content"] = request.content.model_dump()
            new_word_count = calculate_word_count(request.content)
            updates["word_count"] = new_word_count
        if request.tags is not None:
            # Note: tags will be updated via relationship, not direct field assignment
            pass
        if request.version is not None:
            updates["version"] = request.version
            
        # Update document
        updated_document = await repos.document.update(document_id, updates)
        
        if updated_document is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update document: Updated document not returned"
            )
            
        # Update project word count if content changed
        if new_word_count != old_word_count:
            project = await repos.project.get_by_id(existing_document.project_id)
            if project:
                await repos.project.update(existing_document.project_id, {
                    "word_count": project.word_count - old_word_count + new_word_count,
                })
                
        logger.info(f"Updated document: {document_id} for project {existing_document.project_id}")
        return document_to_response(updated_document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{document_id}", response_model=DeleteResponse)
async def delete_document(
    document_id: str,
    user_id: str = Depends(get_current_user_id)
) -> DeleteResponse:
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )

        # Delete document
        success = await repos.document.delete(document_id)
        
        if success:
            # Update project document count and word count
            project = await repos.project.get_by_id(existing_document.project_id)
            if project:
                await repos.project.update(existing_document.project_id, {
                    "document_count": project.document_count - 1,
                    "word_count": project.word_count - existing_document.word_count,
                })
                
            logger.info(f"Deleted document: {document_id} from project {existing_document.project_id}")
            return DeleteResponse(success=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )