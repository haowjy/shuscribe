/**
 * Enhanced seeding functions using dynamic faker-powered content generation
 * 
 * WHY: Creates highly varied, realistic content using faker.js and dynamic templates
 * instead of static templates. Each seed run generates completely different projects
 * with unique names, content, and structures while maintaining professional quality.
 * 
 * This approach showcases TipTap editor capabilities with rich, varied markdown content
 * that's converted to ProseMirror JSON for proper editor display.
 */

import { db } from '../../localdb/db';
import { generateProjectId, generateDocumentId, generateFileTreeId, generateTagId } from '../../utils/id';
import { 
  generateProject,
  generateCharacter, 
  generateLocation, 
  generateChapter,
  generateWorldBuildingDocument,
  generateResearchDocument,
  generateTimelineDocument,
  generateTags
} from '../generators/content-generators';
import { safeFaker, themeGenerators, getRandomTheme, generateThemeContent } from '../generators/faker-utils';
import type { Project, Document, FileTreeItem, Tag } from '../../localdb/types';

// Enhanced seed function using dynamic faker-powered content
export async function seedSampleProject(userId?: string): Promise<string> {
  const projectId = generateProjectId();
  const now = new Date().toISOString();
  
  await db.transaction('rw', [db.projects, db.documents, db.fileTree, db.tags, db.meta], async () => {
    // Generate dynamic project data
    const projectData = await generateProject(userId);
    const theme = projectData.settings?.theme as keyof typeof themeGenerators || 'fantasy';
    
    const project: Project = {
      id: projectId,
      wordCount: 0, // Will be calculated from documents
      documentCount: 0, // Will be calculated from documents
      createdAt: now,
      updatedAt: now,
      ...projectData
    } as Project;

    await db.projects.add(project);

    // Create dynamic folder structure
    const folders = await createDynamicProjectFolders(projectId, theme, now);
    
    // Create varied documents with rich content
    const documents = await createVariedProjectDocuments(projectId, theme, folders, userId, now);
    
    // Create theme-appropriate tags
    const tags = await createDynamicProjectTags(projectId, theme, now);
    
    // Calculate and update project statistics
    const totalWordCount = documents.reduce((sum, doc) => sum + (doc.wordCount || 0), 0);
    await db.projects.update(projectId, {
      wordCount: totalWordCount,
      documentCount: documents.length,
      updatedAt: now
    });

    // Update meta information
    await db.meta.put({ key: 'seedVersion', value: 4 });
    await db.meta.put({ key: 'lastProject', value: projectId });
    await db.meta.put({ key: 'seedType', value: 'dynamic-faker' });
    await db.meta.put({ key: 'projectTheme', value: theme });
  });

  return projectId;
}

// Create dynamic folder structure based on theme
async function createDynamicProjectFolders(projectId: string, theme: keyof typeof themeGenerators, now: string) {
  const helpers = await safeFaker.helpers();
  
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
    system: generateFileTreeId(),
    politics: generateFileTreeId(),
    research: generateFileTreeId(),
    timeline: generateFileTreeId(),
    notes: generateFileTreeId(),
  };

  // Generate dynamic folder names based on theme
  const charactersName = await generateThemeContent.folderName(theme, 'characters');
  const locationsName = await generateThemeContent.folderName(theme, 'locations'); 
  const chaptersName = await generateThemeContent.folderName(theme, 'chapters');
  const worldBuildingName = await generateThemeContent.folderName(theme, 'worldBuilding');
  const researchName = theme === 'mystery' 
    ? await generateThemeContent.folderName(theme, 'notes')
    : 'Research & Notes';

  const folderItems: FileTreeItem[] = [
    // Main folders
    {
      id: folders.characters,
      projectId,
      name: charactersName,
      type: 'folder',
      path: `/${charactersName.toLowerCase().replace(/\s+/g, '-')}`,
      tags: ['character-development'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.locations,
      projectId,
      name: locationsName,
      type: 'folder',
      path: `/${locationsName.toLowerCase().replace(/\s+/g, '-')}`,
      tags: ['world-building'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.chapters,
      projectId,
      name: chaptersName,
      type: 'folder',
      path: `/${chaptersName.toLowerCase().replace(/\s+/g, '-')}`,
      tags: ['main-story'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.worldBuilding,
      projectId,
      name: worldBuildingName,
      type: 'folder',
      path: `/${worldBuildingName.toLowerCase().replace(/\s+/g, '-')}`,
      tags: ['reference'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.research,
      projectId,
      name: researchName,
      type: 'folder',
      path: `/${researchName.toLowerCase().replace(/\s+/g, '-')}`,
      tags: ['reference', 'planning'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.timeline,
      projectId,
      name: 'Timeline',
      type: 'folder',
      path: '/timeline',
      tags: ['chronology', 'reference'],
      createdAt: now,
      updatedAt: now
    },
    
    // Character subfolders
    {
      id: folders.protagonists,
      projectId,
      name: theme === 'mystery' ? 'Investigators' : theme === 'scifi' ? 'Protagonists' : 'Main Characters',
      type: 'folder',
      path: `/${charactersName.toLowerCase().replace(/\s+/g, '-')}/protagonists`,
      parentId: folders.characters,
      tags: ['main-characters'],
      createdAt: now,
      updatedAt: now
    },
    {
      id: folders.supporting,
      projectId,
      name: theme === 'mystery' ? 'Witnesses & Suspects' : theme === 'scifi' ? 'Supporting Crew' : 'Supporting Cast',
      type: 'folder',
      path: `/${charactersName.toLowerCase().replace(/\s+/g, '-')}/supporting`,
      parentId: folders.characters,
      tags: ['supporting-cast'],
      createdAt: now,
      updatedAt: now
    },
    
    // Location subfolders  
    {
      id: folders.cities,
      projectId,
      name: theme === 'mystery' ? 'Key Locations' : theme === 'scifi' ? 'Colonies & Stations' : 'Cities & Towns',
      type: 'folder',
      path: `/${locationsName.toLowerCase().replace(/\s+/g, '-')}/primary`,
      parentId: folders.locations,
      tags: ['primary-locations'],
      createdAt: now,
      updatedAt: now
    },
    
    // World building subfolder
    {
      id: folders.system,
      projectId,
      name: theme === 'fantasy' ? 'Magic System' : theme === 'scifi' ? 'Technology' : theme === 'mystery' ? 'Investigation Methods' : 'Systems',
      type: 'folder',
      path: `/${worldBuildingName.toLowerCase().replace(/\s+/g, '-')}/systems`,
      parentId: folders.worldBuilding,
      tags: ['system', 'reference'],
      createdAt: now,
      updatedAt: now
    }
  ];

  await db.fileTree.bulkAdd(folderItems);
  return folders;
}

// Create varied documents with dynamic content
async function createVariedProjectDocuments(
  projectId: string,
  theme: keyof typeof themeGenerators,
  folders: any,
  userId: string | undefined,
  now: string
) {
  const documents: Document[] = [];
  const fileTreeItems: FileTreeItem[] = [];
  const helpers = await safeFaker.helpers();
  const number = await safeFaker.number();

  // Generate 2-4 character documents
  const numCharacters = await number.int({ min: 2, max: 4 });
  for (let i = 0; i < numCharacters; i++) {
    const { document, fileTree } = await generateCharacter(theme, projectId, 
      i === 0 ? folders.protagonists : folders.supporting);
    
    documents.push({ id: generateDocumentId(), ...document } as Document);
    fileTreeItems.push({ id: generateFileTreeId(), documentId: documents[documents.length - 1].id, ...fileTree } as FileTreeItem);
  }

  // Generate 1-3 location documents
  const numLocations = await number.int({ min: 1, max: 3 });
  for (let i = 0; i < numLocations; i++) {
    const { document, fileTree } = await generateLocation(theme, projectId, folders.cities);
    
    documents.push({ id: generateDocumentId(), ...document } as Document);
    fileTreeItems.push({ id: generateFileTreeId(), documentId: documents[documents.length - 1].id, ...fileTree } as FileTreeItem);
  }

  // Generate 3-6 chapter documents
  const numChapters = await number.int({ min: 3, max: 6 });
  for (let i = 1; i <= numChapters; i++) {
    const { document, fileTree } = await generateChapter(theme, projectId, i, folders.chapters);
    
    documents.push({ id: generateDocumentId(), ...document } as Document);
    fileTreeItems.push({ id: generateFileTreeId(), documentId: documents[documents.length - 1].id, ...fileTree } as FileTreeItem);
  }

  // Generate 1-2 world-building documents
  const numWorldBuilding = await number.int({ min: 1, max: 2 });
  for (let i = 0; i < numWorldBuilding; i++) {
    const { document, fileTree } = await generateWorldBuildingDocument(theme, projectId, folders.system);
    
    documents.push({ id: generateDocumentId(), ...document } as Document);
    fileTreeItems.push({ id: generateFileTreeId(), documentId: documents[documents.length - 1].id, ...fileTree } as FileTreeItem);
  }

  // Generate 1-2 research documents
  const numResearch = await number.int({ min: 1, max: 2 });
  for (let i = 0; i < numResearch; i++) {
    const { document, fileTree } = await generateResearchDocument(theme, projectId, folders.research);
    
    documents.push({ id: generateDocumentId(), ...document } as Document);
    fileTreeItems.push({ id: generateFileTreeId(), documentId: documents[documents.length - 1].id, ...fileTree } as FileTreeItem);
  }

  // Generate 1 timeline document
  const { document, fileTree } = await generateTimelineDocument(theme, projectId, folders.timeline);
  documents.push({ id: generateDocumentId(), ...document } as Document);
  fileTreeItems.push({ id: generateFileTreeId(), documentId: documents[documents.length - 1].id, ...fileTree } as FileTreeItem);

  // Add all documents and file tree items to database
  await db.documents.bulkAdd(documents);
  await db.fileTree.bulkAdd(fileTreeItems);

  return documents;
}

// Create dynamic theme-appropriate tags
async function createDynamicProjectTags(projectId: string, theme: keyof typeof themeGenerators, now: string) {
  // Generate theme-appropriate tags using the dynamic generator
  const generatedTags = await generateTags(theme, projectId);
  
  // Convert to proper Tag objects with IDs
  const tags: Tag[] = generatedTags.map(tag => ({
    id: generateTagId(),
    ...tag,
    createdAt: now,
    updatedAt: now
  })) as Tag[];

  await db.tags.bulkAdd(tags);
  return tags;
}

// Large demo with multiple varied projects
export async function seedLargeDemo(userId?: string): Promise<string> {
  const number = await safeFaker.number();
  
  // Create 2-4 projects with different themes
  const numProjects = await number.int({ min: 2, max: 4 });
  const projectIds: string[] = [];
  
  for (let i = 0; i < numProjects; i++) {
    const projectId = await seedSampleProject(userId);
    projectIds.push(projectId);
  }
  
  // Return the first project ID as the primary one
  return projectIds[0];
}