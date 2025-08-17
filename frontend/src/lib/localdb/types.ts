/**
 * Local Cache Layer - Performance-Optimized Domain Types
 * 
 * WHY: This file solves the critical UX problem of writers waiting for network requests.
 * Content creators need instant feedback when editing - any latency breaks their flow state.
 * This local cache layer provides zero-latency UI updates while background sync handles
 * persistence.
 * 
 * Problem Context: Traditional web apps wait for server responses before updating UI,
 * creating jarring delays for creative work. This layer enables "offline-first" patterns
 * where the UI responds instantly to user actions, then syncs in the background.
 * 
 * Optimization Benefits:
 * - Instant UI responses from local cache (no network latency)
 * - Offline-first: App works without internet connection
 * - Optimistic updates: UI updates immediately, sync happens in background
 * - Field mappings handle automatic conversion to/from backend formats
 * 
 * Usage Patterns:
 * - Use these types for component props and local state
 * - Default value constants enable easy object creation
 * - Helper functions provide business logic for domain operations
 * 
 * Data Flow:
 * User Action → Update Local Cache → Update UI (instant) → Background API Sync
 * 
 * Integration Points:
 * - Mirrors API types with camelCase convention and UI-specific fields
 * - Used by components in workspace/, editor/, and UI layers
 * - Synced with backend via automatic field mapping utilities
 * 
 * @see frontend/src/types/api.ts - Backend interface layer for server communication
 * @see frontend/src/lib/data/local-provider.ts - Cache management implementation
 */

// API Tag format (from backend)
export interface ApiTag {
  id: string;
  name: string;
  icon?: string | null;
  color?: string | null;
}

// API Collaborator format (from backend) 
export interface ApiCollaborator {
  user_id: string;
  role: string;
  name: string;
  avatar?: string | null;
}

// Domain model matching backend exactly
export interface Project {
  id: string;
  title: string;
  description: string;
  ownerId?: string;
  createdBy?: string;
  updatedBy?: string;
  collaborators: Collaborator[];
  wordCount: number;
  documentCount: number;
  settings: Record<string, any>;
  tags: string[];
  createdAt?: string;
  updatedAt?: string;
}

// API Project format (from backend /v1/projects)
export interface ApiProject {
  id: string;
  title: string;
  description: string;
  word_count: number;
  document_count: number;
  created_at: string;
  updated_at: string;
  tags: ApiTag[];
  collaborators: ApiCollaborator[];
}

export interface Collaborator {
  userId: string;
  role: string;
  permissions: string[];
}

// Domain model matching backend exactly  
export interface Document {
  id: string;
  projectId: string;
  title: string;
  path: string;
  content: Record<string, any>; // ProseMirror JSON as generic object
  wordCount: number;
  version: string;
  isLocked: boolean;
  lockedBy?: string;
  fileTreeId?: string;
  createdBy?: string;
  updatedBy?: string;
  tags: string[];
  createdAt?: string;
  updatedAt?: string;
}

// Domain model matching backend exactly
export interface FileTreeItem {
  id: string;
  projectId: string;
  name: string;
  type: 'file' | 'folder';
  path: string;
  parentId?: string;
  documentId?: string;
  wordCount?: number;
  icon?: string;
  tags: string[];
  createdAt?: string;
  updatedAt?: string;
  // UI-specific field (frontend only - not persisted to backend)
  collapsed?: boolean;
}

// Domain model matching backend exactly
export interface Tag {
  id: string;
  name: string;
  icon?: string;
  color?: string;
  description?: string;
  category?: string;
  projectId?: string;
  isGlobal: boolean;
  userId?: string;
  isSystem: boolean;
  isArchived: boolean;
  usageCount: number;
  createdAt?: string;
  updatedAt?: string;
}

// Backend domain model for User
export interface User {
  id: string;
  email: string;
  name?: string;
  avatar?: string;
  isActive: boolean;
  lastSeenAt?: string;
  createdAt?: string;
  updatedAt?: string;
}

// Frontend-specific types (not in backend)
export interface ReferenceIndex {
  id: string;
  projectId: string;
  data: any; // Serialized index for fast cold start
  version: number;
  updatedAt: string;
}

export interface Meta {
  key: string;
  value: any;
}

// Default values to ensure required backend fields are populated
export const DEFAULT_PROJECT_VALUES: Partial<Project> = {
  description: '',
  collaborators: [],
  wordCount: 0,
  documentCount: 0,
  settings: {},
  tags: [],
};

// Helper function to check if user owns or can access a project
export function canUserAccessProject(project: Project, userId?: string): boolean {
  if (!userId) return false;
  
  // User is the owner
  if (project.ownerId === userId) return true;
  
  // User is a collaborator
  if (project.collaborators.some(collab => collab.userId === userId)) return true;
  
  return false;
}

export const DEFAULT_DOCUMENT_VALUES: Partial<Document> = {
  version: '1.0.0',
  isLocked: false,
  tags: [],
  wordCount: 0,
};

export const DEFAULT_FILE_TREE_VALUES: Partial<FileTreeItem> = {
  tags: [],
};

export const DEFAULT_TAG_VALUES: Partial<Tag> = {
  isGlobal: false,
  isSystem: false,
  isArchived: false,
  usageCount: 0,
};