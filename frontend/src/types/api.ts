/**
 * TypeScript interfaces for ShuScribe API contracts
 * These interfaces define the structure of API requests and responses
 * for frontend-first development with MSW mocking.
 */

// ============================================================================
// Base Types
// ============================================================================

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
  status: number;
}

export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, string>;
  request_id?: string;
}

export interface PaginationMeta {
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
  next_offset?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMeta;
}

// ============================================================================
// Authentication & User Types
// ============================================================================

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  created_at: string;
}

export interface AuthLoginRequest {
  email: string;
  password: string;
}

export interface AuthLoginResponse {
  user: User;
  token: string;
  expires_at: string;
}

export interface AuthMeResponse {
  user: User;
}

// ============================================================================
// Project Types
// ============================================================================

export interface ProjectCollaborator {
  user_id: string;
  role: 'owner' | 'editor' | 'viewer';
  name: string;
  avatar?: string | null;
}

export interface ProjectSettings {
  auto_save_interval: number;
  word_count_target: number;
  backup_enabled: boolean;
}

export interface ProjectSummary {
  id: string;
  title: string;
  description: string;
  word_count: number;
  document_count: number;
  created_at: string;
  updated_at: string;
  tags: Tag[];
  collaborators: ProjectCollaborator[];
}

export interface ProjectDetails extends ProjectSummary {
  settings: ProjectSettings;
}

export interface CreateProjectRequest {
  title: string;
  description: string;
  tags?: string[];
  settings?: Partial<ProjectSettings>;
}

export interface UpdateProjectRequest {
  title?: string;
  description?: string;
  tags?: string[];
  settings?: Partial<ProjectSettings>;
}

export interface ProjectListResponse extends PaginatedResponse<ProjectSummary> {}

// ============================================================================
// File Tree Types
// ============================================================================

// Import enhanced file tree types
import type { TreeItem, FileItem, FolderItem, Tag } from '@/data/file-tree';
export type { TreeItem, FileItem, FolderItem, Tag };

// API response structure for file tree
export interface FileTreeResponse {
  fileTree: TreeItem[];  // Backend uses alias "fileTree" for file_tree field
  file_tree?: TreeItem[]; // Keep compatibility with snake_case
  metadata: {
    total_files: number;
    total_folders: number;
    last_updated: string;
  };
}

// File tree item creation requests
export interface CreateFolderRequest {
  name: string;
  parent_id?: string;
  path: string;
  type: 'folder';
  icon?: string;
  tags?: string[];
}

export interface CreateFileRequest {
  name: string;
  parent_id?: string;
  path: string;
  type: 'file';
  document_id: string; // Files must have a document
  icon?: string;
  tags?: string[];
}

export interface UpdateFileTreeItemRequest {
  name?: string;
  parent_id?: string;
  path?: string;
  icon?: string;
  tags?: string[];
  // Note: type and document_id changes require validation
}

export interface MoveItemRequest {
  new_parent_id?: string;
  new_name?: string;
  new_path: string;
}

// ============================================================================
// Document Types
// ============================================================================

export interface DocumentContent {
  type: 'doc';
  content: any[]; // ProseMirror JSON structure
}

export interface DocumentMeta {
  id: string;
  project_id: string;
  title: string;
  path: string;
  tags: string[];
  word_count: number;
  created_at: string;
  updated_at: string;
  version: string;
  is_locked: boolean;
  locked_by?: string;
  file_tree_id?: string;
}

export interface Document extends DocumentMeta {
  content: DocumentContent;
}

export interface CreateDocumentRequest {
  project_id: string;
  title: string;
  path: string;
  content: DocumentContent;
  tags?: string[];
  file_tree_parent_id?: string;
}

export interface UpdateDocumentRequest {
  title?: string;
  content?: DocumentContent;
  tags?: string[];
  version?: string;
}

export interface BulkDocumentsRequest {
  operation: 'get_multiple' | 'update_multiple' | 'delete_multiple';
  document_ids: string[];
  include_content?: boolean;
  updates?: Record<string, UpdateDocumentRequest>;
}

export interface BulkDocumentsResponse {
  documents: Document[] | DocumentMeta[];
  not_found: string[];
  access_denied: string[];
}

// ============================================================================
// Reference System Types
// ============================================================================

export interface DocumentReference {
  target_document_id: string;
  target_title: string;
  reference_text: string;
  count: number;
}

export interface IncomingReference {
  source_document_id: string;
  source_title: string;
  reference_text: string;
  count: number;
}

export interface DocumentReferencesResponse {
  outgoing_references: DocumentReference[];
  incoming_references: IncomingReference[];
}

export interface ReferenceSearchResult {
  id: string;
  title: string;
  type: 'file' | 'folder';
  path: string;
  icon?: string;
  tags?: string[];
  match_score: number;
}

export interface ReferenceSearchRequest {
  q: string;
  type?: 'file' | 'folder' | 'both';
  limit?: number;
  project_id: string;
}

export interface ReferenceSearchResponse {
  results: ReferenceSearchResult[];
  total: number;
}

// ============================================================================
// Query Parameters
// ============================================================================

export interface ProjectListParams {
  limit?: number;
  offset?: number;
  sort?: 'title' | 'created_at' | 'updated_at';
  order?: 'asc' | 'desc';
}

export interface DocumentGetParams {
  include_content?: boolean;
  version?: string;
}

export interface ReferenceSearchParams {
  q: string;
  type?: 'file' | 'folder' | 'both';
  limit?: number;
}

// ============================================================================
// WebSocket Types (Future)
// ============================================================================

export interface WebSocketMessage {
  type: 'document_updated' | 'document_locked' | 'document_unlocked' | 
        'user_joined' | 'user_left' | 'cursor_position';
  payload: any;
  timestamp: string;
  user_id?: string;
}

export interface DocumentLockEvent {
  document_id: string;
  locked_by: string;
  locked_at: string;
}

export interface CursorPositionEvent {
  document_id: string;
  user_id: string;
  position: {
    from: number;
    to: number;
  };
}

// ============================================================================
// Error Types
// ============================================================================

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ApiErrorResponse {
  error: string;
  message: string;
  details?: Record<string, string> | ValidationError[];
  request_id?: string;
}

// Common error codes
export type ApiErrorCode = 
  | 'invalid_credentials'
  | 'project_not_found'
  | 'document_not_found'
  | 'version_conflict'
  | 'access_denied'
  | 'validation_error'
  | 'rate_limit_exceeded'
  | 'internal_error';

// ============================================================================
// HTTP Headers
// ============================================================================

export interface RateLimitHeaders {
  'X-RateLimit-Limit': string;
  'X-RateLimit-Remaining': string;
  'X-RateLimit-Reset': string;
}

export interface ApiVersionHeaders {
  'Accept': string; // e.g., "application/json; version=1"
}

// ============================================================================
// API Client Types
// ============================================================================

export interface ApiClientConfig {
  baseUrl: string;
  timeout: number;
  retries: number;
  authToken?: string;
}

export interface RequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  data?: any;
  params?: Record<string, any>;
  headers?: Record<string, string>;
}

// ============================================================================
// Utility Types
// ============================================================================

export type Timestamp = string; // ISO 8601 format
export type UUID = string;
export type ProjectId = string;
export type DocumentId = string;
export type UserId = string;
export type FileTreeId = string;

// For frontend state management
export interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  lastFetch?: Timestamp;
}

// For optimistic updates
export interface OptimisticUpdate<T> {
  id: string;
  type: 'create' | 'update' | 'delete';
  data: T;
  timestamp: Timestamp;
  reverted?: boolean;
}

// ============================================================================
// Type Guards
// ============================================================================

export function isApiError(response: any): response is ApiErrorResponse {
  return response && typeof response.error === 'string';
}

export function isValidDocument(data: any): data is Document {
  return data && 
         typeof data.id === 'string' &&
         typeof data.project_id === 'string' &&
         typeof data.title === 'string' &&
         data.content &&
         typeof data.content.type === 'string' &&
         Array.isArray(data.content.content);
}

export function isValidProject(data: any): data is ProjectDetails {
  return data &&
         typeof data.id === 'string' &&
         typeof data.title === 'string' &&
         typeof data.description === 'string' &&
         Array.isArray(data.tags) &&
         Array.isArray(data.collaborators);
}

// ============================================================================
// Constants
// ============================================================================

export const API_ENDPOINTS = {
  // Auth
  AUTH_LOGIN: '/api/auth/login',
  AUTH_LOGOUT: '/api/auth/logout',
  AUTH_ME: '/api/auth/me',
  
  // Projects
  PROJECTS: '/api/projects',
  PROJECT_DETAILS: (id: string) => `/api/projects/${id}`,
  PROJECT_FILE_TREE: (id: string) => `/api/projects/${id}/file-tree`,
  PROJECT_REFERENCES_SEARCH: (id: string) => `/api/projects/${id}/references/search`,
  
  // Documents
  DOCUMENTS: '/api/documents',
  DOCUMENT_DETAILS: (id: string) => `/api/documents/${id}`,
  DOCUMENT_META: (id: string) => `/api/documents/${id}/meta`,
  DOCUMENT_REFERENCES: (id: string) => `/api/documents/${id}/references`,
  DOCUMENTS_BULK: '/api/documents/bulk',
  
  // File Tree
  CREATE_FOLDER: (projectId: string) => `/api/projects/${projectId}/file-tree/folders`,
  MOVE_ITEM: (projectId: string, itemId: string) => `/api/projects/${projectId}/file-tree/${itemId}/move`,
} as const;

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
} as const;

export const DEFAULT_PAGINATION = {
  limit: 20,
  offset: 0,
} as const;