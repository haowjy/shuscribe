import { ProjectData, Document } from '@/types/project';
import { mockFileTree, FileItem } from '@/data/file-tree';
import { createEmptyDocument } from '@/lib/editor/content-utils';

/**
 * Generate mock documents from file tree
 */
function generateDocumentsFromFileTree(fileTree: FileItem[], projectId: string = "1"): Document[] {
  const documents: Document[] = [];

  function processFileItem(item: FileItem, parentPath: string = '') {
    const currentPath = parentPath ? `${parentPath}/${item.name}` : item.name;
    
    if (item.type === 'file') {
      // Create a document for this file
      documents.push({
        id: item.id,
        title: item.name.replace(/\.md$/, ''), // Remove .md extension
        content: createEmptyDocument(),
        path: currentPath,
        projectId: projectId,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        tags: item.tags || [],
        wordCount: 0,
      });
    }
    
    // Process children recursively
    if (item.children) {
      item.children.forEach(child => processFileItem(child, currentPath));
    }
  }

  fileTree.forEach(item => processFileItem(item));
  return documents;
}

/**
 * Mock project data that matches the file tree structure
 */
export function getMockProjectData(projectId: string = "1"): ProjectData {
  const documents = generateDocumentsFromFileTree(mockFileTree, projectId);
  
  return {
    id: projectId,
    title: "The Chronicles of Elara",
    description: "A fantasy epic about a young mage discovering her powers in a world where magic is forbidden.",
    documents: documents,
    fileTree: mockFileTree,
    tags: ["fantasy", "magic", "adventure", "coming-of-age"],
    createdAt: "2024-01-15T10:30:00Z",
    updatedAt: new Date().toISOString(),
  };
}

/**
 * Get document by ID from mock data
 */
export function getMockDocument(documentId: string, projectId: string = "1"): Document | undefined {
  const projectData = getMockProjectData(projectId);
  return projectData.documents.find(doc => doc.id === documentId);
}