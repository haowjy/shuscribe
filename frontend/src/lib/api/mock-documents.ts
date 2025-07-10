/**
 * Mock Document API
 * 
 * This file simulates backend API calls for document operations.
 * All functions include realistic delays and responses to simulate
 * network behavior and prepare the frontend for real API integration.
 * 
 * TODO: Replace all mock functions with real backend API calls
 */

import { EditorDocument } from '@/lib/editor/editor-types';

// Simulate network delays
const MOCK_DELAY = {
  SAVE: 300,      // Save operations
  LOAD: 200,      // Load operations  
  DELETE: 250,    // Delete operations
  CREATE: 200,    // Create operations
} as const;

// Mock API response types
export interface DocumentSaveResponse {
  success: boolean;
  id: string;
  saved_at: string;
  error?: string;
}

export interface DocumentLoadResponse {
  success: boolean;
  document?: {
    id: string;
    title: string;
    content: EditorDocument;
    created_at: string;
    updated_at: string;
    word_count: number;
  };
  error?: string;
}

export interface DocumentCreateResponse {
  success: boolean;
  document?: {
    id: string;
    title: string;
    content: EditorDocument;
    created_at: string;
  };
  error?: string;
}

export interface DocumentDeleteResponse {
  success: boolean;
  id: string;
  deleted_at?: string;
  error?: string;
}

/**
 * Mock Documents API
 * 
 * Simulates document CRUD operations with realistic responses.
 * Each function includes TODO comments for backend implementation.
 */
export const documentsApi = {
  /**
   * Save a document
   * TODO: Replace with real backend API call to POST/PUT /api/documents/{id}
   */
  async saveDocument(id: string, content: EditorDocument, title?: string): Promise<DocumentSaveResponse> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, MOCK_DELAY.SAVE));
    
    // TODO: Implement real API call
    console.log('TODO: Implement real API - Mock save successful for document:', id);
    
    // Simulate occasional failures (5% chance)
    if (Math.random() < 0.05) {
      return {
        success: false,
        id,
        saved_at: '',
        error: 'Network error - please try again'
      };
    }
    
    return {
      success: true,
      id,
      saved_at: new Date().toISOString(),
    };
  },

  /**
   * Load a document
   * TODO: Replace with real backend API call to GET /api/documents/{id}
   */
  async loadDocument(id: string): Promise<DocumentLoadResponse> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, MOCK_DELAY.LOAD));
    
    // TODO: Implement real API call
    console.log('TODO: Implement real API - Mock load for document:', id);
    
    // Simulate document not found (10% chance)
    if (Math.random() < 0.1) {
      return {
        success: false,
        error: 'Document not found'
      };
    }
    
    // Return mock document data
    return {
      success: true,
      document: {
        id,
        title: `Document ${id}`,
        content: { 
          type: 'doc', 
          content: [
            { 
              type: 'paragraph', 
              content: [{ type: 'text', text: 'This is mock content loaded from the API.' }] 
            }
          ] 
        },
        created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
        updated_at: new Date().toISOString(),
        word_count: 42
      }
    };
  },

  /**
   * Create a new document
   * TODO: Replace with real backend API call to POST /api/documents
   */
  async createDocument(title: string, content?: EditorDocument): Promise<DocumentCreateResponse> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, MOCK_DELAY.CREATE));
    
    // TODO: Implement real API call
    console.log('TODO: Implement real API - Mock create for document:', title);
    
    const now = new Date().toISOString();
    const newId = `doc_${Date.now()}`;
    
    return {
      success: true,
      document: {
        id: newId,
        title,
        content: content || { type: 'doc', content: [{ type: 'paragraph' }] },
        created_at: now,
      }
    };
  },

  /**
   * Delete a document
   * TODO: Replace with real backend API call to DELETE /api/documents/{id}
   */
  async deleteDocument(id: string): Promise<DocumentDeleteResponse> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, MOCK_DELAY.DELETE));
    
    // TODO: Implement real API call
    console.log('TODO: Implement real API - Mock delete for document:', id);
    
    return {
      success: true,
      id,
      deleted_at: new Date().toISOString(),
    };
  },

  /**
   * Get document metadata (without content)
   * TODO: Replace with real backend API call to GET /api/documents/{id}/meta
   */
  async getDocumentMeta(id: string): Promise<{ success: boolean; meta?: any; error?: string }> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // TODO: Implement real API call
    console.log('TODO: Implement real API - Mock meta for document:', id);
    
    return {
      success: true,
      meta: {
        id,
        title: `Document ${id}`,
        word_count: 42,
        updated_at: new Date().toISOString(),
      }
    };
  }
};

/**
 * API Error Types
 * These will be used when implementing real API error handling
 */
export type ApiError = 
  | 'NETWORK_ERROR'
  | 'NOT_FOUND' 
  | 'UNAUTHORIZED'
  | 'VALIDATION_ERROR'
  | 'SERVER_ERROR';

/**
 * TODO: Add these when implementing real API
 * - Authentication headers
 * - Request/response interceptors
 * - Retry logic for failed requests
 * - Proper error handling and user feedback
 * - Request cancellation for component unmounting
 * - Optimistic updates with rollback on error
 */