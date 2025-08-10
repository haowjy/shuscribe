import { db } from './db';
import { generateReferenceIndexId } from '../utils/id';

export interface ReferenceIndexEntry {
  type: 'file' | 'folder' | 'tag';
  id: string;
  path?: string;
  name: string;
  tags?: string[];
  description?: string;
  documentCount?: number; // For tags
}

export interface ReferenceIndexData {
  entries: ReferenceIndexEntry[];
  lastUpdated: string;
}

/**
 * Build a reference index for a specific project
 */
export async function buildReferenceIndex(projectId: string): Promise<ReferenceIndexEntry[]> {
  const [documents, fileTree, tags] = await Promise.all([
    db.documents.where('projectId').equals(projectId).toArray(),
    db.fileTree.where('projectId').equals(projectId).toArray(),
    db.tags.where('projectId').equals(projectId).toArray()
  ]);

  const index: ReferenceIndexEntry[] = [];

  // Add file references
  documents.forEach(doc => {
    index.push({
      type: 'file',
      id: doc.id,
      path: doc.path,
      name: doc.title,
      tags: doc.tags,
      description: extractFirstLine(doc.content)
    });
  });

  // Add folder references
  fileTree
    .filter(item => item.type === 'folder')
    .forEach(folder => {
      index.push({
        type: 'folder',
        id: folder.id,
        path: folder.path,
        name: folder.name
      });
    });

  // Add tag references
  tags.forEach(tag => {
    const docCount = documents.filter(doc => doc.tags.includes(tag.name)).length;
    index.push({
      type: 'tag',
      id: tag.id,
      name: tag.name,
      documentCount: docCount,
      description: `${docCount} document${docCount !== 1 ? 's' : ''} tagged with ${tag.name}`
    });
  });

  return index;
}

/**
 * Extract first line from ProseMirror content for description
 */
function extractFirstLine(content: any): string {
  try {
    const firstParagraph = content?.content?.[0];
    if (firstParagraph?.content?.[0]?.text) {
      return firstParagraph.content[0].text.slice(0, 100);
    }
  } catch (error) {
    // Ignore parsing errors
  }
  return '';
}

/**
 * Search the reference index
 */
export function searchReferenceIndex(index: ReferenceIndexEntry[], query: string): ReferenceIndexEntry[] {
  const lowercaseQuery = query.toLowerCase();
  
  return index
    .filter(entry => 
      entry.name.toLowerCase().includes(lowercaseQuery) ||
      entry.path?.toLowerCase().includes(lowercaseQuery) ||
      entry.description?.toLowerCase().includes(lowercaseQuery) ||
      entry.tags?.some(tag => tag.toLowerCase().includes(lowercaseQuery))
    )
    .sort((a, b) => {
      // Exact name matches first
      if (a.name.toLowerCase() === lowercaseQuery) return -1;
      if (b.name.toLowerCase() === lowercaseQuery) return 1;
      
      // Name starts with query
      if (a.name.toLowerCase().startsWith(lowercaseQuery)) return -1;
      if (b.name.toLowerCase().startsWith(lowercaseQuery)) return 1;
      
      // Path starts with query (for nested references)
      if (a.path?.toLowerCase().startsWith(lowercaseQuery)) return -1;
      if (b.path?.toLowerCase().startsWith(lowercaseQuery)) return 1;
      
      // Alphabetical by name
      return a.name.localeCompare(b.name);
    });
}

/**
 * Save reference index to database
 */
export async function saveReferenceIndex(projectId: string, index: ReferenceIndexEntry[]): Promise<void> {
  const now = new Date().toISOString();
  const indexData: ReferenceIndexData = {
    entries: index,
    lastUpdated: now
  };

  await db.referenceIndex.put({
    id: generateReferenceIndexId(),
    projectId,
    data: indexData,
    version: 1,
    updatedAt: now
  });
}

/**
 * Load reference index from database
 */
export async function loadReferenceIndex(projectId: string): Promise<ReferenceIndexEntry[]> {
  const indexRecord = await db.referenceIndex.where('projectId').equals(projectId).first();
  
  if (indexRecord && indexRecord.data) {
    return indexRecord.data.entries || [];
  }
  
  // If no index exists, build it
  const index = await buildReferenceIndex(projectId);
  await saveReferenceIndex(projectId, index);
  return index;
}

/**
 * Update reference index for a project (rebuild and save)
 */
export async function updateReferenceIndex(projectId: string): Promise<ReferenceIndexEntry[]> {
  const index = await buildReferenceIndex(projectId);
  await saveReferenceIndex(projectId, index);
  return index;
}

/**
 * Get autocomplete suggestions for @-references
 */
export function getAutocompleteSuggestions(
  index: ReferenceIndexEntry[], 
  query: string, 
  limit: number = 10
): ReferenceIndexEntry[] {
  if (!query || query.length < 1) {
    return index.slice(0, limit);
  }
  
  return searchReferenceIndex(index, query).slice(0, limit);
}