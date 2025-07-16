"""
Integration tests for end-to-end workflows

These tests verify that multiple components work together correctly
in realistic user scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any, List

from src.main import app
from src.database.factory import init_repositories, reset_repositories, get_repositories


class TestProjectCreationWorkflow:
    """Test complete project creation and setup workflow"""
    
    @pytest.fixture(autouse=True)
    async def setup_repositories(self):
        """Set up memory repositories for each test"""
        reset_repositories()
        init_repositories(backend="memory")
        yield
        reset_repositories()
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    async def test_complete_project_setup_workflow(self, client: TestClient):
        """Test creating a project and setting up its complete structure"""
        repos = get_repositories()
        
        # Step 1: Create a new project via repository
        project_data = {
            "id": "novel-project",
            "title": "My Fantasy Novel",
            "description": "An epic fantasy story about dragons and magic",
            "tags": ["fantasy", "novel", "dragons"],
            "collaborators": [
                {
                    "user_id": "author_123",
                    "role": "owner",
                    "name": "Jane Author",
                    "avatar": "https://example.com/avatar.jpg"
                }
            ],
            "settings": {
                "auto_save_interval": 30000,
                "word_count_target": 80000,
                "backup_enabled": True
            }
        }
        
        project = await repos.project.create(project_data)
        assert project.title == "My Fantasy Novel"
        
        # Step 2: Create folder structure via file tree
        # Root folders
        characters_folder = await repos.file_tree.create({
            "id": "folder-characters",
            "project_id": project.id,
            "name": "Characters",
            "type": "folder",
            "path": "/Characters",
            "parent_id": None,
            "icon": "users",
            "tags": ["character", "development"]
        })
        
        chapters_folder = await repos.file_tree.create({
            "id": "folder-chapters",
            "project_id": project.id,
            "name": "Chapters",
            "type": "folder",
            "path": "/Chapters",
            "parent_id": None,
            "icon": "book",
            "tags": ["story", "content"]
        })
        
        worldbuilding_folder = await repos.file_tree.create({
            "id": "folder-worldbuilding",
            "project_id": project.id,
            "name": "Worldbuilding",
            "type": "folder",
            "path": "/Worldbuilding",
            "parent_id": None,
            "icon": "globe",
            "tags": ["worldbuilding", "background"]
        })
        
        # Subfolders
        protagonists_folder = await repos.file_tree.create({
            "id": "folder-protagonists",
            "project_id": project.id,
            "name": "Protagonists",
            "type": "folder",
            "path": "/Characters/Protagonists",
            "parent_id": characters_folder.id,
            "icon": "star",
            "tags": ["character", "protagonist"]
        })
        
        locations_folder = await repos.file_tree.create({
            "id": "folder-locations",
            "project_id": project.id,
            "name": "Locations",
            "type": "folder",
            "path": "/Worldbuilding/Locations",
            "parent_id": worldbuilding_folder.id,
            "icon": "map-pin",
            "tags": ["location", "geography"]
        })
        
        # Step 3: Create documents via API
        # Character document
        char_doc_request = {
            "project_id": project.id,
            "title": "Aria Stormwind - Main Protagonist",
            "path": "/Characters/Protagonists/aria_stormwind.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Aria Stormwind"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "Age: 23\nOccupation: Dragon Rider\nHometown: Windmere"}
                        ]
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Background"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "Aria grew up in the mountain village of Windmere, where she discovered her rare ability to communicate with dragons. Her journey begins when an ancient dragon egg hatches in her presence, bonding her to Zephyr, a storm dragon."}
                        ]
                    }
                ]
            },
            "tags": ["character", "protagonist", "dragon-rider"],
            "file_tree_parent_id": protagonists_folder.id
        }
        
        char_response = client.post("/api/v1/documents", json=char_doc_request)
        assert char_response.status_code == 200
        char_doc = char_response.json()
        
        # Chapter document
        chapter_doc_request = {
            "project_id": project.id,
            "title": "Chapter 1: The Awakening",
            "path": "/Chapters/chapter_01.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Chapter 1: The Awakening"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "The morning mist clung to the peaks of Windmere like a gossamer shroud, and Aria Stormwind knew that everything was about to change. The dragon egg she had found three months ago in the ancient cave was pulsing with an inner light, its crystalline surface cracking with hairline fractures that seemed to spell out runes in a language she couldn't read but somehow understood."}
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "She had hidden the egg from everyone, even her closest friend Marcus, knowing instinctively that some secrets were too dangerous to share. But now, as the egg trembled in her hands and warmth spread through her fingers, she realized that the choice was no longer hers to make."}
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "The egg cracked open with a sound like distant thunder, and a small head emerged—scales the color of storm clouds, eyes like lightning, and a gaze that seemed to look straight into her soul. In that moment, Aria knew her old life was over, and her true adventure was just beginning."}
                        ]
                    }
                ]
            },
            "tags": ["chapter", "opening", "dragon-hatching"],
            "file_tree_parent_id": chapters_folder.id
        }
        
        chapter_response = client.post("/api/v1/documents", json=chapter_doc_request)
        assert chapter_response.status_code == 200
        chapter_doc = chapter_response.json()
        
        # Location document
        location_doc_request = {
            "project_id": project.id,
            "title": "Windmere Village",
            "path": "/Worldbuilding/Locations/windmere.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Windmere Village"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "Population: ~500\nElevation: 8,000 feet\nClimate: Alpine, cold winters, mild summers"}
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "Windmere is a small mountain village nestled high in the Thornpeak Mountains. Known for its stone houses with slate roofs and its ancient dragon shrine, the village has a long history of dragon sightings and mysterious disappearances."}
                        ]
                    }
                ]
            },
            "tags": ["location", "village", "mountains"],
            "file_tree_parent_id": locations_folder.id
        }
        
        location_response = client.post("/api/v1/documents", json=location_doc_request)
        assert location_response.status_code == 200
        location_doc = location_response.json()
        
        # Step 4: Create file tree items that reference the documents
        char_file = await repos.file_tree.create({
            "id": "file-aria",
            "project_id": project.id,
            "name": "aria_stormwind.md",
            "type": "file",
            "path": "/Characters/Protagonists/aria_stormwind.md",
            "parent_id": protagonists_folder.id,
            "document_id": char_doc["id"],
            "icon": "user",
            "tags": ["character", "protagonist"],
            "word_count": char_doc["word_count"]
        })
        
        chapter_file = await repos.file_tree.create({
            "id": "file-chapter1",
            "project_id": project.id,
            "name": "chapter_01.md",
            "type": "file",
            "path": "/Chapters/chapter_01.md",
            "parent_id": chapters_folder.id,
            "document_id": chapter_doc["id"],
            "icon": "file-text",
            "tags": ["chapter", "story"],
            "word_count": chapter_doc["word_count"]
        })
        
        location_file = await repos.file_tree.create({
            "id": "file-windmere",
            "project_id": project.id,
            "name": "windmere.md",
            "type": "file",
            "path": "/Worldbuilding/Locations/windmere.md",
            "parent_id": locations_folder.id,
            "document_id": location_doc["id"],
            "icon": "map-pin",
            "tags": ["location", "worldbuilding"],
            "word_count": location_doc["word_count"]
        })
        
        # Step 5: Verify the complete structure via API
        # Get project details
        project_response = client.get(f"/api/v1/projects/{project.id}")
        assert project_response.status_code == 200
        project_data = project_response.json()
        
        assert project_data["title"] == "My Fantasy Novel"
        assert project_data["document_count"] == 3
        assert project_data["word_count"] > 0
        
        # Get file tree
        file_tree_response = client.get(f"/api/v1/projects/{project.id}/file-tree")
        assert file_tree_response.status_code == 200
        file_tree_data = file_tree_response.json()
        
        assert file_tree_data["metadata"]["total_files"] == 3
        assert file_tree_data["metadata"]["total_folders"] == 5
        
        # Verify hierarchical structure
        tree = file_tree_data["file_tree"]
        assert len(tree) == 3  # 3 root folders
        
        # Find and verify Characters folder hierarchy
        characters = next(item for item in tree if item["name"] == "Characters")
        assert len(characters["children"]) == 1  # Protagonists subfolder
        
        protagonists = characters["children"][0]
        assert protagonists["name"] == "Protagonists"
        assert len(protagonists["children"]) == 1  # Aria file
        
        aria_file = protagonists["children"][0]
        assert aria_file["name"] == "aria_stormwind.md"
        assert aria_file["document_id"] == char_doc["id"]
        assert aria_file["word_count"] == char_doc["word_count"]
        
        # Verify documents can be retrieved
        char_doc_response = client.get(f"/api/v1/documents/{char_doc['id']}")
        assert char_doc_response.status_code == 200
        assert char_doc_response.json()["title"] == "Aria Stormwind - Main Protagonist"
        
        chapter_doc_response = client.get(f"/api/v1/documents/{chapter_doc['id']}")
        assert chapter_doc_response.status_code == 200
        assert chapter_doc_response.json()["title"] == "Chapter 1: The Awakening"
        
        # Step 6: Verify cross-repository consistency
        # All documents should belong to the project
        all_project_docs = await repos.document.get_by_project_id(project.id)
        assert len(all_project_docs) == 3
        
        doc_ids = {doc.id for doc in all_project_docs}
        assert char_doc["id"] in doc_ids
        assert chapter_doc["id"] in doc_ids
        assert location_doc["id"] in doc_ids
        
        # All file tree items should belong to the project
        all_project_files = await repos.file_tree.get_by_project_id(project.id)
        assert len(all_project_files) == 8  # 5 folders + 3 files
        
        # Word counts should be consistent
        total_word_count = sum(doc.word_count for doc in all_project_docs)
        project_word_count = project_data["word_count"]
        assert project_word_count == total_word_count


class TestDocumentLifecycleWorkflow:
    """Test complete document lifecycle with file tree synchronization"""
    
    @pytest.fixture(autouse=True)
    async def setup_repositories(self):
        """Set up memory repositories for each test"""
        reset_repositories()
        init_repositories(backend="memory")
        yield
        reset_repositories()
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    async def base_setup(self):
        """Create base project and folder structure"""
        repos = get_repositories()
        
        # Create project
        project = await repos.project.create({
            "id": "lifecycle-project",
            "title": "Document Lifecycle Test",
            "word_count": 0,
            "document_count": 0
        })
        
        # Create folder
        folder = await repos.file_tree.create({
            "id": "test-folder",
            "project_id": project.id,
            "name": "Test Folder",
            "type": "folder",
            "path": "/Test Folder",
            "parent_id": None
        })
        
        return {"project": project, "folder": folder}
    
    async def test_document_creation_to_deletion_workflow(self, client: TestClient, base_setup):
        """Test complete document lifecycle: create → update → move → delete"""
        project = base_setup["project"]
        folder = base_setup["folder"]
        repos = get_repositories()
        
        # Step 1: Create document via API
        create_request = {
            "project_id": project.id,
            "title": "Test Document Lifecycle",
            "path": "/Test Folder/lifecycle_test.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Initial content for lifecycle test."}]
                    }
                ]
            },
            "tags": ["test", "lifecycle"],
            "file_tree_parent_id": folder.id
        }
        
        create_response = client.post("/api/v1/documents", json=create_request)
        assert create_response.status_code == 200
        document = create_response.json()
        
        # Verify project counts updated
        updated_project = await repos.project.get_by_id(project.id)
        assert updated_project is not None
        assert updated_project.document_count == 1
        assert updated_project.word_count == document["word_count"]
        
        # Step 2: Create corresponding file tree item
        file_item = await repos.file_tree.create({
            "id": "lifecycle-file",
            "project_id": project.id,
            "name": "lifecycle_test.md",
            "type": "file",
            "path": "/Test Folder/lifecycle_test.md",
            "parent_id": folder.id,
            "document_id": document["id"],
            "icon": "file-text",
            "tags": ["test", "lifecycle"],
            "word_count": document["word_count"]
        })
        
        # Step 3: Update document content via API
        update_request = {
            "title": "Updated Document Lifecycle",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Updated Content"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "This is the updated content with much more text to increase the word count significantly. "},
                            {"type": "text", "marks": [{"type": "strong"}], "text": "This is bold text. "},
                            {"type": "text", "text": "And this continues the paragraph with additional content."}
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "A second paragraph with even more content for testing."}
                        ]
                    }
                ]
            },
            "tags": ["test", "lifecycle", "updated"],
            "version": "1.1.0"
        }
        
        update_response = client.put(f"/api/v1/documents/{document['id']}", json=update_request)
        assert update_response.status_code == 200
        updated_document = update_response.json()
        
        assert updated_document["title"] == "Updated Document Lifecycle"
        assert updated_document["version"] == "1.1.0"
        assert updated_document["word_count"] > document["word_count"]
        assert updated_document["tags"] == ["test", "lifecycle", "updated"]
        
        # Verify project word count updated
        project_after_update = await repos.project.get_by_id(project.id)
        assert project_after_update is not None
        assert project_after_update.word_count == updated_document["word_count"]
        
        # Step 4: Update file tree item to match
        await repos.file_tree.update(file_item.id, {
            "word_count": updated_document["word_count"],
            "tags": ["test", "lifecycle", "updated"]
        })
        
        # Step 5: Create new folder and move document
        new_folder = await repos.file_tree.create({
            "id": "new-folder",
            "project_id": project.id,
            "name": "New Folder",
            "type": "folder",
            "path": "/New Folder",
            "parent_id": None
        })
        
        # Move file to new folder
        await repos.file_tree.update(file_item.id, {
            "parent_id": new_folder.id,
            "path": "/New Folder/lifecycle_test.md"
        })
        
        # Step 6: Verify file tree structure
        file_tree_response = client.get(f"/api/v1/projects/{project.id}/file-tree")
        assert file_tree_response.status_code == 200
        file_tree = file_tree_response.json()
        
        # Should have 2 folders and 1 file
        assert file_tree["metadata"]["total_folders"] == 2
        assert file_tree["metadata"]["total_files"] == 1
        
        # Find the file in new location
        new_folder_item = next(item for item in file_tree["file_tree"] if item["name"] == "New Folder")
        assert len(new_folder_item["children"]) == 1
        moved_file = new_folder_item["children"][0]
        assert moved_file["name"] == "lifecycle_test.md"
        assert moved_file["document_id"] == document["id"]
        assert moved_file["word_count"] == updated_document["word_count"]
        
        # Step 7: Delete document via API
        delete_response = client.delete(f"/api/v1/documents/{document['id']}")
        assert delete_response.status_code == 200
        delete_result = delete_response.json()
        assert delete_result["success"] is True
        
        # Verify document is gone
        get_response = client.get(f"/api/v1/documents/{document['id']}")
        assert get_response.status_code == 404
        
        # Verify project counts updated
        final_project = await repos.project.get_by_id(project.id)
        assert final_project is not None
        assert final_project.document_count == 0
        assert final_project.word_count == 0
        
        # Step 8: Clean up file tree item
        await repos.file_tree.delete(file_item.id)
        
        # Verify file tree is clean
        final_file_tree_response = client.get(f"/api/v1/projects/{project.id}/file-tree")
        final_tree = final_file_tree_response.json()
        assert final_tree["metadata"]["total_files"] == 0
        assert final_tree["metadata"]["total_folders"] == 2  # Both folders still exist


class TestCollaborativeWorkflow:
    """Test workflows involving multiple collaborators and concurrent operations"""
    
    @pytest.fixture(autouse=True)
    async def setup_repositories(self):
        """Set up memory repositories for each test"""
        reset_repositories()
        init_repositories(backend="memory")
        yield
        reset_repositories()
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    async def test_multi_user_project_collaboration_workflow(self, client: TestClient):
        """Test workflow with multiple collaborators working on the same project"""
        repos = get_repositories()
        
        # Step 1: Owner creates project
        project_data = {
            "id": "collab-project",
            "title": "Collaborative Story Project",
            "description": "A story written by multiple authors",
            "collaborators": [
                {
                    "user_id": "owner_123",
                    "role": "owner",
                    "name": "Primary Author",
                    "avatar": "https://example.com/owner.jpg"
                }
            ],
            "settings": {
                "auto_save_interval": 30000,
                "backup_enabled": True
            }
        }
        
        project = await repos.project.create(project_data)
        
        # Step 2: Add collaborators to project
        updated_collaborators = [
            {
                "user_id": "owner_123",
                "role": "owner",
                "name": "Primary Author",
                "avatar": "https://example.com/owner.jpg"
            },
            {
                "user_id": "editor_456",
                "role": "editor",
                "name": "Content Editor",
                "avatar": "https://example.com/editor.jpg"
            },
            {
                "user_id": "writer_789",
                "role": "editor",
                "name": "Co-Writer",
                "avatar": None
            },
            {
                "user_id": "reviewer_101",
                "role": "viewer",
                "name": "Beta Reader",
                "avatar": "https://example.com/reviewer.jpg"
            }
        ]
        
        await repos.project.update(project.id, {
            "collaborators": updated_collaborators
        })
        
        # Step 3: Create shared folder structure
        chapters_folder = await repos.file_tree.create({
            "id": "collab-chapters",
            "project_id": project.id,
            "name": "Chapters",
            "type": "folder",
            "path": "/Chapters",
            "parent_id": None,
            "tags": ["shared", "content"]
        })
        
        notes_folder = await repos.file_tree.create({
            "id": "collab-notes",
            "project_id": project.id,
            "name": "Shared Notes",
            "type": "folder",
            "path": "/Shared Notes",
            "parent_id": None,
            "tags": ["notes", "collaboration"]
        })
        
        # Step 4: Owner creates initial chapter
        owner_chapter_request = {
            "project_id": project.id,
            "title": "Chapter 1: The Meeting",
            "path": "/Chapters/chapter_01.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Chapter 1: The Meeting"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "Sarah walked into the coffee shop, scanning the room for her mysterious contact. The email had been cryptic: 'Meet me at Brew & Bean at 3 PM. Look for the red scarf.' Now, surrounded by the aroma of fresh coffee and the chatter of afternoon customers, she wondered if she had made a mistake."}
                        ]
                    }
                ]
            },
            "tags": ["chapter", "opening", "owner-created"]
        }
        
        owner_chapter_response = client.post("/api/v1/documents", json=owner_chapter_request)
        assert owner_chapter_response.status_code == 200
        owner_chapter = owner_chapter_response.json()
        
        # Step 5: Editor adds collaborative notes
        editor_notes_request = {
            "project_id": project.id,
            "title": "Story Notes and Ideas",
            "path": "/Shared Notes/story_notes.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Story Development Notes"}]
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Character Development"}]
                    },
                    {
                        "type": "bullet_list",
                        "content": [
                            {
                                "type": "list_item",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Sarah - protagonist, investigative journalist"}]
                                    }
                                ]
                            },
                            {
                                "type": "list_item",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Mysterious contact - reveal identity in Chapter 3"}]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Plot Points"}]
                    },
                    {
                        "type": "bullet_list",
                        "content": [
                            {
                                "type": "list_item",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Chapter 1: Initial meeting and setup"}]
                                    }
                                ]
                            },
                            {
                                "type": "list_item",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Chapter 2: First clue revealed"}]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "tags": ["notes", "planning", "collaborative"]
        }
        
        editor_notes_response = client.post("/api/v1/documents", json=editor_notes_request)
        assert editor_notes_response.status_code == 200
        editor_notes = editor_notes_response.json()
        
        # Step 6: Co-writer continues the story
        cowriter_chapter_request = {
            "project_id": project.id,
            "title": "Chapter 2: The Revelation",
            "path": "/Chapters/chapter_02.md",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Chapter 2: The Revelation"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "The woman with the red scarf looked up as Sarah approached. Her eyes were sharp, intelligent, and held a hint of desperation that made Sarah's journalistic instincts perk up immediately."}
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "'You came,' the woman said simply. 'I wasn't sure you would.' She gestured to the seat across from her. 'Please, sit. What I'm about to tell you will change everything you think you know about the Morrison case.'"}
                        ]
                    }
                ]
            },
            "tags": ["chapter", "continuation", "cowriter-created"]
        }
        
        cowriter_chapter_response = client.post("/api/v1/documents", json=cowriter_chapter_request)
        assert cowriter_chapter_response.status_code == 200
        cowriter_chapter = cowriter_chapter_response.json()
        
        # Step 7: Simulate document locking for editing
        # Lock the first chapter for editing
        await repos.document.update(owner_chapter["id"], {
            "is_locked": True,
            "locked_by": "editor_456"
        })
        
        # Step 8: Editor updates the locked document
        edit_update_request = {
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Chapter 1: The Meeting"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "Sarah walked into the coffee shop, scanning the room for her mysterious contact. The email had been cryptic: 'Meet me at Brew & Bean at 3 PM. Look for the red scarf.' Now, surrounded by the aroma of fresh coffee and the chatter of afternoon customers, she wondered if she had made a mistake."}
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "She ordered a latte and found a table near the window, positioning herself so she could watch the entrance. The red scarf instruction had seemed odd, but then again, everything about this situation was odd. Three days ago, she had been investigating a routine corporate scandal. Now she was meeting a stranger who claimed to have information that would 'change everything.'"}
                        ]
                    }
                ]
            },
            "version": "1.1.0"
        }
        
        edit_response = client.put(f"/api/v1/documents/{owner_chapter['id']}", json=edit_update_request)
        assert edit_response.status_code == 200
        edited_chapter = edit_response.json()
        
        # Unlock the document
        await repos.document.update(owner_chapter["id"], {
            "is_locked": False,
            "locked_by": None
        })
        
        # Step 9: Create file tree items for all documents
        await repos.file_tree.create({
            "id": "file-chapter1",
            "project_id": project.id,
            "name": "chapter_01.md",
            "type": "file",
            "path": "/Chapters/chapter_01.md",
            "parent_id": chapters_folder.id,
            "document_id": owner_chapter["id"],
            "icon": "file-text",
            "tags": ["chapter", "opening"],
            "word_count": edited_chapter["word_count"]
        })
        
        await repos.file_tree.create({
            "id": "file-chapter2",
            "project_id": project.id,
            "name": "chapter_02.md",
            "type": "file",
            "path": "/Chapters/chapter_02.md",
            "parent_id": chapters_folder.id,
            "document_id": cowriter_chapter["id"],
            "icon": "file-text",
            "tags": ["chapter", "continuation"],
            "word_count": cowriter_chapter["word_count"]
        })
        
        await repos.file_tree.create({
            "id": "file-notes",
            "project_id": project.id,
            "name": "story_notes.md",
            "type": "file",
            "path": "/Shared Notes/story_notes.md",
            "parent_id": notes_folder.id,
            "document_id": editor_notes["id"],
            "icon": "sticky-note",
            "tags": ["notes", "planning"],
            "word_count": editor_notes["word_count"]
        })
        
        # Step 10: Verify final project state
        final_project_response = client.get(f"/api/v1/projects/{project.id}")
        assert final_project_response.status_code == 200
        final_project = final_project_response.json()
        
        # Should have 4 collaborators
        assert len(final_project["collaborators"]) == 4
        
        # Should have 3 documents
        assert final_project["document_count"] == 3
        
        # Word count should be sum of all documents
        total_words = edited_chapter["word_count"] + cowriter_chapter["word_count"] + editor_notes["word_count"]
        assert final_project["word_count"] == total_words
        
        # Verify file tree structure
        file_tree_response = client.get(f"/api/v1/projects/{project.id}/file-tree")
        assert file_tree_response.status_code == 200
        file_tree = file_tree_response.json()
        
        assert file_tree["metadata"]["total_files"] == 3
        assert file_tree["metadata"]["total_folders"] == 2
        
        # Verify chapters folder has 2 files
        chapters = next(item for item in file_tree["file_tree"] if item["name"] == "Chapters")
        assert len(chapters["children"]) == 2
        
        # Verify notes folder has 1 file
        notes = next(item for item in file_tree["file_tree"] if item["name"] == "Shared Notes")
        assert len(notes["children"]) == 1
        
        # Step 11: Verify all documents are accessible and have correct content
        chapter1_response = client.get(f"/api/v1/documents/{owner_chapter['id']}")
        assert chapter1_response.status_code == 200
        chapter1_final = chapter1_response.json()
        assert chapter1_final["version"] == "1.1.0"
        assert chapter1_final["is_locked"] is False
        assert len(chapter1_final["content"]["content"]) == 3  # Should have 3 paragraphs after edit
        
        chapter2_response = client.get(f"/api/v1/documents/{cowriter_chapter['id']}")
        assert chapter2_response.status_code == 200
        chapter2_final = chapter2_response.json()
        assert "Morrison case" in str(chapter2_final["content"])
        
        notes_response = client.get(f"/api/v1/documents/{editor_notes['id']}")
        assert notes_response.status_code == 200
        notes_final = notes_response.json()
        assert "Character Development" in str(notes_final["content"])