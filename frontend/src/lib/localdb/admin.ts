import { db } from './db';
import type { Project, Document, FileTreeItem, Tag, ReferenceIndex, Meta } from './types';

export interface ExportData {
  projects: Project[];
  documents: Document[];
  fileTree: FileTreeItem[];
  tags: Tag[];
  referenceIndex: ReferenceIndex[];
  meta: Meta[];
  exportedAt: string;
  version: number;
}

/**
 * Clear all local data from IndexedDB
 */
export async function clearAllLocalData(): Promise<void> {
  await db.transaction('rw', [db.projects, db.documents, db.fileTree, db.tags, db.referenceIndex, db.meta], async () => {
    await db.projects.clear();
    await db.documents.clear();
    await db.fileTree.clear();
    await db.tags.clear();
    await db.referenceIndex.clear();
    await db.meta.clear();
  });
}

/**
 * Export all data to JSON format
 */
export async function exportAllData(): Promise<void> {
  const [projects, documents, fileTree, tags, referenceIndex, meta] = await Promise.all([
    db.projects.toArray(),
    db.documents.toArray(),
    db.fileTree.toArray(),
    db.tags.toArray(),
    db.referenceIndex.toArray(),
    db.meta.toArray(),
  ]);

  const exportData: ExportData = {
    projects,
    documents,
    fileTree,
    tags,
    referenceIndex,
    meta,
    exportedAt: new Date().toISOString(),
    version: 1,
  };

  // Create and download JSON file
  const dataStr = JSON.stringify(exportData, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = `shuscribe-export-${new Date().toISOString().split('T')[0]}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  URL.revokeObjectURL(url);
}

/**
 * Import data from JSON file
 */
export async function importAllData(file: File): Promise<void> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = async (e) => {
      try {
        const jsonStr = e.target?.result as string;
        const importData: ExportData = JSON.parse(jsonStr);
        
        // Validate import data structure
        if (!importData.projects || !importData.documents || !importData.fileTree || !importData.tags) {
          throw new Error('Invalid import file format');
        }
        
        // Clear existing data and import new data
        await db.transaction('rw', [db.projects, db.documents, db.fileTree, db.tags, db.referenceIndex, db.meta], async () => {
          // Clear all tables
          await db.projects.clear();
          await db.documents.clear();
          await db.fileTree.clear();
          await db.tags.clear();
          await db.referenceIndex.clear();
          await db.meta.clear();
          
          // Import new data
          if (importData.projects.length > 0) {
            await db.projects.bulkAdd(importData.projects);
          }
          if (importData.documents.length > 0) {
            await db.documents.bulkAdd(importData.documents);
          }
          if (importData.fileTree.length > 0) {
            await db.fileTree.bulkAdd(importData.fileTree);
          }
          if (importData.tags.length > 0) {
            await db.tags.bulkAdd(importData.tags);
          }
          if (importData.referenceIndex && importData.referenceIndex.length > 0) {
            await db.referenceIndex.bulkAdd(importData.referenceIndex);
          }
          if (importData.meta && importData.meta.length > 0) {
            await db.meta.bulkAdd(importData.meta);
          }
        });
        
        resolve();
      } catch (error) {
        reject(new Error(`Failed to import data: ${error instanceof Error ? error.message : String(error)}`));
      }
    };
    
    reader.onerror = () => {
      reject(new Error('Failed to read import file'));
    };
    
    reader.readAsText(file);
  });
}

/**
 * Get storage statistics
 */
export async function getStorageStats(): Promise<{
  projects: number;
  documents: number;
  fileTree: number;
  tags: number;
  referenceIndex: number;
  meta: number;
}> {
  const [projects, documents, fileTree, tags, referenceIndex, meta] = await Promise.all([
    db.projects.count(),
    db.documents.count(),
    db.fileTree.count(),
    db.tags.count(),
    db.referenceIndex.count(),
    db.meta.count(),
  ]);

  return {
    projects,
    documents,
    fileTree,
    tags,
    referenceIndex,
    meta,
  };
}