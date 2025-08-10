import { db } from '../localdb/db';
import type { Project, Document, FileTreeItem, Tag } from '../localdb/types';
import { DEFAULT_PROJECT_VALUES, DEFAULT_DOCUMENT_VALUES, DEFAULT_FILE_TREE_VALUES, DEFAULT_TAG_VALUES, canUserAccessProject } from '../localdb/types';
import { generateProjectId, generateDocumentId, generateFileTreeId, generateTagId } from '../utils/id';
import type { DataProvider } from './provider';

export class LocalDataProvider implements DataProvider {
  private userId?: string;

  constructor(userId?: string) {
    this.userId = userId;
  }

  setUserId(userId?: string) {
    this.userId = userId;
  }

  // Projects
  async getProjects(): Promise<Project[]> {
    const allProjects = await db.projects.orderBy('updatedAt').reverse().toArray();
    
    // If no user, return all projects (for backwards compatibility)
    if (!this.userId) {
      return allProjects;
    }

    // Filter projects user can access
    return allProjects.filter(project => canUserAccessProject(project, this.userId));
  }

  async getProject(id: string): Promise<Project | null> {
    const project = await db.projects.get(id);
    
    // If no project found, return null
    if (!project) return null;
    
    // If no user or user can access the project, return it
    if (!this.userId || canUserAccessProject(project, this.userId)) {
      return project;
    }
    
    // User doesn't have access
    return null;
  }

  async createProject(project: Omit<Project, 'id' | 'createdAt' | 'updatedAt'>): Promise<Project> {
    const now = new Date().toISOString();
    const newProject: Project = {
      id: generateProjectId(),
      ...DEFAULT_PROJECT_VALUES,
      ...project,
      ownerId: this.userId, // Set current user as owner
      createdBy: this.userId,
      createdAt: now,
      updatedAt: now,
    };

    await db.projects.add(newProject);
    return newProject;
  }

  async updateProject(id: string, updates: Partial<Project>): Promise<Project> {
    const updatedProject = {
      ...updates,
      updatedBy: this.userId,
      updatedAt: new Date().toISOString(),
    };

    await db.projects.update(id, updatedProject);
    const project = await db.projects.get(id);
    if (!project) {
      throw new Error(`Project ${id} not found`);
    }
    
    // Check if user has access to the updated project
    if (this.userId && !canUserAccessProject(project, this.userId)) {
      throw new Error('Access denied to project');
    }
    
    return project;
  }

  async deleteProject(id: string): Promise<void> {
    await db.transaction('rw', [db.projects, db.documents, db.fileTree, db.tags, db.referenceIndex], async () => {
      await db.projects.delete(id);
      await db.documents.where('projectId').equals(id).delete();
      await db.fileTree.where('projectId').equals(id).delete();
      await db.tags.where('projectId').equals(id).delete();
      await db.referenceIndex.where('projectId').equals(id).delete();
    });
  }

  // Documents
  async getDocuments(projectId: string): Promise<Document[]> {
    return await db.documents.where('projectId').equals(projectId).toArray();
  }

  async getDocument(id: string): Promise<Document | null> {
    return (await db.documents.get(id)) || null;
  }

  async createDocument(document: Omit<Document, 'id' | 'createdAt' | 'updatedAt'>): Promise<Document> {
    const now = new Date().toISOString();
    const newDocument: Document = {
      id: generateDocumentId(),
      ...DEFAULT_DOCUMENT_VALUES,
      ...document,
      createdAt: now,
      updatedAt: now,
    };

    await db.documents.add(newDocument);
    return newDocument;
  }

  async updateDocument(id: string, updates: Partial<Document>): Promise<Document> {
    const updatedDocument = {
      ...updates,
      updatedAt: new Date().toISOString(),
    };

    await db.documents.update(id, updatedDocument);
    const document = await db.documents.get(id);
    if (!document) {
      throw new Error(`Document ${id} not found`);
    }
    return document;
  }

  async deleteDocument(id: string): Promise<void> {
    await db.transaction('rw', [db.documents, db.fileTree], async () => {
      await db.documents.delete(id);
      // Delete associated file tree item
      await db.fileTree.where('documentId').equals(id).delete();
    });
  }

  // File Tree
  async getFileTree(projectId: string): Promise<FileTreeItem[]> {
    return await db.fileTree.where('projectId').equals(projectId).toArray();
  }

  async createFileTreeItem(item: Omit<FileTreeItem, 'id' | 'createdAt' | 'updatedAt'>): Promise<FileTreeItem> {
    const now = new Date().toISOString();
    const newItem: FileTreeItem = {
      id: generateFileTreeId(),
      ...DEFAULT_FILE_TREE_VALUES,
      ...item,
      createdAt: now,
      updatedAt: now,
    };

    await db.fileTree.add(newItem);
    return newItem;
  }

  async updateFileTreeItem(id: string, updates: Partial<FileTreeItem>): Promise<FileTreeItem> {
    await db.fileTree.update(id, updates);
    const item = await db.fileTree.get(id);
    if (!item) {
      throw new Error(`FileTreeItem ${id} not found`);
    }
    return item;
  }

  async deleteFileTreeItem(id: string): Promise<void> {
    await db.fileTree.delete(id);
  }

  // Tags
  async getTags(projectId: string): Promise<Tag[]> {
    return await db.tags.where('projectId').equals(projectId).toArray();
  }

  async createTag(tag: Omit<Tag, 'id' | 'createdAt' | 'updatedAt'>): Promise<Tag> {
    const now = new Date().toISOString();
    const newTag: Tag = {
      id: generateTagId(),
      ...DEFAULT_TAG_VALUES,
      ...tag,
      createdAt: now,
      updatedAt: now,
    };

    await db.tags.add(newTag);
    return newTag;
  }

  async updateTag(id: string, updates: Partial<Tag>): Promise<Tag> {
    await db.tags.update(id, updates);
    const tag = await db.tags.get(id);
    if (!tag) {
      throw new Error(`Tag ${id} not found`);
    }
    return tag;
  }

  async deleteTag(id: string): Promise<void> {
    await db.tags.delete(id);
  }

  // Bootstrap
  async isEmpty(): Promise<boolean> {
    const projectCount = await db.projects.count();
    return projectCount === 0;
  }

  async clear(): Promise<void> {
    await db.transaction('rw', [db.projects, db.documents, db.fileTree, db.tags, db.referenceIndex, db.meta], async () => {
      await db.projects.clear();
      await db.documents.clear();
      await db.fileTree.clear();
      await db.tags.clear();
      await db.referenceIndex.clear();
      await db.meta.clear();
    });
  }
}

// Factory function to create provider with user context
export function createLocalDataProvider(userId?: string): LocalDataProvider {
  return new LocalDataProvider(userId);
}

// Default instance for backwards compatibility
export const localDataProvider = new LocalDataProvider();