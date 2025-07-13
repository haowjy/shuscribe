// API client for ShuScribe backend communication

import { 
  Document,
  CreateDocumentRequest, 
  UpdateDocumentRequest,
  FileTreeResponse,
  ProjectDetails,
  ProjectListResponse,
  ProjectListParams,
  ApiErrorResponse
} from '@/types/api';

// Legacy API response type for backward compatibility
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    // Use environment variable for API base URL, fallback to localhost:8000
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
  }

  private getAuthToken(): string {
    if (typeof window === 'undefined') return '';
    
    try {
      const auth = localStorage.getItem('shuscribe_auth');
      if (auth) {
        const authData = JSON.parse(auth);
        return authData.token || '';
      }
    } catch {
      // Ignore parsing errors
    }
    
    return '';
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      const authToken = this.getAuthToken();
      
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...(authToken && { 'Authorization': `Bearer ${authToken}` }),
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();

      if (!response.ok) {
        const errorData = data as ApiErrorResponse;
        return {
          error: errorData.message || errorData.error || 'An error occurred',
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  // Project endpoints
  async listProjects(params: ProjectListParams = {}): Promise<ApiResponse<ProjectListResponse>> {
    const searchParams = new URLSearchParams();
    
    if (params.limit) searchParams.set('limit', params.limit.toString());
    if (params.offset) searchParams.set('offset', params.offset.toString());
    if (params.sort) searchParams.set('sort', params.sort);
    if (params.order) searchParams.set('order', params.order);
    
    const queryString = searchParams.toString();
    const endpoint = queryString ? `/projects?${queryString}` : '/projects';
    
    return this.request<ProjectListResponse>(endpoint);
  }

  async getProjectData(projectId: string): Promise<ApiResponse<ProjectDetails>> {
    return this.request<ProjectDetails>(`/projects/${projectId}`);
  }
  
  async getProjectFileTree(projectId: string): Promise<ApiResponse<FileTreeResponse>> {
    return this.request<FileTreeResponse>(`/projects/${projectId}/file-tree`);
  }

  // Document endpoints
  async getDocument(documentId: string): Promise<ApiResponse<Document>> {
    return this.request<Document>(`/documents/${documentId}`);
  }

  async createDocument(document: CreateDocumentRequest): Promise<ApiResponse<Document>> {
    return this.request<Document>('/documents', {
      method: 'POST',
      body: JSON.stringify(document),
    });
  }

  async updateDocument(
    documentId: string,
    updates: UpdateDocumentRequest
  ): Promise<ApiResponse<Document>> {
    return this.request<Document>(`/documents/${documentId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteDocument(documentId: string): Promise<ApiResponse<{ success: boolean }>> {
    return this.request<{ success: boolean }>(`/documents/${documentId}`, {
      method: 'DELETE',
    });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient;