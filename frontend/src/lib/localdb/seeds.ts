import { db } from './db';
import { generateProjectId, generateDocumentId, generateFileTreeId, generateTagId } from '../utils/id';

export async function seedSampleProject(userId?: string): Promise<string> {
  const now = new Date().toISOString();
  const projectId = generateProjectId();
  
  await db.transaction('rw', [db.projects, db.documents, db.fileTree, db.tags, db.meta], async () => {
    // Create project
    await db.projects.add({
      id: projectId,
      title: 'Sample Fantasy Novel',
      description: 'A sample project with characters, locations, and chapters',
      ownerId: userId,
      createdBy: userId,
      collaborators: [],
      wordCount: 0,
      documentCount: 3,
      settings: {
        theme: 'fantasy',
        autoSave: true
      },
      tags: ['fantasy', 'novel', 'demo'],
      createdAt: now,
      updatedAt: now
    });

    // Create file tree structure
    const charactersFolder = generateFileTreeId();
    const protagonistsFolder = generateFileTreeId();
    const locationsFolder = generateFileTreeId();
    const settlementsFolder = generateFileTreeId();
    const chaptersFolder = generateFileTreeId();

    await db.fileTree.bulkAdd([
      { 
        id: charactersFolder, 
        projectId, 
        name: 'characters', 
        type: 'folder', 
        path: '/characters',
        tags: [],
        createdAt: now,
        updatedAt: now
      },
      { 
        id: protagonistsFolder, 
        projectId, 
        name: 'protagonists', 
        type: 'folder', 
        path: '/characters/protagonists', 
        parentId: charactersFolder,
        tags: [],
        createdAt: now,
        updatedAt: now
      },
      { 
        id: locationsFolder, 
        projectId, 
        name: 'locations', 
        type: 'folder', 
        path: '/locations',
        tags: [],
        createdAt: now,
        updatedAt: now
      },
      { 
        id: settlementsFolder, 
        projectId, 
        name: 'settlements', 
        type: 'folder', 
        path: '/locations/settlements', 
        parentId: locationsFolder,
        tags: [],
        createdAt: now,
        updatedAt: now
      },
      { 
        id: chaptersFolder, 
        projectId, 
        name: 'chapters', 
        type: 'folder', 
        path: '/chapters',
        tags: [],
        createdAt: now,
        updatedAt: now
      }
    ]);

    // Create documents
    const elaraDoc = generateDocumentId();
    const hometownDoc = generateDocumentId();
    const ch1Doc = generateDocumentId();
    
    await db.documents.bulkAdd([
      {
        id: elaraDoc,
        projectId,
        path: '/characters/protagonists/elara.md',
        title: 'Elara Stormwind',
        version: '1.0.0',
        isLocked: false,
        wordCount: 45,
        tags: ['fire-magic', 'protagonist'],
        createdAt: now,
        updatedAt: now,
        content: {
          type: 'doc',
          content: [
            {
              type: 'heading',
              attrs: { level: 1 },
              content: [{ type: 'text', text: 'Elara Stormwind' }]
            },
            {
              type: 'paragraph',
              content: [
                { 
                  type: 'text', 
                  text: 'Elara is a powerful fire mage from ' 
                },
                { 
                  type: 'text', 
                  text: '@locations/settlements/hometown',
                  marks: [{ type: 'reference', attrs: { path: '/locations/settlements/hometown' } }]
                },
                { 
                  type: 'text', 
                  text: '. She discovered her abilities at age 16 when her emotions ran high during a village festival.' 
                }
              ]
            },
            {
              type: 'heading',
              attrs: { level: 2 },
              content: [{ type: 'text', text: 'Abilities' }]
            },
            {
              type: 'bulletList',
              content: [
                {
                  type: 'listItem',
                  content: [
                    {
                      type: 'paragraph',
                      content: [{ type: 'text', text: 'Fire manipulation and creation' }]
                    }
                  ]
                },
                {
                  type: 'listItem',
                  content: [
                    {
                      type: 'paragraph',
                      content: [{ type: 'text', text: 'Heat resistance' }]
                    }
                  ]
                },
                {
                  type: 'listItem',
                  content: [
                    {
                      type: 'paragraph',
                      content: [{ type: 'text', text: 'Enhanced reflexes when channeling magic' }]
                    }
                  ]
                }
              ]
            }
          ]
        }
      },
      {
        id: hometownDoc,
        projectId,
        path: '/locations/settlements/hometown.md',
        title: 'Millhaven',
        version: '1.0.0',
        isLocked: false,
        wordCount: 38,
        tags: ['settlement', 'peaceful'],
        createdAt: now,
        updatedAt: now,
        content: {
          type: 'doc',
          content: [
            {
              type: 'heading',
              attrs: { level: 1 },
              content: [{ type: 'text', text: 'Millhaven' }]
            },
            {
              type: 'paragraph',
              content: [
                { 
                  type: 'text', 
                  text: 'A peaceful farming village nestled in the valley between the Whispering Hills. Home to ' 
                },
                { 
                  type: 'text', 
                  text: '@characters/protagonists/elara',
                  marks: [{ type: 'reference', attrs: { path: '/characters/protagonists/elara' } }]
                },
                { 
                  type: 'text', 
                  text: ' and about 300 other residents.' 
                }
              ]
            },
            {
              type: 'paragraph',
              content: [
                { 
                  type: 'text', 
                  text: 'The village is known for its annual Harvest Festival, where the discovery of Elara\'s powers changed everything.' 
                }
              ]
            }
          ]
        }
      },
      {
        id: ch1Doc,
        projectId,
        path: '/chapters/chapter-1.md',
        title: 'Chapter 1: The Awakening',
        version: '1.0.0',
        isLocked: false,
        wordCount: 52,
        tags: ['chapter', 'opening', 'fire-magic'],
        createdAt: now,
        updatedAt: now,
        content: {
          type: 'doc',
          content: [
            {
              type: 'heading',
              attrs: { level: 1 },
              content: [{ type: 'text', text: 'Chapter 1: The Awakening' }]
            },
            {
              type: 'paragraph',
              content: [
                { 
                  type: 'text', 
                  text: 'The morning mist clung to the cobblestones of ' 
                },
                { 
                  type: 'text', 
                  text: '@locations/settlements/hometown',
                  marks: [{ type: 'reference', attrs: { path: '/locations/settlements/hometown' } }]
                },
                { 
                  type: 'text', 
                  text: ' as ' 
                },
                { 
                  type: 'text', 
                  text: '@characters/protagonists/elara',
                  marks: [{ type: 'reference', attrs: { path: '/characters/protagonists/elara' } }]
                },
                { 
                  type: 'text', 
                  text: ' hurried through the market square. Today was different—she could feel it in the air, like the charge before a thunderstorm.' 
                }
              ]
            },
            {
              type: 'paragraph',
              content: [
                { 
                  type: 'text', 
                  text: 'Little did she know that by sunset, her entire world would be ablaze—literally.' 
                }
              ]
            }
          ]
        }
      }
    ]);

    // Create file tree items for documents
    await db.fileTree.bulkAdd([
      {
        id: generateFileTreeId(),
        projectId,
        name: 'elara.md',
        type: 'file',
        path: '/characters/protagonists/elara.md',
        parentId: protagonistsFolder,
        documentId: elaraDoc,
        wordCount: 45,
        icon: 'User',
        tags: ['fire-magic', 'protagonist'],
        createdAt: now,
        updatedAt: now
      },
      {
        id: generateFileTreeId(),
        projectId,
        name: 'hometown.md',
        type: 'file',
        path: '/locations/settlements/hometown.md',
        parentId: settlementsFolder,
        documentId: hometownDoc,
        wordCount: 38,
        icon: 'MapPin',
        tags: ['settlement', 'peaceful'],
        createdAt: now,
        updatedAt: now
      },
      {
        id: generateFileTreeId(),
        projectId,
        name: 'chapter-1.md',
        type: 'file',
        path: '/chapters/chapter-1.md',
        parentId: chaptersFolder,
        documentId: ch1Doc,
        wordCount: 52,
        icon: 'FileText',
        tags: ['chapter', 'opening', 'fire-magic'],
        createdAt: now,
        updatedAt: now
      }
    ]);

    // Create tags
    await db.tags.bulkAdd([
      { 
        id: generateTagId(), 
        projectId, 
        name: 'fire-magic', 
        category: 'magic-system', 
        color: '#ff6b6b', 
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
        name: 'protagonist', 
        category: 'character-role', 
        color: '#4ecdc4', 
        icon: 'Star',
        description: 'Main character of the story',
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
        name: 'chapter', 
        category: 'content-type', 
        color: '#95a5a6', 
        icon: 'Book',
        description: 'Story chapter content',
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
        name: 'opening', 
        category: 'story-structure', 
        color: '#f39c12', 
        icon: 'Play',
        description: 'Beginning of the story',
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
        name: 'settlement', 
        category: 'location-type', 
        color: '#9b59b6', 
        icon: 'Home',
        description: 'Towns and villages',
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
        name: 'peaceful', 
        category: 'mood', 
        color: '#2ecc71', 
        icon: 'Heart',
        description: 'Calm and tranquil atmosphere',
        isGlobal: false,
        isSystem: false,
        isArchived: false,
        usageCount: 1,
        createdAt: now,
        updatedAt: now
      }
    ]);

    // Update meta
    await db.meta.put({ key: 'seedVersion', value: 1 });
    await db.meta.put({ key: 'lastProject', value: projectId });
  });

  return projectId;
}

export async function seedLargeDemo(userId?: string): Promise<string> {
  // For now, just return the sample project
  // TODO: Add more complex data with additional characters, locations, chapters, complex @-references
  return await seedSampleProject(userId);
}