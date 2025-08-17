/**
 * Enhanced seeding functions using markdown-to-ProseMirror conversion
 * Creates realistic content that showcases TipTap editor capabilities
 */

import { db } from '../../localdb/db';
import { generateProjectId, generateDocumentId, generateFileTreeId, generateTagId } from '../../utils/id';
import { markdownToProseMirror, calculateWordCount } from '../parsers/markdown-parser';
import { CONTENT_TEMPLATES, TEMPLATE_METADATA } from '../content/templates';
import type { Project, Document, FileTreeItem, Tag } from '../../localdb/types';

// Enhanced seed function using realistic markdown content
export async function seedSampleProject(userId?: string): Promise<string> {
  const projectId = generateProjectId();
  const now = new Date().toISOString();
  
  await db.transaction('rw', [db.projects, db.documents, db.fileTree, db.tags, db.meta], async () => {
    // Create project with realistic settings
    const project: Project = {
      id: projectId,
      title: 'The Chronicles of Aethermoor',
      description: 'An epic fantasy novel featuring elemental magic, political intrigue, and character-driven storytelling.',
      ownerId: userId,
      createdBy: userId,
      collaborators: [],
      wordCount: 0, // Will be calculated from documents
      documentCount: 0, // Will be calculated from documents
      settings: {
        theme: 'fantasy',
        autoSave: true,
        wordCountGoal: 80000,
        chapterGoal: 20,
        targetAudience: 'Young Adult',
        genre: 'Epic Fantasy'
      },
      tags: ['fantasy', 'novel', 'magic', 'adventure'],
      createdAt: now,
      updatedAt: now,
    };

    await db.projects.add(project);

    // Create folder structure
    const folders = await createProjectFolders(projectId, now);
    
    // Create documents with rich content
    const documents = await createProjectDocuments(projectId, folders, userId, now);
    
    // Create project tags
    const tags = await createProjectTags(projectId, now);
    
    // Calculate and update project statistics
    const totalWordCount = documents.reduce((sum, doc) => sum + (doc.wordCount || 0), 0);
    await db.projects.update(projectId, {
      wordCount: totalWordCount,
      documentCount: documents.length,
      updatedAt: now
    });

    // Update meta information
    await db.meta.put({ key: 'seedVersion', value: 3 });
    await db.meta.put({ key: 'lastProject', value: projectId });
    await db.meta.put({ key: 'seedType', value: 'enhanced-markdown' });
  });

  return projectId;
}

// Create organized folder structure
async function createProjectFolders(projectId: string, now: string) {
  const folders = {
    characters: generateFileTreeId(),
    protagonists: generateFileTreeId(),
    antagonists: generateFileTreeId(),
    supporting: generateFileTreeId(),
    locations: generateFileTreeId(),
    cities: generateFileTreeId(),
    regions: generateFileTreeId(),
    chapters: generateFileTreeId(),
    worldBuilding: generateFileTreeId(),
    magic: generateFileTreeId(),
    politics: generateFileTreeId(),
    notes: generateFileTreeId(),
    research: generateFileTreeId(),
    timeline: generateFileTreeId(),
  };

  const folderItems: FileTreeItem[] = [
    // Main folders
    {
      id: folders.characters,
      projectId,
      name: 'Characters',
      type: 'folder',
      path: '/characters',
      tags: ['character-development'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.locations,
      projectId,
      name: 'Locations',
      type: 'folder',
      path: '/locations',
      tags: ['world-building'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.chapters,
      projectId,
      name: 'Chapters',
      type: 'folder',
      path: '/chapters',
      tags: ['main-story'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.worldBuilding,
      projectId,
      name: 'World Building',
      type: 'folder',
      path: '/world-building',
      tags: ['reference'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.notes,
      projectId,
      name: 'Notes & Research',
      type: 'folder',
      path: '/notes',
      tags: ['reference', 'planning'],
      createdAt: now,
      updatedAt: now
    },
    
    // Character subfolders
    {
      id: folders.protagonists,
      projectId,
      name: 'Protagonists',
      type: 'folder',
      path: '/characters/protagonists',
      parentId: folders.characters,
      tags: ['main-characters'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.antagonists,
      projectId,
      name: 'Antagonists',
      type: 'folder',
      path: '/characters/antagonists',
      parentId: folders.characters,
      tags: ['villains'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.supporting,
      projectId,
      name: 'Supporting Cast',
      type: 'folder',
      path: '/characters/supporting',
      parentId: folders.characters,
      tags: ['supporting-cast'],
      createdAt: now,
      updatedAt: now
    },
    
    // Location subfolders
    {
      id: folders.cities,
      projectId,
      name: 'Cities & Towns',
      type: 'folder',
      path: '/locations/cities',
      parentId: folders.locations,
      tags: ['settlements'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.regions,
      projectId,
      name: 'Regions & Kingdoms',
      type: 'folder',
      path: '/locations/regions',
      parentId: folders.locations,
      tags: ['geography'],
      createdAt: now,
      updatedAt: now
    },
    
    // World building subfolders
    {
      id: folders.magic,
      projectId,
      name: 'Magic System',
      type: 'folder',
      path: '/world-building/magic',
      parentId: folders.worldBuilding,
      tags: ['magic-system'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.politics,
      projectId,
      name: 'Politics & History',
      type: 'folder',
      path: '/world-building/politics',
      parentId: folders.worldBuilding,
      tags: ['politics', 'history'],
      createdAt: now,
      updatedAt: now
    },
    
    // Notes subfolders
    {
      id: folders.research,
      projectId,
      name: 'Research',
      type: 'folder',
      path: '/notes/research',
      parentId: folders.notes,
      tags: ['research'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.timeline,
      projectId,
      name: 'Timeline',
      type: 'folder',
      path: '/notes/timeline',
      parentId: folders.notes,
      tags: ['timeline', 'plotting'],
      createdAt: now,
      updatedAt: now
    }
  ];

  await db.fileTree.bulkAdd(folderItems);
  return folders;
}

// Create documents with rich markdown content
async function createProjectDocuments(
  projectId: string, 
  folders: any, 
  userId: string | undefined, 
  now: string
) {
  const documents: Document[] = [];
  const fileTreeItems: FileTreeItem[] = [];

  // Character documents
  const characterDoc = createDocument(
    'Elara Stormwind',
    '/characters/protagonists/elara-stormwind.md',
    CONTENT_TEMPLATES.FANTASY_CHARACTER_TEMPLATE,
    projectId,
    userId,
    now,
    ['protagonist', 'fire-magic', 'main-character']
  );
  
  documents.push(characterDoc.document);
  fileTreeItems.push({
    ...characterDoc.fileTreeItem,
    parentId: folders.protagonists,
    icon: 'User'
  });

  // Location documents
  const locationDoc = createDocument(
    'The City of Ravenshore',
    '/locations/cities/ravenshore.md',
    CONTENT_TEMPLATES.FANTASY_LOCATION_TEMPLATE,
    projectId,
    userId,
    now,
    ['city', 'harbor', 'political-center']
  );
  
  documents.push(locationDoc.document);
  fileTreeItems.push({
    ...locationDoc.fileTreeItem,
    parentId: folders.cities,
    icon: 'MapPin'
  });

  // Chapter documents
  const chapterDoc = createDocument(
    'Chapter 1: The Storm\'s Calling',
    '/chapters/chapter-01-storms-calling.md',
    CONTENT_TEMPLATES.FANTASY_CHAPTER_TEMPLATE,
    projectId,
    userId,
    now,
    ['chapter', 'opening', 'storm-magic']
  );
  
  documents.push(chapterDoc.document);
  fileTreeItems.push({
    ...chapterDoc.fileTreeItem,
    parentId: folders.chapters,
    icon: 'BookOpen'
  });

  // World building documents
  const magicSystemDoc = createDocument(
    'Elemental Magic System',
    '/world-building/magic/elemental-system.md',
    createMagicSystemContent(),
    projectId,
    userId,
    now,
    ['magic-system', 'elemental', 'reference']
  );
  
  documents.push(magicSystemDoc.document);
  fileTreeItems.push({
    ...magicSystemDoc.fileTreeItem,
    parentId: folders.magic,
    icon: 'Zap'
  });

  // Research documents
  const researchDoc = createDocument(
    'Medieval Harbor Cities Research',
    '/notes/research/harbor-cities.md',
    CONTENT_TEMPLATES.TECHNICAL_GUIDE_TEMPLATE.replace(
      /TypeScript and Prisma/g, 
      'Medieval Harbor Cities'
    ).substring(0, 2000) + '\n\n*Research notes for world building...*',
    projectId,
    userId,
    now,
    ['research', 'historical', 'world-building']
  );
  
  documents.push(researchDoc.document);
  fileTreeItems.push({
    ...researchDoc.fileTreeItem,
    parentId: folders.research,
    icon: 'Search'
  });

  // Add all documents and file tree items to database
  await db.documents.bulkAdd(documents);
  await db.fileTree.bulkAdd(fileTreeItems);

  return documents;
}

// Helper function to create document and file tree item
function createDocument(
  title: string,
  path: string,
  markdownContent: string,
  projectId: string,
  userId: string | undefined,
  now: string,
  tags: string[]
) {
  const documentId = generateDocumentId();
  const fileTreeId = generateFileTreeId();
  
  const content = markdownToProseMirror(markdownContent);
  const wordCount = calculateWordCount(content);

  const document: Document = {
    id: documentId,
    projectId,
    title,
    path,
    content,
    wordCount,
    version: '1.0.0',
    isLocked: false,
    fileTreeId,
    createdBy: userId,
    updatedBy: userId,
    tags,
    createdAt: now,
    updatedAt: now,
  };

  const fileTreeItem: FileTreeItem = {
    id: fileTreeId,
    projectId,
    name: path.split('/').pop()?.replace('.md', '') || title,
    type: 'file',
    path,
    documentId,
    wordCount,
    tags,
    createdAt: now,
    updatedAt: now,
  };

  return { document, fileTreeItem };
}

// Create magic system content
function createMagicSystemContent(): string {
  return `# Elemental Magic System

## Overview

The magic system in Aethermoor is based on **elemental affinities** that manifest differently in each individual. Magic users, known as **Elementalists**, can typically master one primary element, though rare individuals may develop secondary affinities.

---

## The Four Primary Elements

### Fire Magic
- **Source**: Emotional intensity and inner passion
- **Manifestations**: Flame creation, heat manipulation, lightning (advanced)
- **Practitioners**: Called **Flame Wardens**
- **Weaknesses**: Water magic, emotional suppression

### Water Magic  
- **Source**: Emotional flow and adaptability
- **Manifestations**: Water control, ice creation, healing (rare)
- **Practitioners**: Called **Tide Speakers**
- **Weaknesses**: Earth magic, emotional rigidity

### Earth Magic
- **Source**: Stability and connection to the land
- **Manifestations**: Stone shaping, plant growth, metal forging
- **Practitioners**: Called **Stone Hearts**
- **Weaknesses**: Air magic, disconnection from nature

### Air Magic
- **Source**: Freedom and mental clarity
- **Manifestations**: Wind control, flight, sound manipulation
- **Practitioners**: Called **Wind Dancers**  
- **Weaknesses**: Fire magic, mental confusion

---

## Magic Acquisition & Training

### Natural Awakening
Most elementalists discover their abilities during:
- [x] **Emotional trauma** (most common trigger)
- [x] **Puberty** (ages 13-16 typically)
- [x] **Near-death experiences** (rare but powerful)
- [ ] **Artificial awakening** (dangerous, often fatal)

### Training Stages

| Stage | Duration | Abilities | Risks |
|-------|----------|-----------|-------|
| **Spark** | 0-1 years | Basic manipulation | Accidental discharge |
| **Flame** | 1-5 years | Controlled casting | Power overflow |
| **Inferno** | 5-15 years | Advanced techniques | Elemental corruption |
| **Mastery** | 15+ years | Teaching others | Power stagnation |

---

## Dual Affinities

> *"One who commands two elements commands the storm itself, but risks being torn apart by conflicting forces."*
> 
> — **Archmage Valdris**, *Treatise on Elemental Harmony*

### Known Combinations
- **Fire + Lightning**: Storm magic (Elara's rare gift)
- **Water + Ice**: Frost magic (common in the north)
- **Earth + Metal**: Forge magic (dwarven specialty)
- **Air + Sound**: Song magic (bardic tradition)

### Requirements
- Exceptional mental discipline
- Complementary emotional range
- Years of meditation and balance training
- Usually only achieved by 1 in 10,000 elementalists

---

## Magic Limitations

### Physical Costs
\`\`\`
Energy Drain Formula:
Base Cost + (Power Level × Duration) + Complexity Modifier

Example: Large fireball = 10 + (8 × 3) + 5 = 39 energy points
\`\`\`

### Emotional Requirements
Each element requires specific emotional states:
- **Fire**: Passion, anger, determination
- **Water**: Calm, adaptability, empathy
- **Earth**: Stability, patience, steadfastness  
- **Air**: Joy, freedom, curiosity

### Environmental Factors
- Fire magic weakens in heavy rain
- Water magic struggles in arid deserts
- Earth magic fails over deep water
- Air magic diminishes in enclosed spaces

---

## Forbidden Magic

### Shadow Magic
- **Source**: Drawing power from life force of others
- **Practitioners**: **Shadow Weavers** (universally condemned)
- **Effects**: Rapid aging, soul corruption, madness
- **Legal Status**: Death penalty in all kingdoms

### Blood Magic
- **Source**: Using one's own life force as fuel
- **Risk**: Permanent damage, shortened lifespan
- **Usage**: Only permitted for life-saving healing
- **Regulation**: Strictly monitored by Temple authorities

---

## Cultural Impact

### Social Hierarchy
Magic ability often determines social status:
1. **Archmages** - Rulers and high nobles
2. **Battle Mages** - Military officers and protectors
3. **Guild Mages** - Craftsmen and professionals
4. **Hedge Mages** - Common folk with minor abilities
5. **Nulls** - Non-magical individuals (majority)

### Economic Systems
- **Mage Guilds** control magical industries
- **Enchanted items** drive luxury markets
- **Magical services** (healing, transport) are heavily regulated
- **Anti-magic zones** exist for non-magical commerce

---

**Last Updated**: Current campaign year  
**Source**: *The Elemental Codex*, Imperial Library of Aethermoor  
**Author Notes**: This system allows for character growth while maintaining clear limitations and consequences.`;
}

// Create project tags
async function createProjectTags(projectId: string, now: string) {
  const tags: Tag[] = [
    {
      id: generateTagId(),
      projectId,
      name: 'protagonist',
      category: 'character-type',
      color: '#3b82f6',
      icon: 'Crown',
      description: 'Main character or hero',
      isGlobal: false,
      isSystem: false,
      isArchived: false,
      usageCount: 1,
      createdAt: now,
      updatedAt: now
    },
    {
      id: generateTagId(),
      projectId,
      name: 'fire-magic',
      category: 'magic-type',
      color: '#ef4444',
      icon: 'Flame',
      description: 'Fire-based magical abilities',
      isGlobal: false,
      isSystem: false,
      isArchived: false,
      usageCount: 2,
      createdAt: now,
      updatedAt: now
    },
    {
      id: generateTagId(),
      projectId,
      name: 'world-building',
      category: 'content-type',
      color: '#10b981',
      icon: 'Globe',
      description: 'World and universe development',
      isGlobal: false,
      isSystem: false,
      isArchived: false,
      usageCount: 3,
      createdAt: now,
      updatedAt: now
    },
    {
      id: generateTagId(),
      projectId,
      name: 'main-story',
      category: 'plot',
      color: '#8b5cf6',
      icon: 'BookOpen',
      description: 'Primary narrative content',
      isGlobal: false,
      isSystem: false,
      isArchived: false,
      usageCount: 1,
      createdAt: now,
      updatedAt: now
    },
    {
      id: generateTagId(),
      projectId,
      name: 'reference',
      category: 'content-type',
      color: '#6b7280',
      icon: 'Archive',
      description: 'Reference and research material',
      isGlobal: false,
      isSystem: false,
      isArchived: false,
      usageCount: 2,
      createdAt: now,
      updatedAt: now
    }
  ];

  await db.tags.bulkAdd(tags);
  return tags;
}

// Large demo with multiple projects
export async function seedLargeDemo(userId?: string): Promise<string> {
  // Create the main fantasy project
  const fantasyProjectId = await seedSampleProject(userId);
  
  // For large demo, we could add more projects here
  // but for now, the single project with rich content is sufficient
  
  return fantasyProjectId;
}