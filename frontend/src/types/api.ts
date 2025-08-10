/**
 * API Types matching backend domain models
 * These types represent the complete API contract for server communication
 */

// === Base Types ===

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  status: number;
}

export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

// === Project Types ===

export interface Project extends BaseEntity {
  title: string;
  description: string;
  ownerId?: string;
  createdBy?: string;
  updatedBy?: string;
  collaborators: Collaborator[];
  wordCount: number;
  documentCount: number;
  settings: ProjectSettings;
  tags: string[];
}

export interface Collaborator {
  userId: string;
  role: 'owner' | 'editor' | 'viewer';
  permissions: string[];
}

export interface ProjectSettings {
  theme?: string;
  defaultTemplate?: string;
  autoSave?: boolean;
  [key: string]: any;
}

// === Document Types ===

export interface Document extends BaseEntity {
  projectId: string;
  title: string;
  path: string;
  content: ProseMirrorContent;
  wordCount: number;
  version: string;
  isLocked: boolean;
  lockedBy?: string;
  fileTreeId?: string;
  createdBy?: string;
  updatedBy?: string;
  tags: string[];
}

export interface ProseMirrorContent {
  type: string;
  content?: any[];
  attrs?: Record<string, any>;
  marks?: any[];
  text?: string;
}

// === File Tree Types ===

export interface FileTreeItem extends BaseEntity {
  projectId: string;
  name: string;
  type: 'file' | 'folder';
  path: string;
  parentId?: string;
  documentId?: string;
  wordCount?: number;
  icon?: string;
  tags: string[];
  // UI-specific fields (local only)
  collapsed?: boolean;
  children?: FileTreeItem[];
}

// === Tag Types ===

export interface Tag extends BaseEntity {
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
}

// === User Types ===

export interface User extends BaseEntity {
  email: string;
  name?: string;
  avatar?: string;
  isActive: boolean;
  lastSeenAt?: string;
}

// === Request/Response Types ===

export interface CreateProjectRequest {
  title: string;
  description?: string;
  settings?: ProjectSettings;
}

export interface UpdateProjectRequest {
  title?: string;
  description?: string;
  settings?: ProjectSettings;
}

export interface CreateDocumentRequest {
  title: string;
  path: string;
  content?: ProseMirrorContent;
  tags?: string[];
}

export interface UpdateDocumentRequest {
  title?: string;
  path?: string;
  content?: ProseMirrorContent;
  tags?: string[];
}

export interface CreateFileTreeItemRequest {
  name: string;
  type: 'file' | 'folder';
  path: string;
  parentId?: string;
  documentId?: string;
  icon?: string;
  tags?: string[];
}

export interface UpdateFileTreeItemRequest {
  name?: string;
  path?: string;
  parentId?: string;
  icon?: string;
  tags?: string[];
}

export interface CreateTagRequest {
  name: string;
  icon?: string;
  color?: string;
  description?: string;
  category?: string;
  projectId?: string;
}

export interface UpdateTagRequest {
  name?: string;
  icon?: string;
  color?: string;
  description?: string;
  category?: string;
  isArchived?: boolean;
}

// === LLM/AI Types ===

export interface LLMGenerateRequest {
  prompt: string;
  context?: Record<string, any>;
  model?: string;
  maxTokens?: number;
  temperature?: number;
}

export interface LLMGenerateResponse {
  content: string;
  model: string;
  tokensUsed: number;
  finishReason: string;
}

// === Authentication Types ===

export interface AuthUser {
  id: string;
  email: string;
  name?: string;
  avatar?: string;
  accessToken: string;
  refreshToken: string;
}

export interface AuthContext {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// === Error Types ===

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

// === Utility Types ===

export type EntityType = 'project' | 'document' | 'fileTreeItem' | 'tag' | 'user';

export interface SearchResult<T> {
  items: T[];
  total: number;
  query: string;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// === Field Mapping Types ===

export interface FieldMapping {
  camelCase: string;
  snake_case: string;
}

export const FIELD_MAPPINGS: FieldMapping[] = [
  { camelCase: 'projectId', snake_case: 'project_id' },
  { camelCase: 'documentId', snake_case: 'document_id' },
  { camelCase: 'parentId', snake_case: 'parent_id' },
  { camelCase: 'fileTreeId', snake_case: 'file_tree_id' },
  { camelCase: 'wordCount', snake_case: 'word_count' },
  { camelCase: 'documentCount', snake_case: 'document_count' },
  { camelCase: 'usageCount', snake_case: 'usage_count' },
  { camelCase: 'createdAt', snake_case: 'created_at' },
  { camelCase: 'updatedAt', snake_case: 'updated_at' },
  { camelCase: 'createdBy', snake_case: 'created_by' },
  { camelCase: 'updatedBy', snake_case: 'updated_by' },
  { camelCase: 'ownerId', snake_case: 'owner_id' },
  { camelCase: 'userId', snake_case: 'user_id' },
  { camelCase: 'isLocked', snake_case: 'is_locked' },
  { camelCase: 'lockedBy', snake_case: 'locked_by' },
  { camelCase: 'isGlobal', snake_case: 'is_global' },
  { camelCase: 'isSystem', snake_case: 'is_system' },
  { camelCase: 'isArchived', snake_case: 'is_archived' },
  { camelCase: 'isActive', snake_case: 'is_active' },
  { camelCase: 'lastSeenAt', snake_case: 'last_seen_at' },
];