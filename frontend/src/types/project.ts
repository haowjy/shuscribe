// Shared types for project and file system

import { EditorDocument } from "@/lib/editor/editor-types";

export interface FileItem {
  id: string;
  name: string;
  type: "file" | "folder";
  children?: FileItem[];
  tags?: string[];
  icon?: string; // Icon name for the file/folder
  documentId?: string; // For API integration
  path?: string; // File path
}

export interface Document {
  id: string;
  projectId: string;
  title: string;
  path: string;
  content: EditorDocument; // ProseMirror JSON
  tags: string[];
  wordCount: number;
  createdAt: string;
  updatedAt: string;
  isTemp?: boolean;
}

export interface ProjectData {
  id: string;
  title: string;
  description: string;
  documents: Document[];
  fileTree: FileItem[]; // Use consistent FileItem type
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export interface CreateDocumentRequest {
  projectId: string;
  title: string;
  path: string;
  content?: object;
  tags?: string[];
  isTemp?: boolean;
}

export interface UpdateDocumentRequest {
  title?: string;
  content?: object;
  tags?: string[];
}