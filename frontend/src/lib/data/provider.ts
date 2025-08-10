import type { Project, Document, FileTreeItem, Tag } from '../localdb/types';

export interface DataProvider {
  // Projects
  getProjects(): Promise<Project[]>;
  getProject(id: string): Promise<Project | null>;
  createProject(project: Omit<Project, 'id' | 'createdAt' | 'updatedAt'>): Promise<Project>;
  updateProject(id: string, updates: Partial<Project>): Promise<Project>;
  deleteProject(id: string): Promise<void>;

  // Documents
  getDocuments(projectId: string): Promise<Document[]>;
  getDocument(id: string): Promise<Document | null>;
  createDocument(document: Omit<Document, 'id' | 'createdAt' | 'updatedAt'>): Promise<Document>;
  updateDocument(id: string, updates: Partial<Document>): Promise<Document>;
  deleteDocument(id: string): Promise<void>;

  // File Tree
  getFileTree(projectId: string): Promise<FileTreeItem[]>;
  createFileTreeItem(item: Omit<FileTreeItem, 'id' | 'createdAt' | 'updatedAt'>): Promise<FileTreeItem>;
  updateFileTreeItem(id: string, updates: Partial<FileTreeItem>): Promise<FileTreeItem>;
  deleteFileTreeItem(id: string): Promise<void>;

  // Tags
  getTags(projectId: string): Promise<Tag[]>;
  createTag(tag: Omit<Tag, 'id' | 'createdAt' | 'updatedAt'>): Promise<Tag>;
  updateTag(id: string, updates: Partial<Tag>): Promise<Tag>;
  deleteTag(id: string): Promise<void>;

  // Bootstrap
  isEmpty(): Promise<boolean>;
  clear(): Promise<void>;
}