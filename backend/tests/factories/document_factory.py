"""
DocumentFactory for creating Document domain models in tests.
"""
import uuid
from datetime import datetime, UTC
from typing import Optional, Dict, Any, List

from src.database.interfaces.models import Document


class DocumentFactory:
    """Factory for creating Document domain models with realistic test data."""
    
    @staticmethod
    def create(
        id: Optional[str] = None,
        project_id: Optional[str] = None,
        title: Optional[str] = None,
        path: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        word_count: int = 0,
        version: str = "1.0.0",
        is_locked: bool = False,
        locked_by: Optional[str] = None,
        file_tree_id: Optional[str] = None,
        created_by: Optional[str] = None,
        updated_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs
    ) -> Document:
        """
        Create a Document domain model with sensible defaults.
        
        Args:
            id: Document ID (auto-generated UUID if not provided)
            project_id: Project ID (auto-generated UUID if not provided)
            title: Document title (auto-generated if not provided)
            path: Document path (auto-generated based on title if not provided)
            content: ProseMirror JSON content (default empty document)
            word_count: Word count (auto-calculated from content if 0)
            version: Document version (default "1.0.0")
            is_locked: Lock status (default False)
            locked_by: User who locked the document (default None)
            file_tree_id: Associated file tree item ID (default None)
            created_by: User ID who created the document (auto-generated UUID if not provided)
            updated_by: User ID who last updated the document (uses created_by if not provided)
            tags: List of tag names/IDs (default empty)
            created_at: Creation timestamp (current time if not provided)
            updated_at: Update timestamp (current time if not provided)
            **kwargs: Additional keyword arguments
            
        Returns:
            Properly constructed Document domain model
        """
        # Generate defaults
        doc_id = id or str(uuid.uuid4())
        doc_project_id = project_id or str(uuid.uuid4())
        doc_title = title or f"Test Document {doc_id[:8]}"
        doc_path = path or f"/{doc_title.lower().replace(' ', '_')}.md"
        doc_created_by = created_by or str(uuid.uuid4())
        now = datetime.now(UTC).replace(tzinfo=None)
        
        # Default ProseMirror content
        if content is None:
            content = {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": f"This is the content of {doc_title}."
                            }
                        ]
                    }
                ]
            }
        
        # Use provided word count (no auto-calculation for now)
        
        # Default tags
        if tags is None:
            tags = []
        
        return Document(
            id=doc_id,
            project_id=doc_project_id,
            title=doc_title,
            path=doc_path,
            content=content,
            word_count=word_count,
            version=version,
            is_locked=is_locked,
            locked_by=locked_by,
            file_tree_id=file_tree_id,
            created_by=doc_created_by,
            updated_by=updated_by or doc_created_by,
            tags=tags,
            created_at=created_at or now,
            updated_at=updated_at or now,
        )
    
    
    @staticmethod
    def create_character_profile(
        name: str = "Aria Moonwhisper",
        project_id: Optional[str] = None
    ) -> Document:
        """Create a character profile document with rich content."""
        character_content = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [
                        {"type": "text", "text": name}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2}, 
                    "content": [
                        {"type": "text", "text": "Physical Description"}
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{name} is a 24-year-old mage with exceptional abilities in elemental magic. Standing at average height with flowing auburn hair and piercing green eyes, she carries herself with quiet confidence born from years of magical training."
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [
                        {"type": "text", "text": "Background"}
                    ]
                },
                {
                    "type": "paragraph", 
                    "content": [
                        {
                            "type": "text",
                            "text": f"Born in the mountain village of Thornwick, {name} discovered her powers at age 12 when she accidentally froze the village well during a particularly emotional moment. This incident led to her being taken to the Academy of Elemental Arts for proper training."
                        }
                    ]
                }
            ]
        }
        
        return DocumentFactory.create(
            project_id=project_id,
            title=f"{name} - Character Profile",
            path=f"/characters/{name.lower().replace(' ', '_')}.md",
            content=character_content,
            tags=["character", "protagonist", "mage"]
        )
    
    @staticmethod
    def create_chapter(
        chapter_num: int = 1,
        project_id: Optional[str] = None,
        word_count: int = 250
    ) -> Document:
        """Create a chapter document with specified word count."""
        # Create content with approximately the requested word count
        base_text = f"This is the content of chapter {chapter_num}. "
        repeat_count = max(1, word_count // len(base_text.split()))
        chapter_text = (base_text * repeat_count).strip()
        
        chapter_content = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [
                        {"type": "text", "text": f"Chapter {chapter_num}"}
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": chapter_text}
                    ]
                }
            ]
        }
        
        return DocumentFactory.create(
            project_id=project_id,
            title=f"Chapter {chapter_num}: The Beginning",
            path=f"/chapters/chapter_{chapter_num:02d}.md",
            content=chapter_content,
            word_count=word_count,
            tags=["chapter", "story"]
        )
    
    @staticmethod
    def create_empty(project_id: Optional[str] = None) -> Document:
        """Create an empty document with minimal content."""
        return DocumentFactory.create(
            project_id=project_id,
            title="Empty Document",
            path="/empty.md",
            content={
                "type": "doc",
                "content": []
            },
            word_count=0,
            tags=[]
        )
    
    @staticmethod
    def create_with_complex_content(project_id: Optional[str] = None) -> Document:
        """Create a document with complex ProseMirror content including formatting."""
        complex_content = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [
                        {"type": "text", "text": "Complex Document"}
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "This paragraph contains "},
                        {"type": "text", "text": "bold text", "marks": [{"type": "strong"}]},
                        {"type": "text", "text": " and "},
                        {"type": "text", "text": "italic text", "marks": [{"type": "em"}]},
                        {"type": "text", "text": " for testing."}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "First bullet point"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem", 
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Second bullet point"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        return DocumentFactory.create(
            project_id=project_id,
            title="Complex Formatting Document",
            path="/complex_document.md",
            content=complex_content,
            tags=["test", "formatting", "complex"]
        )