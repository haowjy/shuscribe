"""
File-Based Wiki Repository Implementation

Handles complex chapter-based versioning for spoiler prevention.
Structure:
- wiki/ - Current article versions (user-visible)
- wiki-versions/ - Chapter-specific versions organized by article and chapter
- .shuscribe/connections.json - Article connections
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID, uuid4
import re

from src.database.interfaces.wiki import IWikiRepository
from src.database.models.wiki import (
    WikiArticle, WikiArticleCreate, WikiArticleUpdate, WikiArticleType,
    ChapterVersion, CurrentVersion, ArticleConnection
)
from src.database.file.utils import FileManager, ensure_workspace_structure


class FileWikiRepository(IWikiRepository):
    """File-based wiki repository with chapter versioning"""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.file_manager = FileManager(workspace_path)
        
        # Ensure workspace structure exists
        ensure_workspace_structure(workspace_path)
        
        # File paths
        structure = self.file_manager.get_workspace_structure()
        self.wiki_dir = structure['wiki']
        self.versions_dir = structure['wiki_versions']
        self.connections_file = structure['system'] / "connections.json"
        self.articles_index_file = structure['system'] / "articles_index.json"
    
    def _get_article_category_dir(self, article_type: WikiArticleType) -> str:
        """Get directory name for article type"""
        type_map = {
            WikiArticleType.CHARACTER: "characters",
            WikiArticleType.LOCATION: "locations",
            WikiArticleType.CONCEPT: "concepts",
            WikiArticleType.EVENT: "events",
            WikiArticleType.ORGANIZATION: "organizations",
            WikiArticleType.OBJECT: "objects"
        }
        return type_map.get(article_type, "other")
    
    def _get_article_filename(self, title: str) -> str:
        """Convert article title to safe filename"""
        # Replace spaces with hyphens, remove special characters
        safe_name = re.sub(r'[^\w\s-]', '', title.lower())
        safe_name = re.sub(r'[-\s]+', '-', safe_name)
        return f"{safe_name}.md"
    
    def _get_article_file_path(self, article_type: WikiArticleType, title: str) -> Path:
        """Get file path for current article"""
        category = self._get_article_category_dir(article_type)
        filename = self._get_article_filename(title)
        return self.wiki_dir / category / filename
    
    def _get_version_file_path(self, article_type: WikiArticleType, title: str, chapter: int) -> Path:
        """Get file path for chapter version"""
        category = self._get_article_category_dir(article_type)
        article_name = self._get_article_filename(title).replace('.md', '')
        filename = f"ch{chapter:03d}.md"
        return self.versions_dir / category / article_name / filename
    
    def _load_articles_index(self) -> Dict[str, dict]:
        """Load articles index"""
        return self.file_manager.read_json_file(self.articles_index_file, {})
    
    def _save_articles_index(self, index: Dict[str, dict]) -> None:
        """Save articles index"""
        self.file_manager.write_json_file(self.articles_index_file, index)
    
    def _article_to_markdown(self, article: WikiArticle) -> str:
        """Convert article to markdown with frontmatter"""
        frontmatter = f"""---
id: {article.id}
title: {article.title}
article_type: {article.article_type.value}
tags: {article.tags}
safe_through_chapter: {article.safe_through_chapter or ""}
created_at: {article.created_at.isoformat()}
updated_at: {article.updated_at.isoformat() if article.updated_at else ""}
---

{article.content}
"""
        return frontmatter
    
    def _markdown_to_article(self, content: str, workspace_id: UUID) -> WikiArticle:
        """Parse markdown content to WikiArticle object"""
        lines = content.strip().split('\n')
        
        # Parse frontmatter
        if lines[0] == '---':
            frontmatter_end = lines.index('---', 1)
            frontmatter_lines = lines[1:frontmatter_end]
            content_lines = lines[frontmatter_end + 1:]
        else:
            raise ValueError("Article file missing frontmatter")
        
        # Parse frontmatter fields
        frontmatter = {}
        for line in frontmatter_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        
        # Parse tags (they're stored as string representation of list)
        tags = []
        if frontmatter.get('tags'):
            tags_str = frontmatter['tags']
            # Simple parsing - could be enhanced
            if tags_str.startswith('[') and tags_str.endswith(']'):
                tags_content = tags_str[1:-1]
                if tags_content:
                    tags = [tag.strip().strip("'\"") for tag in tags_content.split(',')]
        
        article_content = '\n'.join(content_lines).strip()
        
        return WikiArticle(
            id=UUID(frontmatter['id']),
            workspace_id=workspace_id,
            title=frontmatter['title'],
            article_type=WikiArticleType(frontmatter['article_type']),
            content=article_content,
            summary=frontmatter.get('summary'),
            tags=tags,
            safe_through_chapter=int(frontmatter['safe_through_chapter']) if frontmatter.get('safe_through_chapter') else None,
            created_at=datetime.fromisoformat(frontmatter['created_at']),
            updated_at=datetime.fromisoformat(frontmatter['updated_at']) if frontmatter.get('updated_at') else None
        )

    # Article operations
    async def get_article(self, id: UUID) -> Optional[WikiArticle]:
        """Get article by ID"""
        index = self._load_articles_index()
        
        for article_data in index.values():
            if article_data['id'] == str(id):
                article_type = WikiArticleType(article_data['article_type'])
                title = article_data['title']
                file_path = self._get_article_file_path(article_type, title)
                
                if file_path.exists():
                    content = self.file_manager.read_text_file(file_path)
                    return self._markdown_to_article(content, UUID(article_data['workspace_id']))
        
        return None

    async def get_articles_by_workspace(self, workspace_id: UUID) -> List[WikiArticle]:
        """Get all articles for workspace"""
        index = self._load_articles_index()
        articles = []
        
        for article_data in index.values():
            if article_data['workspace_id'] == str(workspace_id):
                article_type = WikiArticleType(article_data['article_type'])
                title = article_data['title']
                file_path = self._get_article_file_path(article_type, title)
                
                if file_path.exists():
                    content = self.file_manager.read_text_file(file_path)
                    articles.append(self._markdown_to_article(content, workspace_id))
        
        return articles

    async def get_articles_by_type(self, workspace_id: UUID, article_type: str) -> List[WikiArticle]:
        """Get articles by type"""
        all_articles = await self.get_articles_by_workspace(workspace_id)
        return [article for article in all_articles if article.article_type.value == article_type]

    async def create_article(self, workspace_id: UUID, article_data: WikiArticleCreate) -> WikiArticle:
        """Create new article"""
        article_id = uuid4()
        
        article = WikiArticle(
            id=article_id,
            workspace_id=workspace_id,
            title=article_data.title,
            article_type=article_data.article_type,
            content=article_data.content,
            summary=article_data.summary,
            tags=article_data.tags,
            safe_through_chapter=article_data.safe_through_chapter,
            created_at=datetime.now(),
            updated_at=None
        )
        
        # Save to file
        file_path = self._get_article_file_path(article.article_type, article.title)
        self.file_manager.ensure_directory(file_path.parent)
        markdown_content = self._article_to_markdown(article)
        self.file_manager.write_text_file(file_path, markdown_content)
        
        # Update index
        index = self._load_articles_index()
        index[str(article_id)] = {
            "id": str(article.id),
            "workspace_id": str(article.workspace_id),
            "title": article.title,
            "article_type": article.article_type.value
        }
        self._save_articles_index(index)
        
        return article

    async def update_article(self, article_id: UUID, article_data: WikiArticleUpdate) -> WikiArticle:
        """Update article"""
        article = await self.get_article(article_id)
        if not article:
            raise ValueError("Article not found")
        
        old_file_path = self._get_article_file_path(article.article_type, article.title)
        
        # Update fields
        update_dict = article_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(article, field):
                setattr(article, field, value)
        
        article.updated_at = datetime.now()
        
        # If title or type changed, need to move file
        new_file_path = self._get_article_file_path(article.article_type, article.title)
        if old_file_path != new_file_path:
            # Delete old file
            self.file_manager.delete_file(old_file_path)
            # Ensure new directory exists
            self.file_manager.ensure_directory(new_file_path.parent)
        
        # Save to new/same file
        markdown_content = self._article_to_markdown(article)
        self.file_manager.write_text_file(new_file_path, markdown_content)
        
        # Update index
        index = self._load_articles_index()
        index[str(article_id)].update({
            "title": article.title,
            "article_type": article.article_type.value
        })
        self._save_articles_index(index)
        
        return article

    async def delete_article(self, article_id: UUID) -> bool:
        """Delete article"""
        article = await self.get_article(article_id)
        if not article:
            return False
        
        # Delete main file
        file_path = self._get_article_file_path(article.article_type, article.title)
        self.file_manager.delete_file(file_path)
        
        # Delete all version files
        category = self._get_article_category_dir(article.article_type)
        article_name = self._get_article_filename(article.title).replace('.md', '')
        version_dir = self.versions_dir / category / article_name
        
        if version_dir.exists():
            # Delete all chapter version files
            for version_file in version_dir.glob("*.md"):
                self.file_manager.delete_file(version_file)
            # Remove directory if empty
            try:
                version_dir.rmdir()
            except OSError:
                pass  # Directory not empty or other issue
        
        # Remove from index
        index = self._load_articles_index()
        if str(article_id) in index:
            del index[str(article_id)]
            self._save_articles_index(index)
        
        return True

    # Chapter versioning
    async def create_chapter_version(
        self, 
        article_id: UUID, 
        content: str, 
        safe_through_chapter: int,
        **metadata
    ) -> ChapterVersion:
        """Create chapter version"""
        article = await self.get_article(article_id)
        if not article:
            raise ValueError("Article not found")
        
        version_id = uuid4()
        version = ChapterVersion(
            id=version_id,
            article_id=article_id,
            safe_through_chapter=safe_through_chapter,
            content=content,
            summary=metadata.get('summary'),
            ai_guidance=metadata.get('ai_guidance'),
            created_at=datetime.now(),
            updated_at=None
        )
        
        # Save version file
        file_path = self._get_version_file_path(article.article_type, article.title, safe_through_chapter)
        self.file_manager.ensure_directory(file_path.parent)
        
        # Create version markdown with metadata
        version_content = f"""---
id: {version.id}
article_id: {version.article_id}
safe_through_chapter: {version.safe_through_chapter}
summary: {version.summary or ""}
ai_guidance: {version.ai_guidance or ""}
created_at: {version.created_at.isoformat()}
---

{version.content}
"""
        self.file_manager.write_text_file(file_path, version_content)
        
        return version

    async def get_version_for_chapter(
        self, 
        article_id: UUID, 
        chapter_number: int
    ) -> Optional[ChapterVersion]:
        """Get appropriate version for chapter (spoiler prevention)"""
        article = await self.get_article(article_id)
        if not article:
            return None
        
        # Find the latest version that's safe for this chapter
        category = self._get_article_category_dir(article.article_type)
        article_name = self._get_article_filename(article.title).replace('.md', '')
        version_dir = self.versions_dir / category / article_name
        
        if not version_dir.exists():
            return None
        
        # Find all versions safe through this chapter or earlier
        best_version = None
        best_chapter = 0
        
        for version_file in version_dir.glob("ch*.md"):
            # Extract chapter number from filename
            match = re.match(r'ch(\d+)\.md', version_file.name)
            if match:
                version_chapter = int(match.group(1))
                if version_chapter <= chapter_number and version_chapter > best_chapter:
                    best_chapter = version_chapter
                    best_version = version_file
        
        if best_version:
            content = self.file_manager.read_text_file(best_version)
            # Parse version content
            lines = content.strip().split('\n')
            if lines[0] == '---':
                frontmatter_end = lines.index('---', 1)
                frontmatter_lines = lines[1:frontmatter_end]
                content_lines = lines[frontmatter_end + 1:]
                
                frontmatter = {}
                for line in frontmatter_lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip()
                
                return ChapterVersion(
                    id=UUID(frontmatter['id']),
                    article_id=UUID(frontmatter['article_id']),
                    safe_through_chapter=int(frontmatter['safe_through_chapter']),
                    content='\n'.join(content_lines).strip(),
                    summary=frontmatter.get('summary') or None,
                    ai_guidance=frontmatter.get('ai_guidance') or None,
                    created_at=datetime.fromisoformat(frontmatter['created_at']),
                    updated_at=None
                )
        
        return None

    async def get_all_versions(self, article_id: UUID) -> List[ChapterVersion]:
        """Get all versions for article"""
        article = await self.get_article(article_id)
        if not article:
            return []
        
        category = self._get_article_category_dir(article.article_type)
        article_name = self._get_article_filename(article.title).replace('.md', '')
        version_dir = self.versions_dir / category / article_name
        
        if not version_dir.exists():
            return []
        
        versions = []
        for version_file in version_dir.glob("ch*.md"):
            content = self.file_manager.read_text_file(version_file)
            # Parse version (similar to get_version_for_chapter)
            lines = content.strip().split('\n')
            if lines[0] == '---':
                frontmatter_end = lines.index('---', 1)
                frontmatter_lines = lines[1:frontmatter_end]
                content_lines = lines[frontmatter_end + 1:]
                
                frontmatter = {}
                for line in frontmatter_lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip()
                
                versions.append(ChapterVersion(
                    id=UUID(frontmatter['id']),
                    article_id=UUID(frontmatter['article_id']),
                    safe_through_chapter=int(frontmatter['safe_through_chapter']),
                    content='\n'.join(content_lines).strip(),
                    summary=frontmatter.get('summary') or None,
                    ai_guidance=frontmatter.get('ai_guidance') or None,
                    created_at=datetime.fromisoformat(frontmatter['created_at']),
                    updated_at=None
                ))
        
        return sorted(versions, key=lambda v: v.safe_through_chapter)

    # Current version management (simplified for file storage)
    async def create_current_version(
        self, 
        article_id: UUID, 
        content: str,
        user_notes: str = ""
    ) -> CurrentVersion:
        """Create or update current version (updates main article)"""
        article = await self.get_article(article_id)
        if not article:
            raise ValueError("Article not found")
        
        # Update main article content
        article.content = content
        article.updated_at = datetime.now()
        
        # Save updated article
        file_path = self._get_article_file_path(article.article_type, article.title)
        markdown_content = self._article_to_markdown(article)
        self.file_manager.write_text_file(file_path, markdown_content)
        
        # Return current version representation
        return CurrentVersion(
            id=uuid4(),  # Not persisted separately in file storage
            article_id=article_id,
            content=content,
            user_notes=user_notes,
            ai_guidance="",
            is_generated=False,
            created_at=datetime.now(),
            updated_at=None
        )

    async def get_current_version(self, article_id: UUID) -> Optional[CurrentVersion]:
        """Get current version (from main article)"""
        article = await self.get_article(article_id)
        if not article:
            return None
        
        return CurrentVersion(
            id=uuid4(),  # Not persisted separately
            article_id=article_id,
            content=article.content,
            user_notes="",  # Not stored separately in file storage
            ai_guidance="",
            is_generated=False,
            created_at=article.created_at,
            updated_at=article.updated_at
        )

    async def update_current_version(
        self, 
        article_id: UUID, 
        content: Optional[str] = None,
        user_notes: Optional[str] = None,
        **updates
    ) -> CurrentVersion:
        """Update current version"""
        return await self.create_current_version(
            article_id, 
            content or "", 
            user_notes or ""
        )

    # Article connections
    async def create_connection(
        self,
        from_article_id: UUID,
        to_article_id: UUID,
        connection_type: str = "related",
        strength: float = 1.0,
        context: Optional[str] = None
    ) -> ArticleConnection:
        """Create connection between articles"""
        if from_article_id == to_article_id:
            raise ValueError("Cannot connect article to itself")
        
        connection_id = uuid4()
        connection = ArticleConnection(
            id=connection_id,
            from_article_id=from_article_id,
            to_article_id=to_article_id,
            connection_type=connection_type,
            description=context,
            strength=strength,
            created_at=datetime.now(),
            updated_at=None
        )
        
        # Load connections
        connections_data = self.file_manager.read_json_file(self.connections_file, {})
        
        # Add new connection
        connections_data[str(connection_id)] = {
            "id": str(connection.id),
            "from_article_id": str(connection.from_article_id),
            "to_article_id": str(connection.to_article_id),
            "connection_type": connection.connection_type,
            "description": connection.description,
            "strength": connection.strength,
            "created_at": connection.created_at.isoformat(),
            "updated_at": None
        }
        
        self.file_manager.write_json_file(self.connections_file, connections_data)
        return connection

    async def get_connections_from(self, article_id: UUID) -> List[ArticleConnection]:
        """Get all connections from an article"""
        connections_data = self.file_manager.read_json_file(self.connections_file, {})
        connections = []
        
        for conn_data in connections_data.values():
            if conn_data['from_article_id'] == str(article_id):
                connections.append(ArticleConnection(
                    id=UUID(conn_data['id']),
                    from_article_id=UUID(conn_data['from_article_id']),
                    to_article_id=UUID(conn_data['to_article_id']),
                    connection_type=conn_data['connection_type'],
                    description=conn_data.get('description'),
                    strength=conn_data['strength'],
                    created_at=datetime.fromisoformat(conn_data['created_at']),
                    updated_at=datetime.fromisoformat(conn_data['updated_at']) if conn_data.get('updated_at') else None
                ))
        
        return connections

    async def get_connections_to(self, article_id: UUID) -> List[ArticleConnection]:
        """Get all connections to an article"""
        connections_data = self.file_manager.read_json_file(self.connections_file, {})
        connections = []
        
        for conn_data in connections_data.values():
            if conn_data['to_article_id'] == str(article_id):
                connections.append(ArticleConnection(
                    id=UUID(conn_data['id']),
                    from_article_id=UUID(conn_data['from_article_id']),
                    to_article_id=UUID(conn_data['to_article_id']),
                    connection_type=conn_data['connection_type'],
                    description=conn_data.get('description'),
                    strength=conn_data['strength'],
                    created_at=datetime.fromisoformat(conn_data['created_at']),
                    updated_at=datetime.fromisoformat(conn_data['updated_at']) if conn_data.get('updated_at') else None
                ))
        
        return connections

    async def delete_connection(self, from_article_id: UUID, to_article_id: UUID) -> bool:
        """Delete connection between articles"""
        connections_data = self.file_manager.read_json_file(self.connections_file, {})
        
        # Find and remove connection
        for conn_id, conn_data in list(connections_data.items()):
            if (conn_data['from_article_id'] == str(from_article_id) and 
                conn_data['to_article_id'] == str(to_article_id)):
                del connections_data[conn_id]
                self.file_manager.write_json_file(self.connections_file, connections_data)
                return True
        
        return False 