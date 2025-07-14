# backend/src/database/seed.py
"""
Mock data factory for generating realistic test data using Faker
"""
import uuid
from datetime import datetime, UTC
from typing import Dict, Any, List
from faker import Faker

fake = Faker('en_US')


class MockDataFactory:
    """Factory for generating realistic mock data for development and testing"""
    
    @staticmethod
    def generate_project(project_id: str | None = None, genre: str = "fantasy") -> Dict[str, Any]:
        """Generate a realistic project with genre-specific details"""
        if project_id is None:
            project_id = str(uuid.uuid4())
            
        # Genre-specific project configurations
        genre_configs = {
            "fantasy": {
                "titles": [
                    "The Chronicles of Eldoria",
                    "Shadows of the Ancient Realm", 
                    "The Last Mage's Quest",
                    "Dragons of the Northern Kingdoms",
                    "The Wizard's Apprentice"
                ],
                "descriptions": [
                    "An epic fantasy adventure following a young mage discovering her destiny in a world where magic is forbidden.",
                    "A dark fantasy tale of political intrigue and ancient powers awakening in a medieval kingdom.",
                    "The journey of an unlikely hero who must unite the fractured realms against an emerging darkness."
                ],
                "tags": ["fantasy", "magic", "adventure", "medieval", "dragons"]
            },
            "scifi": {
                "titles": [
                    "Stellar Horizons",
                    "The Quantum Paradox",
                    "Colony Ship Aurora",
                    "Neural Interface Protocol",
                    "Mars Rebellion 2157"
                ],
                "descriptions": [
                    "A hard science fiction thriller set in the 22nd century where humanity battles for survival among the stars.",
                    "An exploration of consciousness and reality through advanced neural interfaces and quantum computing.",
                    "The story of the first generation born on a colony ship, questioning their purpose and destination."
                ],
                "tags": ["science fiction", "space", "technology", "future", "thriller"]
            },
            "mystery": {
                "titles": [
                    "The Vanishing at Willowbrook",
                    "Dead Letters Detective Agency", 
                    "The Midnight Murders",
                    "Secrets of the Old Library",
                    "The Cold Case Files"
                ],
                "descriptions": [
                    "A gripping mystery following Detective Sarah Chen as she investigates a series of disappearances in a small town.",
                    "A cozy mystery series featuring an amateur detective who inherits her grandmother's detective agency.",
                    "A psychological thriller exploring the dark secrets hidden beneath a seemingly perfect suburban community."
                ],
                "tags": ["mystery", "detective", "crime", "thriller", "investigation"]
            }
        }
        
        config = genre_configs.get(genre, genre_configs["fantasy"])
        
        word_count = fake.random_int(min=5000, max=85000)
        document_count = fake.random_int(min=8, max=45)
        target_word_count = fake.random_int(min=50000, max=120000)
        
        return {
            "id": project_id,
            "title": fake.random_element(config["titles"]),
            "description": fake.random_element(config["descriptions"]),
            "word_count": word_count,
            "document_count": document_count,
            "tag_names": fake.random_elements(config["tags"], length=fake.random_int(min=2, max=4), unique=True),
            "collaborators": [
                {
                    "user_id": f"user_{fake.uuid4()[:8]}",
                    "role": "owner",
                    "name": fake.name(),
                    "avatar": None
                }
            ],
            "settings": {
                "auto_save_interval": fake.random_element([15000, 30000, 60000]),
                "word_count_target": target_word_count,
                "backup_enabled": fake.boolean(chance_of_getting_true=85)
            },
            "created_at": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=None),
            "updated_at": fake.date_time_between(start_date="-30d", end_date="now", tzinfo=None)
        }
    
    @staticmethod
    def generate_document(project_id: str, document_type: str = "chapter", chapter_num: int | None = None) -> Dict[str, Any]:
        """Generate a realistic document with ProseMirror content"""
        document_id = str(uuid.uuid4())
        
        if document_type == "chapter":
            if chapter_num is None:
                chapter_num = fake.random_int(min=1, max=25)
            
            title = f"Chapter {chapter_num}: {fake.catch_phrase()}"
            path = f"/Chapters/chapter_{chapter_num:02d}.md"
            
            # Generate realistic chapter content
            paragraphs = []
            for _ in range(fake.random_int(min=3, max=8)):
                paragraph_text = fake.paragraph(nb_sentences=fake.random_int(min=4, max=8))
                paragraphs.append({
                    "type": "paragraph",
                    "content": [{"type": "text", "text": paragraph_text}]
                })
            
            content = {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": f"Chapter {chapter_num}"}]
                    }
                ] + paragraphs
            }
            
            word_count = sum(len(p["content"][0]["text"].split()) for p in paragraphs)
            tag_ids = []  # Will be populated with actual tag IDs from project
            
        elif document_type == "character":
            character_name = fake.name()
            title = f"{character_name} - Character Profile"
            path = f"/Characters/{character_name.lower().replace(' ', '_')}.md"
            
            # Character profile content
            age = fake.random_int(min=16, max=65)
            profession = fake.job()
            personality = fake.text(max_nb_chars=200)
            backstory = fake.text(max_nb_chars=300)
            
            content = {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": character_name}]
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Basic Information"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": f"Age: {age}"}]
                    },
                    {
                        "type": "paragraph", 
                        "content": [{"type": "text", "text": f"Profession: {profession}"}]
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Personality"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": personality}]
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Backstory"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": backstory}]
                    }
                ]
            }
            
            word_count = len((personality + backstory).split())
            tag_ids = []  # Will be populated with actual tag IDs from project
            
        elif document_type == "location":
            location_name = f"{fake.city()} {fake.random_element(['Castle', 'Forest', 'Temple', 'Academy', 'Market'])}"
            title = f"{location_name} - Location Guide"
            path = f"/Locations/{location_name.lower().replace(' ', '_')}.md"
            
            description = fake.text(max_nb_chars=400)
            
            content = {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": location_name}]
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Key Features"}]
                    },
                    {
                        "type": "bullet_list",
                        "content": [
                            {
                                "type": "list_item",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": fake.sentence()}]
                                    }
                                ]
                            }
                            for _ in range(fake.random_int(min=2, max=5))
                        ]
                    }
                ]
            }
            
            word_count = len(description.split()) + fake.random_int(min=20, max=60)
            tag_ids = []  # Will be populated with actual tag IDs from project
            
        else:  # notes or general document
            title = fake.catch_phrase()
            path = f"/Notes/{title.lower().replace(' ', '_')}.md"
            
            note_content = fake.text(max_nb_chars=500)
            
            content = {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": title}]
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": note_content}]
                    }
                ]
            }
            
            word_count = len(note_content.split())
            tag_ids = []  # Will be populated with actual tag IDs from project
        
        return {
            "id": document_id,
            "project_id": project_id,
            "title": title,
            "path": path,
            "content": content,
            "tag_ids": tag_ids,
            "word_count": word_count,
            "version": "1.0.0",
            "is_locked": False,
            "locked_by": None,
            "created_at": fake.date_time_between(start_date="-6m", end_date="now", tzinfo=None),
            "updated_at": fake.date_time_between(start_date="-7d", end_date="now", tzinfo=None)
        }
    
    @staticmethod 
    def generate_file_tree_item(project_id: str, name: str, item_type: str, path: str, 
                              parent_id: str | None = None, document_id: str | None = None) -> Dict[str, Any]:
        """Generate a file tree item (file or folder)"""
        item_id = str(uuid.uuid4())
        
        base_item = {
            "id": item_id,
            "project_id": project_id,
            "name": name,
            "type": item_type,
            "path": path,
            "parent_id": parent_id,
            "created_at": fake.date_time_between(start_date="-6m", end_date="now", tzinfo=None),
            "updated_at": fake.date_time_between(start_date="-7d", end_date="now", tzinfo=None)
        }
        
        if item_type == "file":
            # File-specific properties
            base_item.update({
                "document_id": document_id,
                "icon": MockDataFactory._get_file_icon(name),
                "tag_ids": [],  # Will be populated with actual tag IDs from project
                "word_count": fake.random_int(min=50, max=2000) if document_id else None
            })
        else:
            # Folder-specific properties
            base_item.update({
                "document_id": None,
                "icon": "folder",
                "tag_ids": [],  # Will be populated with actual tag IDs from project
                "word_count": None
            })
        
        return base_item
    
    @staticmethod
    def _get_file_icon(filename: str) -> str:
        """Get appropriate icon for file based on name/type"""
        if "character" in filename.lower():
            return "user"
        elif "chapter" in filename.lower():
            return "file-text"
        elif "location" in filename.lower():
            return "map-pin"
        elif "note" in filename.lower():
            return "sticky-note"
        else:
            return "file"
    
    @staticmethod
    def _get_file_tags(filepath: str) -> List[str]:
        """Get appropriate tags based on file path"""
        path_lower = filepath.lower()
        tag_ids = []
        
        # This method is deprecated - tags are now handled differently
        # keeping for backwards compatibility but returning empty list
        return tag_ids
    
    @staticmethod
    def _get_folder_tags(folder_name: str) -> List[str]:
        """Get appropriate tags for folders - deprecated, returns empty list"""
        # This method is deprecated - tags are now handled differently
        return []
    
    @staticmethod
    def generate_global_tags() -> List[Dict[str, Any]]:
        """Generate global system tags available to all users"""
        global_tags = [
            # System status tags (global)
            {"name": "draft", "icon": "edit", "color": "#94a3b8", "is_system": True, "category": "status"},
            {"name": "published", "icon": "check-circle", "color": "#10b981", "is_system": True, "category": "status"},
            {"name": "archived", "icon": "archive", "color": "#6b7280", "is_system": True, "category": "status"},
            {"name": "review", "icon": "eye", "color": "#f59e0b", "is_system": True, "category": "status"},
            
            # Content type tags (global)
            {"name": "character", "icon": "user", "color": "#3b82f6", "category": "content"},
            {"name": "location", "icon": "map-pin", "color": "#8b5cf6", "category": "content"},
            {"name": "chapter", "icon": "file-text", "color": "#f59e0b", "category": "content"},
            {"name": "notes", "icon": "sticky-note", "color": "#84cc16", "category": "content"},
            {"name": "research", "icon": "book-open", "color": "#06b6d4", "category": "content"},
            
            # Genre tags (global)
            {"name": "fantasy", "icon": "sparkles", "color": "#a855f7", "category": "genre"},
            {"name": "sci-fi", "icon": "rocket", "color": "#7c3aed", "category": "genre"},
            {"name": "mystery", "icon": "search", "color": "#d97706", "category": "genre"},
            {"name": "romance", "icon": "heart", "color": "#ec4899", "category": "genre"},
            {"name": "thriller", "icon": "zap", "color": "#ef4444", "category": "genre"},
            
            # Priority tags (global)
            {"name": "high-priority", "icon": "alert-circle", "color": "#ef4444", "category": "priority"},
            {"name": "medium-priority", "icon": "circle", "color": "#f59e0b", "category": "priority"},
            {"name": "low-priority", "icon": "minus-circle", "color": "#9ca3af", "category": "priority"},
            
            # Additional tags for testing UI responsiveness
            {"name": "important", "icon": "star", "color": "#fbbf24", "category": "meta"},
            {"name": "needs-editing", "icon": "edit-2", "color": "#f97316", "category": "workflow"},
            {"name": "complete", "icon": "check", "color": "#22c55e", "category": "workflow"},
            {"name": "in-progress", "icon": "clock", "color": "#3b82f6", "category": "workflow"},
        ]
        
        # Add default values for global tags
        for tag in global_tags:
            tag.update({
                "id": str(uuid.uuid4()),
                "description": f"Global {tag['name']} tag",
                "usage_count": 0,
                "is_global": True,
                "user_id": None,  # Global tags have no owner
                "is_system": tag.get("is_system", False),
                "is_archived": False,
            })
        
        return global_tags
    
    @staticmethod
    def generate_sample_private_tags(user_id: str) -> List[Dict[str, Any]]:
        """Generate sample private tags for a user"""
        private_tags = [
            {"name": "favorite", "icon": "star", "color": "#fbbf24", "category": "personal"},
            {"name": "needs-work", "icon": "edit-3", "color": "#ef4444", "category": "personal"},
            {"name": "inspiration", "icon": "lightbulb", "color": "#10b981", "category": "personal"},
            {"name": "plot-hole", "icon": "alert-triangle", "color": "#f59e0b", "category": "issues"},
        ]
        
        # Add default values for private tags
        for tag in private_tags:
            tag.update({
                "id": str(uuid.uuid4()),
                "description": f"Personal {tag['name']} tag",
                "usage_count": 0,
                "is_global": False,
                "user_id": user_id,
                "is_system": False,
                "is_archived": False,
            })
        
        return private_tags


class ProjectTemplates:
    """Pre-defined project templates with structured content"""
    
    FANTASY_NOVEL = {
        "genre": "fantasy",
        "folders": [
            {"name": "Characters", "path": "/Characters"},
            {"name": "Chapters", "path": "/Chapters"},  
            {"name": "Locations", "path": "/Locations"},
            {"name": "Notes", "path": "/Notes"}
        ],
        "documents": [
            {"type": "character", "folder": "Characters", "count": 2},
            {"type": "chapter", "folder": "Chapters", "count": 3},
            {"type": "location", "folder": "Locations", "count": 2},
            {"type": "notes", "folder": "Notes", "count": 1}
        ]
    }
    
    SCIFI_THRILLER = {
        "genre": "scifi",
        "folders": [
            {"name": "Characters", "path": "/Characters"},
            {"name": "Chapters", "path": "/Chapters"},
            {"name": "Technology", "path": "/Technology"},
            {"name": "Locations", "path": "/Locations"}
        ],
        "documents": [
            {"type": "character", "folder": "Characters", "count": 2},
            {"type": "chapter", "folder": "Chapters", "count": 3},
            {"type": "location", "folder": "Locations", "count": 1},
            {"type": "notes", "folder": "Technology", "count": 1}
        ]
    }
    
    MYSTERY_NOVEL = {
        "genre": "mystery",
        "folders": [
            {"name": "Characters", "path": "/Characters"},
            {"name": "Chapters", "path": "/Chapters"},
            {"name": "Clues", "path": "/Clues"},
            {"name": "Notes", "path": "/Notes"}
        ],
        "documents": [
            {"type": "character", "folder": "Characters", "count": 2},
            {"type": "chapter", "folder": "Chapters", "count": 3},
            {"type": "notes", "folder": "Clues", "count": 2},
            {"type": "notes", "folder": "Notes", "count": 1}
        ]
    }