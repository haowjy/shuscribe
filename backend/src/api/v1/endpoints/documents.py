# backend/src/api/v1/endpoints/documents.py
"""
Document API endpoints matching frontend expectations
"""
import logging
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, field_validator

from src.database.factory import get_repositories
from src.database.interfaces.models import Document, Tag
from src.schemas.responses.tags import TagInfo
from src.schemas.responses.documents import DocumentResponse
from src.api.dependencies import get_current_user_id
from src.utils.path_utils import validate_document_path, ensure_folder_hierarchy_exists
from src.utils.prosemirror import compute_word_count_from_prosemirror

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================


def tag_to_info(tag: Tag | str) -> TagInfo:
    """Convert Tag model or tag string to TagInfo response"""
    if isinstance(tag, str):
        # For domain models where tags are stored as strings
        return TagInfo(id=tag, name=tag, icon=None, color=None)  # Use the tag string as ID for now
    else:
        # Full Tag object
        return TagInfo(id=tag.id, name=tag.name, icon=tag.icon, color=tag.color)


# ============================================================================
# Request/Response Models (matching frontend API types)
# ============================================================================


class DocumentContent(BaseModel):
    """ProseMirror document content structure

    Rich JSON format supporting text, images, formatting, and @-references
    """

    type: str = "doc"
    content: List[Dict[str, Any]] = []

    @field_validator("content", mode="before")
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

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        """Ensure type is always 'doc' for ProseMirror documents"""
        if v != "doc":
            return "doc"
        return v


class CreateDocumentRequest(BaseModel):
    """Request to create a new document

    Fields:
    - title: Display name - e.g., "Chapter 1: The Beginning" or "story.md"
    - path: Organizational structure - e.g., "/chapters/chapter-1"
    - content: ProseMirror JSON with rich content (text, images, formatting, @-references)
    - tags: List of tag strings for categorization
    """

    model_config = {"populate_by_name": True}

    project_id: str
    title: str
    path: str
    content: DocumentContent = DocumentContent()
    tags: List[str] = []

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty"""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")

        return v.strip()

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate path format for organizational structure"""
        if not v or not v.strip():
            raise ValueError("Path cannot be empty")

        path_clean = v.strip()

        # Ensure path starts with /
        if not path_clean.startswith("/"):
            path_clean = "/" + path_clean

        # Remove any double slashes
        while "//" in path_clean:
            path_clean = path_clean.replace("//", "/")

        return path_clean


class UpdateDocumentRequest(BaseModel):
    """Request to update an existing document

    Fields:
    - title: Display name - e.g., "Chapter 1: The Beginning" or "story.md"
    - content: ProseMirror JSON with rich content (text, images, formatting, @-references)
    - tags: List of tag strings for categorization
    """

    title: str | None = None
    content: DocumentContent | None = None
    tags: List[str] | None = None
    version: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """Validate title is not empty"""
        if v is None:
            return v

        if not v.strip():
            raise ValueError("Title cannot be empty")

        return v.strip()


class DeleteResponse(BaseModel):
    """Response for delete operations"""

    success: bool


# ============================================================================
# Helper Functions
# ============================================================================


def prosemirror_to_markdown(content: DocumentContent) -> str:
    """Convert ProseMirror content to Markdown format for LLM processing"""

    def node_to_markdown(node: Dict[str, Any], depth: int = 0) -> str:
        """Convert a ProseMirror node to Markdown"""
        if not isinstance(node, dict):
            return ""

        node_type = node.get("type", "")

        # Handle text nodes
        if node_type == "text":
            text = node.get("text", "")
            marks = node.get("marks", [])

            # Apply text formatting based on marks
            for mark in marks:
                mark_type = mark.get("type", "")
                if mark_type == "strong":
                    text = f"**{text}**"
                elif mark_type == "em":
                    text = f"*{text}*"
                elif mark_type == "code":
                    text = f"`{text}`"

            return text

        # Handle block nodes
        elif node_type == "paragraph":
            content_text = ""
            if "content" in node and isinstance(node["content"], list):
                content_text = "".join(node_to_markdown(child, depth) for child in node["content"])
            return f"{content_text}\n\n"

        elif node_type == "heading":
            level = node.get("attrs", {}).get("level", 1)
            content_text = ""
            if "content" in node and isinstance(node["content"], list):
                content_text = "".join(node_to_markdown(child, depth) for child in node["content"])
            return f"{'#' * level} {content_text}\n\n"

        elif node_type == "blockquote":
            content_text = ""
            if "content" in node and isinstance(node["content"], list):
                content_text = "".join(node_to_markdown(child, depth) for child in node["content"])
            # Add > prefix to each line
            quoted = "\n".join(f"> {line}" for line in content_text.strip().split("\n"))
            return f"{quoted}\n\n"

        elif node_type == "codeBlock":
            content_text = ""
            if "content" in node and isinstance(node["content"], list):
                content_text = "".join(node_to_markdown(child, depth) for child in node["content"])
            lang = node.get("attrs", {}).get("language", "")
            return f"```{lang}\n{content_text}```\n\n"

        elif node_type == "bulletList":
            content_text = ""
            if "content" in node and isinstance(node["content"], list):
                for item in node["content"]:
                    item_text = node_to_markdown(item, depth + 1)
                    content_text += f"{'  ' * depth}- {item_text.strip()}\n"
            return f"{content_text}\n"

        elif node_type == "orderedList":
            content_text = ""
            if "content" in node and isinstance(node["content"], list):
                for i, item in enumerate(node["content"], 1):
                    item_text = node_to_markdown(item, depth + 1)
                    content_text += f"{'  ' * depth}{i}. {item_text.strip()}\n"
            return f"{content_text}\n"

        elif node_type == "listItem":
            content_text = ""
            if "content" in node and isinstance(node["content"], list):
                content_text = "".join(node_to_markdown(child, depth) for child in node["content"])
            return content_text.strip()

        # Handle other nodes generically by processing their content
        else:
            if "content" in node and isinstance(node["content"], list):
                return "".join(node_to_markdown(child, depth) for child in node["content"])
            elif "text" in node:
                return node["text"]

        return ""

    # Convert the entire document
    markdown_text = ""
    for node in content.content:
        markdown_text += node_to_markdown(node)

    # Clean up extra newlines
    while "\n\n\n" in markdown_text:
        markdown_text = markdown_text.replace("\n\n\n", "\n\n")

    return markdown_text.strip()


def prosemirror_to_html(content: DocumentContent) -> str:
    """Convert ProseMirror content to HTML format for display/export"""

    def node_to_html(node: Dict[str, Any]) -> str:
        """Convert a ProseMirror node to HTML"""
        if not isinstance(node, dict):
            return ""

        node_type = node.get("type", "")

        # Handle text nodes
        if node_type == "text":
            text = node.get("text", "")
            marks = node.get("marks", [])

            # Apply HTML formatting based on marks
            for mark in marks:
                mark_type = mark.get("type", "")
                if mark_type == "strong":
                    text = f"<strong>{text}</strong>"
                elif mark_type == "em":
                    text = f"<em>{text}</em>"
                elif mark_type == "code":
                    text = f"<code>{text}</code>"

            return text

        # Handle block and inline nodes
        elif node_type == "paragraph":
            content_html = ""
            if "content" in node and isinstance(node["content"], list):
                content_html = "".join(node_to_html(child) for child in node["content"])
            return f"<p>{content_html}</p>"

        elif node_type == "heading":
            level = node.get("attrs", {}).get("level", 1)
            content_html = ""
            if "content" in node and isinstance(node["content"], list):
                content_html = "".join(node_to_html(child) for child in node["content"])
            return f"<h{level}>{content_html}</h{level}>"

        elif node_type == "blockquote":
            content_html = ""
            if "content" in node and isinstance(node["content"], list):
                content_html = "".join(node_to_html(child) for child in node["content"])
            return f"<blockquote>{content_html}</blockquote>"

        elif node_type == "codeBlock":
            content_html = ""
            if "content" in node and isinstance(node["content"], list):
                content_html = "".join(node_to_html(child) for child in node["content"])
            lang = node.get("attrs", {}).get("language", "")
            lang_attr = f' class="language-{lang}"' if lang else ""
            return f"<pre><code{lang_attr}>{content_html}</code></pre>"

        elif node_type == "bulletList":
            content_html = ""
            if "content" in node and isinstance(node["content"], list):
                content_html = "".join(node_to_html(child) for child in node["content"])
            return f"<ul>{content_html}</ul>"

        elif node_type == "orderedList":
            content_html = ""
            if "content" in node and isinstance(node["content"], list):
                content_html = "".join(node_to_html(child) for child in node["content"])
            return f"<ol>{content_html}</ol>"

        elif node_type == "listItem":
            content_html = ""
            if "content" in node and isinstance(node["content"], list):
                content_html = "".join(node_to_html(child) for child in node["content"])
            return f"<li>{content_html}</li>"

        # Handle other nodes generically
        else:
            if "content" in node and isinstance(node["content"], list):
                return "".join(node_to_html(child) for child in node["content"])
            elif "text" in node:
                return node["text"]

        return ""

    # Convert the entire document
    html_content = ""
    for node in content.content:
        html_content += node_to_html(node)

    return html_content


def document_to_response(document: Document) -> DocumentResponse:
    """Convert Document model to DocumentResponse"""
    # Ensure content has the right structure
    content = document.content or {"type": "doc", "content": []}
    if not isinstance(content, dict):
        content = {"type": "doc", "content": []}

    # Convert to DocumentContent object expected by schema
    from src.schemas.responses.documents import DocumentContent as ResponseDocumentContent
    content_obj = ResponseDocumentContent(
        type=content.get("type", "doc"), 
        content=content.get("content", [])
    )

    # Handle tags - in domain models they are List[str], convert to TagInfo
    tags = [tag_to_info(tag) for tag in document.tags] if document.tags else []

    return DocumentResponse(
        id=document.id,
        project_id=document.project_id,
        title=document.title,
        path=document.path,
        content=content_obj,
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


# Note: Word count calculation removed - will be implemented later with proper ProseMirror schema


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
    - content: ProseMirror JSON format with rich content (text, images, formatting, @-references)
    
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

        # Compute word count from ProseMirror content
        word_count = compute_word_count_from_prosemirror(request.content.model_dump())

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
            "file_tree_id": parent_folder_id,  # Auto-determined from path
        }

        # Create document
        document = await repos.document.create(document_data)

        # Assign tags to document if provided
        if request.tags:
            # Update document with tags (domain model expects List[str])
            await repos.document.update(document.id, {"tags": request.tags})
            # Refresh document to get updated tags
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
    - content: ProseMirror JSON format with rich content (text, images, formatting, @-references)
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
            updates["content"] = request.content.model_dump()
            # Compute new word count from updated content
            new_word_count = compute_word_count_from_prosemirror(request.content.model_dump())
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
            return DeleteResponse(success=True)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete document")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
