"""
File Storage Utilities

Common utilities for file-based storage operations including JSON handling,
directory management, and file locking for concurrent access.
"""

import json
import os
import fcntl
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar, Generic
from contextlib import contextmanager
import threading
from uuid import UUID

T = TypeVar('T')


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for ShuScribe types"""
    
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'model_dump'):
            return obj.model_dump()
        return super().default(obj)


class FileManager:
    """Manages file operations with proper locking and error handling"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self._locks: Dict[str, threading.Lock] = {}
        self._lock_lock = threading.Lock()
    
    def _get_file_lock(self, file_path: Path) -> threading.Lock:
        """Get or create a lock for a specific file"""
        file_key = str(file_path)
        with self._lock_lock:
            if file_key not in self._locks:
                self._locks[file_key] = threading.Lock()
            return self._locks[file_key]
    
    def ensure_directory(self, dir_path: Path) -> None:
        """Ensure directory exists with proper permissions"""
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Set secure permissions for system directories
        if dir_path.name == '.shuscribe':
            os.chmod(dir_path, 0o700)  # Owner read/write/execute only
    
    @contextmanager
    def locked_file_write(self, file_path: Path):
        """Context manager for thread-safe file writing"""
        lock = self._get_file_lock(file_path)
        with lock:
            yield
    
    def read_json_file(self, file_path: Path, default: Any = None) -> Any:
        """Read JSON file with error handling"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default
        except (json.JSONDecodeError, IOError) as e:
            if default is not None:
                return default
            raise ValueError(f"Failed to read JSON file {file_path}: {e}")
    
    def write_json_file(self, file_path: Path, data: Any, secure: bool = False) -> None:
        """Write JSON file atomically with proper permissions"""
        self.ensure_directory(file_path.parent)
        
        with self.locked_file_write(file_path):
            # Write to temporary file first (atomic operation)
            temp_file = file_path.with_suffix(f"{file_path.suffix}.tmp")
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, cls=JSONEncoder, indent=2, ensure_ascii=False)
                
                # Atomic move
                temp_file.replace(file_path)
                
                # Set secure permissions for sensitive files
                if secure:
                    os.chmod(file_path, 0o600)  # Owner read/write only
                    
            except Exception as e:
                # Clean up temp file on error
                if temp_file.exists():
                    temp_file.unlink()
                raise ValueError(f"Failed to write JSON file {file_path}: {e}")
    
    def read_text_file(self, file_path: Path, default: str = "") -> str:
        """Read text file with error handling"""
        try:
            if file_path.exists():
                return file_path.read_text(encoding='utf-8')
            return default
        except IOError as e:
            if default:
                return default
            raise ValueError(f"Failed to read text file {file_path}: {e}")
    
    def write_text_file(self, file_path: Path, content: str) -> None:
        """Write text file with proper directory creation"""
        self.ensure_directory(file_path.parent)
        
        with self.locked_file_write(file_path):
            file_path.write_text(content, encoding='utf-8')
    
    def delete_file(self, file_path: Path) -> bool:
        """Delete file safely"""
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except OSError:
            return False
    
    def list_files(self, dir_path: Path, pattern: str = "*") -> List[Path]:
        """List files in directory with pattern matching"""
        if not dir_path.exists():
            return []
        return list(dir_path.glob(pattern))
    
    def get_workspace_structure(self) -> Dict[str, Path]:
        """Get standard workspace directory structure"""
        return {
            'root': self.workspace_path,
            'system': self.workspace_path / '.shuscribe',
            'story': self.workspace_path / 'story',
            'chapters': self.workspace_path / 'story' / 'chapters',
            'drafts': self.workspace_path / 'story' / 'drafts',
            'wiki': self.workspace_path / 'wiki',
            'wiki_versions': self.workspace_path / 'wiki-versions',
            'notes': self.workspace_path / 'notes',
            'conversations': self.workspace_path / 'conversations',
        }


class FileIndex(Generic[T]):
    """Generic file-based index for fast lookups"""
    
    def __init__(self, file_manager: FileManager, index_file: Path):
        self.file_manager = file_manager
        self.index_file = index_file
        self._index: Dict[str, Any] = {}
        self._load_index()
    
    def _load_index(self) -> None:
        """Load index from file"""
        self._index = self.file_manager.read_json_file(self.index_file, {})
    
    def _save_index(self) -> None:
        """Save index to file"""
        self.file_manager.write_json_file(self.index_file, self._index)
    
    def add(self, key: str, value: Any) -> None:
        """Add entry to index"""
        self._index[key] = value
        self._save_index()
    
    def get(self, key: str) -> Optional[Any]:
        """Get entry from index"""
        return self._index.get(key)
    
    def remove(self, key: str) -> bool:
        """Remove entry from index"""
        if key in self._index:
            del self._index[key]
            self._save_index()
            return True
        return False
    
    def list_keys(self) -> List[str]:
        """List all keys in index"""
        return list(self._index.keys())
    
    def clear(self) -> None:
        """Clear entire index"""
        self._index.clear()
        self._save_index()


def ensure_workspace_structure(workspace_path: Path) -> None:
    """Ensure complete workspace directory structure exists"""
    file_manager = FileManager(workspace_path)
    structure = file_manager.get_workspace_structure()
    
    for dir_path in structure.values():
        file_manager.ensure_directory(dir_path)
    
    # Create category subdirectories for wiki
    wiki_categories = ['characters', 'locations', 'concepts', 'events', 'organizations', 'objects']
    for category in wiki_categories:
        file_manager.ensure_directory(structure['wiki'] / category)
        file_manager.ensure_directory(structure['wiki_versions'] / category) 