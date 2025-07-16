import { TreeItem } from '@/types/api';
import { isFile, isFolder } from '@/data/file-tree';

export interface ReferenceItem {
  id: string;
  label: string;
  type: 'file' | 'folder';
  path: string;
  icon?: string;
  tags?: string[];
}

/**
 * Transform TreeItem tree into flat list of referenceable items
 */
export function transformFileTreeToReferences(
  fileTree: TreeItem[],
  parentPath: string = ''
): ReferenceItem[] {
  const references: ReferenceItem[] = [];

  for (const item of fileTree) {
    const currentPath = parentPath ? `${parentPath}/${item.name}` : item.name;
    
    // Add current item to references
    references.push({
      id: item.id,
      label: item.name.replace(/\.md$/, ''), // Remove .md extension for display
      type: item.type,
      path: currentPath,
      tags: item.tags?.map(tag => tag.name),
      icon: item.icon,
    });

    // Recursively process children (only folders can have children)
    if (isFolder(item) && item.children) {
      references.push(...transformFileTreeToReferences(item.children, currentPath));
    }
  }

  return references;
}

/**
 * Filter references based on query string
 */
export function filterReferences(
  references: ReferenceItem[],
  query: string
): ReferenceItem[] {
  if (!query.trim()) {
    return references;
  }

  const lowerQuery = query.toLowerCase();
  
  return references.filter(ref => {
    // Match against label (filename without extension)
    const labelMatch = ref.label.toLowerCase().includes(lowerQuery);
    
    // Match against tags
    const tagMatch = ref.tags?.some(tag => 
      tag.toLowerCase().includes(lowerQuery)
    );
    
    // Match against path
    const pathMatch = ref.path.toLowerCase().includes(lowerQuery);
    
    return labelMatch || tagMatch || pathMatch;
  });
}

/**
 * Sort references by relevance to query
 */
export function sortReferencesByRelevance(
  references: ReferenceItem[],
  query: string
): ReferenceItem[] {
  if (!query.trim()) {
    return references;
  }

  const lowerQuery = query.toLowerCase();
  
  return references.sort((a, b) => {
    // Exact matches first
    if (a.label.toLowerCase() === lowerQuery) return -1;
    if (b.label.toLowerCase() === lowerQuery) return 1;
    
    // Starts with query
    const aStartsWith = a.label.toLowerCase().startsWith(lowerQuery);
    const bStartsWith = b.label.toLowerCase().startsWith(lowerQuery);
    
    if (aStartsWith && !bStartsWith) return -1;
    if (!aStartsWith && bStartsWith) return 1;
    
    // Files before folders
    if (a.type === 'file' && b.type === 'folder') return -1;
    if (a.type === 'folder' && b.type === 'file') return 1;
    
    // Alphabetical order
    return a.label.localeCompare(b.label);
  });
}

/**
 * Get reference item by ID
 */
export function getReferenceById(
  references: ReferenceItem[],
  id: string
): ReferenceItem | undefined {
  return references.find(ref => ref.id === id);
}

/**
 * Get reference item by label
 */
export function getReferenceByLabel(
  references: ReferenceItem[],
  label: string
): ReferenceItem | undefined {
  return references.find(ref => ref.label.toLowerCase() === label.toLowerCase());
}