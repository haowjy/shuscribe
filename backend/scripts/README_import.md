# Story Import Documentation

## Overview
This directory contains scripts for importing stories from various formats into the ShuScribe file-based database system.

## Import Script (`import_story.py`)

### Features
- **Temporary Staging**: All imports are first created in a `temp/` directory for safety
- **Complete Metadata Extraction**: Extracts title, author, synopsis, genres, tags, publication status
- **Chapter Import**: Converts XML chapters to Markdown with YAML frontmatter
- **Automatic Statistics**: Calculates word counts and chapter statistics
- **Safe Moving**: Moves from temp to final location only after successful import

### Usage

#### Import Pokemon Amber (built-in example)
```bash
python import_story.py --pokemon-amber
```

#### Import Custom Story
```bash
python import_story.py --story-dir /path/to/story --workspace-dir /path/to/workspace
```

#### Temp Directory Management
```bash
# List temporary workspaces
python import_story.py --list-temp

# Clean up temporary workspaces
python import_story.py --cleanup-temp
```

### Import Process
1. **Temp Creation**: Creates unique temp workspace with timestamp
2. **Import to Temp**: Imports all data to temporary location
3. **Verification**: Import completes in temp for verification
4. **Safe Move**: Moves to final location if target doesn't exist
5. **Conflict Handling**: Warns if final location exists, keeps temp copy

### Temp Directory Structure
```
backend/
├── temp/
│   └── workspace_pokemon_amber_20250630_010924/  # Timestamped temp workspace
│       ├── .shuscribe/
│       ├── story/
│       ├── wiki/
│       └── ...
└── workspace_pokemon_amber/  # Final location (if moved)
```

## Verification Script (`verify_import.py`)

Verifies imported workspaces by checking:
- User and workspace data
- Story metadata completeness
- Chapter count and content
- Database API functionality

```bash
python verify_import.py
```

## XML Format Support

### Metadata Structure
```xml
<StoryMetadata>
    <Title>Story Title</Title>
    <Author>Author Name</Author>
    <Synopsis>Story description...</Synopsis>
    <Genres>
        <Genre name="Fantasy" />
        <Genre name="Adventure" />
    </Genres>
    <Tags>
        <Tag name="Tag1" />
        <Tag name="Tag2" />
    </Tags>
    <Status>In Progress</Status>
    <DateCreated>2025-06-26</DateCreated>
    <LastUpdated>2025-06-26</LastUpdated>
    <Copyright>© 2025 Author. All rights reserved.</Copyright>
</StoryMetadata>
```

### Directory Structure
```
story_directory/
├── _meta.xml          # Story metadata
├── 1.xml             # Chapter 1
├── 2.xml             # Chapter 2
└── ...
```

## Database Integration

The import creates a complete ShuScribe workspace with:

- **File-based storage** with atomic writes and threading locks
- **Encrypted API keys** for secure configuration
- **Human-readable formats** (Markdown + YAML frontmatter)
- **Complete metadata** including genres, tags, publication status
- **Chapter statistics** with word counts and publication tracking
- **Wiki system** ready for expansion

## Error Handling

- **XML Parsing**: Handles malformed XML gracefully
- **File Conflicts**: Prevents overwriting existing workspaces
- **Metadata Validation**: Ensures required fields are present  
- **Temp Safety**: Isolates imports until verified
- **Cleanup Tools**: Manages temporary workspace cleanup

## Status Mapping

XML Status → Database Status:
- "Complete" → "completed"
- "In Progress" → "in_progress"
- "On Hiatus" → "on_hiatus"
- "Discontinued" → "discontinued"
- "Draft" → "draft"

## 📁 Available Scripts

### `import_story.py`
Imports stories from XML directory format (like Pokemon Amber) into the database structure.

### `verify_import.py`
Verifies that imported stories can be read correctly through the database API.

## 🚀 Usage

### Import Pokemon Amber (Example)
```bash
# From the backend directory
source .venv/bin/activate
python scripts/import_story.py --pokemon-amber
```

This will:
- Create a new workspace at `backend/workspace_pokemon_amber/`
- Import all 17 chapters with proper metadata
- Set up the complete file structure for ShuScribe

### Import Any XML Directory Story
```bash
python scripts/import_story.py --story-dir /path/to/story --workspace-dir /path/to/workspace
```

**Expected story directory structure:**
```
story_directory/
├── _meta.xml              # Story metadata
├── 1.xml                  # Chapter files (numbered)
├── 2.xml
├── 3.xml
└── ...
```

### Verify Import
```bash
python scripts/verify_import.py
```

## 📋 What Gets Imported

### Story Metadata (`_meta.xml`)
- Title, Author, Synopsis
- Genres and Tags
- Publication status
- Creation/update dates

### Chapters (numbered `.xml` files)
- Chapter content (XML wrapper stripped)
- Chapter titles (extracted from content)
- Word counts (automatically calculated)
- Published status (all imported as published)

## 🗂️ Generated File Structure

After import, you'll have a complete ShuScribe workspace:

```
workspace_directory/
├── .shuscribe/                 # System files (secure permissions)
│   ├── config.json            # User config + API keys
│   ├── workspace.json         # Workspace metadata
│   ├── chapters_index.json    # Fast chapter lookups
│   └── articles_index.json    # Wiki article index
├── story/
│   ├── metadata.json          # Story metadata
│   ├── chapters/              # Published chapters as Markdown
│   │   ├── chapter_001.md
│   │   ├── chapter_002.md
│   │   └── ...
│   └── drafts/                # Draft chapters
├── wiki/                      # Current wiki articles (by category)
│   ├── characters/
│   ├── locations/
│   ├── concepts/
│   └── ...
├── wiki-versions/             # Chapter-specific wiki versions
├── notes/                     # Author notes
└── conversations/             # AI conversations
```

## 📄 Chapter Format

Chapters are converted to Markdown with YAML frontmatter:

```markdown
---
id: de359ab7-5d56-47ca-9f4a-35781c40d0ec
title: [Chapter 1] Truck-kun Strikes Again
chapter_number: 1
status: published
word_count: 2405
created_at: 2025-06-30T00:41:31.807650
updated_at: 
published_at: 2025-06-30T00:41:31.807650
---

# [Chapter 1] Truck-kun Strikes Again

Chapter content goes here...
```

## 🔧 Database Access

After import, you can access the data through the database API:

```python
from src.database.factory import get_repositories
from pathlib import Path

# Get repositories for the workspace
repos = get_repositories(
    backend="file", 
    workspace_path=Path("workspace_pokemon_amber")
)

# Get story metadata
metadata = await repos["story"].get_story_metadata(workspace_id)

# Get chapters
chapters = await repos["story"].get_chapters_by_workspace(workspace_id)

# Get specific chapter
chapter = await repos["story"].get_chapter_by_number(workspace_id, 1)
```

## ✅ Success Verification

The import creates:
- ✅ User configuration with local settings
- ✅ Workspace with story metadata
- ✅ All chapters converted to Markdown
- ✅ Proper file structure and permissions
- ✅ Fast lookup indexes
- ✅ Complete database API access

**Pokemon Amber Import Results:**
- 📚 Story: "Pokemon: Ambertwo" by ChronicImmortality  
- 📄 17 chapters imported (47,351 total words)
- 🔧 Full ShuScribe database compatibility
- 🎯 Ready for AI processing and wiki generation

## 🛠️ Extending

To import other formats:
1. Create a new loader in `StoryImporter`
2. Add format detection logic
3. Follow the same conversion pattern to database models
4. Test with verification script

The import system is designed to be extensible for various input formats while maintaining the same output structure. 