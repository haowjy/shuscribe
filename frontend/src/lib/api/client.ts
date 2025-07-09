// API client for ShuScribe backend communication

import { 
  ApiResponse, 
  Document, 
  ProjectData, 
  CreateDocumentRequest, 
  UpdateDocumentRequest 
} from '@/types/project';

// Re-export types for convenience
export type { 
  ApiResponse, 
  Document, 
  ProjectData, 
  CreateDocumentRequest, 
  UpdateDocumentRequest,
  FileItem
} from '@/types/project';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = '/api') {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.error || 'An error occurred',
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
  async getProjectData(projectId: string): Promise<ApiResponse<ProjectData>> {
    return this.request<ProjectData>(`/projects/${projectId}/data`);
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