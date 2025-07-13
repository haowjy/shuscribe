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
            "tags": fake.random_elements(config["tags"], length=fake.random_int(min=2, max=4), unique=True),
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
            tags = ["chapter", "story", "draft"]
            
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
            tags = ["character", "profile", fake.random_element(["protagonist", "antagonist", "supporting"])]
            
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
            tags = ["location", "worldbuilding", fake.random_element(["city", "wilderness", "building", "landmark"])]
            
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
            tags = ["notes", "planning", fake.random_element(["ideas", "research", "worldbuilding"])]
        
        return {
            "id": document_id,
            "project_id": project_id,
            "title": title,
            "path": path,
            "content": content,
            "tags": tags,
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
                "tags": MockDataFactory._get_file_tags(path),
                "word_count": fake.random_int(min=50, max=2000) if document_id else None
            })
        else:
            # Folder-specific properties
            base_item.update({
                "document_id": None,
                "icon": "folder",
                "tags": MockDataFactory._get_folder_tags(name),
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
        tags = []
        
        if "/characters/" in path_lower:
            tags.extend(["character", "profile"])
        elif "/chapters/" in path_lower:
            tags.extend(["chapter", "story"])
        elif "/locations/" in path_lower:
            tags.extend(["location", "worldbuilding"])
        elif "/notes/" in path_lower:
            tags.extend(["notes", "planning"])
        
        return tags
    
    @staticmethod
    def _get_folder_tags(folder_name: str) -> List[str]:
        """Get appropriate tags for folders"""
        name_lower = folder_name.lower()
        
        if "character" in name_lower:
            return ["character"]
        elif "chapter" in name_lower:
            return ["story"]
        elif "location" in name_lower:
            return ["worldbuilding"]
        elif "note" in name_lower:
            return ["planning"]
        else:
            return ["organization"]


class ProjectTemplates:
    """Pre-defined project templates with structured content"""
    
    FANTASY_NOVEL = {
        "genre": "fantasy",
        "folders": [
            {"name": "Characters", "path": "/Characters"},
            {"name": "Chapters", "path": "/Chapters"},  
            {"name": "Locations", "path": "/Locations"},
            {"name": "Magic System", "path": "/Magic System"},
            {"name": "Notes", "path": "/Notes"}
        ],
        "documents": [
            {"type": "character", "folder": "Characters", "count": 4},
            {"type": "chapter", "folder": "Chapters", "count": 8},
            {"type": "location", "folder": "Locations", "count": 3},
            {"type": "notes", "folder": "Notes", "count": 2}
        ]
    }
    
    SCIFI_THRILLER = {
        "genre": "scifi",
        "folders": [
            {"name": "Characters", "path": "/Characters"},
            {"name": "Chapters", "path": "/Chapters"},
            {"name": "Technology", "path": "/Technology"},
            {"name": "Locations", "path": "/Locations"},
            {"name": "Research", "path": "/Research"}
        ],
        "documents": [
            {"type": "character", "folder": "Characters", "count": 3},
            {"type": "chapter", "folder": "Chapters", "count": 6},
            {"type": "location", "folder": "Locations", "count": 2},
            {"type": "notes", "folder": "Technology", "count": 2},
            {"type": "notes", "folder": "Research", "count": 1}
        ]
    }
    
    MYSTERY_NOVEL = {
        "genre": "mystery",
        "folders": [
            {"name": "Characters", "path": "/Characters"},
            {"name": "Chapters", "path": "/Chapters"},
            {"name": "Clues", "path": "/Clues"},
            {"name": "Timeline", "path": "/Timeline"},
            {"name": "Notes", "path": "/Notes"}
        ],
        "documents": [
            {"type": "character", "folder": "Characters", "count": 5},
            {"type": "chapter", "folder": "Chapters", "count": 10},
            {"type": "notes", "folder": "Clues", "count": 3},
            {"type": "notes", "folder": "Timeline", "count": 1},
            {"type": "notes", "folder": "Notes", "count": 2}
        ]
    }