import { db } from './db';
import { generateProjectId, generateDocumentId, generateFileTreeId, generateTagId } from '../utils/id';

// Conditional dev-only imports
let contentGenerators: any = null;
if (process.env.NODE_ENV === 'development') {
  try {
    contentGenerators = require('../dev/content-generators');
  } catch (error) {
    console.warn('Content generators not available:', error);
  }
}

// Enhanced seed function with faker integration
export async function seedSampleProject(userId?: string): Promise<string> {
  const projectId = generateProjectId();
  
  // Use faker-generated content in development, static fallback otherwise
  if (contentGenerators && process.env.NODE_ENV === 'development') {
    return await seedWithFaker(projectId, userId);
  } else {
    return await seedStaticContent(projectId, userId);
  }
}

// Faker-powered seed function (development only)
async function seedWithFaker(projectId: string, userId?: string): Promise<string> {
  const {
    generateProject,
    generateCharacter, 
    generateLocation,
    generateChapter,
    generateTags
  } = contentGenerators;

  await db.transaction('rw', [db.projects, db.documents, db.fileTree, db.tags, db.meta], async () => {
    // Generate random project
    const projectData = await generateProject(userId);
    const theme = projectData.settings?.theme || 'fantasy';
    
    await db.projects.add({
      id: projectId,
      title: 'Sample Fantasy Novel', // Keep basic fallback
      description: 'A sample project with characters, locations, and chapters',
      ownerId: userId,
      createdBy: userId,
      collaborators: [],
      wordCount: 0,
      documentCount: 5, // Will be updated
      settings: { theme: 'fantasy', autoSave: true },
      tags: ['fantasy', 'novel', 'demo'],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      ...projectData
    });

    // Create folder structure
    const charactersFolder = generateFileTreeId();
    const locationsFolder = generateFileTreeId();  
    const chaptersFolder = generateFileTreeId();
    
    await db.fileTree.bulkAdd([
      {
        id: charactersFolder,
        projectId,
        name: 'characters',
        type: 'folder' as const,
        path: '/characters',
        tags: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: locationsFolder, 
        projectId,
        name: 'locations',
        type: 'folder' as const,
        path: '/locations',
        tags: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: chaptersFolder,
        projectId, 
        name: 'chapters',
        type: 'folder' as const,
        path: '/chapters',
        tags: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]);

    // Generate varied content
    const documents = [];
    const fileTreeItems = [];
    
    // Generate 2-3 characters
    for (let i = 0; i < 3; i++) {
      const { document: doc, fileTree: file } = await generateCharacter(theme, projectId, charactersFolder);
      documents.push({ 
        id: generateDocumentId(),
        ...doc
      });
      fileTreeItems.push({
        id: generateFileTreeId(),
        documentId: documents[documents.length - 1].id,
        ...file
      });
    }

    // Generate 2 locations  
    for (let i = 0; i < 2; i++) {
      const { document: doc, fileTree: file } = await generateLocation(theme, projectId, locationsFolder);
      documents.push({
        id: generateDocumentId(),
        ...doc
      });
      fileTreeItems.push({
        id: generateFileTreeId(), 
        documentId: documents[documents.length - 1].id,
        ...file
      });
    }

    // Generate 3 chapters
    for (let i = 1; i <= 3; i++) {
      const { document: doc, fileTree: file } = await generateChapter(theme, projectId, i, chaptersFolder);
      documents.push({
        id: generateDocumentId(),
        ...doc
      });
      fileTreeItems.push({
        id: generateFileTreeId(),
        documentId: documents[documents.length - 1].id, 
        ...file
      });
    }

    // Add all documents and file tree items
    await db.documents.bulkAdd(documents);
    await db.fileTree.bulkAdd(fileTreeItems);

    // Generate tags
    const tags = await generateTags(theme, projectId);
    const resolvedTags = await Promise.all(tags);
    await db.tags.bulkAdd(resolvedTags.map(tag => ({
      id: generateTagId(),
      ...tag
    })));

    // Update project with actual counts
    const totalWordCount = documents.reduce((sum, doc) => sum + (doc.wordCount || 0), 0);
    await db.projects.update(projectId, {
      wordCount: totalWordCount,
      documentCount: documents.length
    });

    // Update meta
    await db.meta.put({ key: 'seedVersion', value: 2 });
    await db.meta.put({ key: 'lastProject', value: projectId });
  });

  return projectId;
}

// Static content fallback (production safe)
async function seedStaticContent(projectId: string, userId?: string): Promise<string> {
  const now = new Date().toISOString();
  
  await db.transaction('rw', [db.projects, db.documents, db.fileTree, db.tags, db.meta], async () => {
    // Create project (original static content)
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

    // Create file tree structure (original static structure)
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
        type: 'folder' as const, 
        path: '/characters',
        tags: [],
        createdAt: now,
        updatedAt: now
      },
      { 
        id: protagonistsFolder, 
        projectId, 
        name: 'protagonists', 
        type: 'folder' as const, 
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
        type: 'folder' as const, 
        path: '/locations',
        tags: [],
        createdAt: now,
        updatedAt: now
      },
      { 
        id: settlementsFolder, 
        projectId, 
        name: 'settlements', 
        type: 'folder' as const, 
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
        type: 'folder' as const, 
        path: '/chapters',
        tags: [],
        createdAt: now,
        updatedAt: now
      }
    ]);

    // Create documents (original static content)
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
                { type: 'text', text: 'A powerful fire mage from the village of Millhaven.' }
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
        type: 'file' as const,
        path: '/characters/protagonists/elara.md',
        parentId: protagonistsFolder,
        documentId: elaraDoc,
        wordCount: 45,
        icon: 'User',
        tags: ['fire-magic', 'protagonist'],
        createdAt: now,
        updatedAt: now
      }
    ]);

    // Create basic tags
    await db.tags.bulkAdd([
      { 
        id: generateTagId(), 
        projectId, 
        name: 'fantasy', 
        category: 'genre', 
        color: '#9b59b6', 
        icon: 'Star',
        description: 'Fantasy genre content',
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

// Enhanced large demo with multiple varied projects (development only)
export async function seedLargeDemo(userId?: string): Promise<string> {
  if (contentGenerators && process.env.NODE_ENV === 'development') {
    // Generate 3-5 varied projects with different themes
    const projectIds = [];
    
    for (let i = 0; i < 3; i++) {
      const projectId = await seedSampleProject(userId);
      projectIds.push(projectId);
    }
    
    return projectIds[0]; // Return first project ID
  } else {
    // Fallback to single project
    return await seedSampleProject(userId);
  }
}