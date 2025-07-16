/**
 * Smart Document Loading Service
 * localStorage-first strategy with API fallback and conflict resolution
 */

import { Document, UpdateDocumentRequest } from '@/types/project';
import { EditorDocument } from '@/lib/editor/editor-types';
import { documentCache } from '@/lib/storage/cache-manager';
import { apiClient } from './client';
import { createDebug } from '@/lib/utils/logger';

export interface DocumentServiceOptions {
  enableCache?: boolean;
  enableApiCalls?: boolean;
  cacheKey?: string;
}

export interface LoadDocumentResult {
  document: Document;
  source: 'cache' | 'api' | 'fallback';
  fromCache: boolean;
  error?: string;
}

export interface SaveDocumentResult {
  success: boolean;
  document?: Document;
  error?: string;
  hadConflict?: boolean;
}

export interface ConflictResolution {
  useLocal: boolean;
  useRemote: boolean;
  merged?: Document;
}

/**
 * Smart document service with localStorage-first loading
 */
const debug = createDebug('app:api:document');

export class DocumentService {
  private options: Required<DocumentServiceOptions>;

  constructor(options: DocumentServiceOptions = {}) {
    this.options = {
      enableCache: true,
      enableApiCalls: true,
      cacheKey: 'documents',
      ...options
    };
  }

  /**
   * Load document with localStorage-first strategy
   * 1. Check cache first
   * 2. Fall back to API if not in cache
   * 3. Cache API result for future use
   */
  async loadDocument(documentId: string): Promise<LoadDocumentResult> {
    const startTime = performance.now();
    
    // Step 1: Try cache first
    if (this.options.enableCache) {
      const cacheStartTime = performance.now();
      const cachedDocument = documentCache.get(documentId);
      const cacheTime = performance.now() - cacheStartTime;
      
      if (cachedDocument) {
        const totalTime = performance.now() - startTime;
        debug(`Document ${documentId} loaded from cache in ${cacheTime.toFixed(1)}ms (total: ${totalTime.toFixed(1)}ms)`);
        return {
          document: cachedDocument,
          source: 'cache',
          fromCache: true
        };
      } else {
        debug(`Document ${documentId} cache miss (${cacheTime.toFixed(1)}ms)`);
      }
    }

    // Step 2: Try API if cache miss
    if (this.options.enableApiCalls) {
      try {
        const apiStartTime = performance.now();
        const response = await apiClient.getDocument(documentId);
        const apiTime = performance.now() - apiStartTime;
        
        if (response.error) {
          const totalTime = performance.now() - startTime;
          debug(`Document ${documentId} API error in ${apiTime.toFixed(1)}ms (total: ${totalTime.toFixed(1)}ms):`, response.error);
          return {
            document: this.createFallbackDocument(documentId),
            source: 'fallback',
            fromCache: false,
            error: response.error
          };
        }

        const document = response.data!;
        
        // Step 3: Cache the API result
        if (this.options.enableCache) {
          const cacheSetStartTime = performance.now();
          documentCache.set(documentId, document);
          const cacheSetTime = performance.now() - cacheSetStartTime;
          const totalTime = performance.now() - startTime;
          debug(`Document ${documentId} loaded from API in ${apiTime.toFixed(1)}ms, cached in ${cacheSetTime.toFixed(1)}ms (total: ${totalTime.toFixed(1)}ms)`);
        } else {
          const totalTime = performance.now() - startTime;
          debug(`Document ${documentId} loaded from API in ${apiTime.toFixed(1)}ms (total: ${totalTime.toFixed(1)}ms)`);
        }

        return {
          document: document as unknown as Document,
          source: 'api',
          fromCache: false
        };
      } catch (error) {
        const totalTime = performance.now() - startTime;
        console.warn(`📄 Document ${documentId} API error after ${totalTime.toFixed(1)}ms:`, error);
        return {
          document: this.createFallbackDocument(documentId),
          source: 'fallback',
          fromCache: false,
          error: error instanceof Error ? error.message : 'API error'
        };
      }
    }

    // Step 3: Fallback document
    return {
      document: this.createFallbackDocument(documentId),
      source: 'fallback',
      fromCache: false,
      error: 'No cache or API available'
    };
  }

  /**
   * Save document with conflict detection and resolution
   */
  async saveDocument(
    documentId: string, 
    content: EditorDocument, 
    title?: string,
    forceLocal = false
  ): Promise<SaveDocumentResult> {
    const startTime = performance.now();
    
    const document: Document = {
      id: documentId,
      title: title || `Document ${documentId}`,
      content,
      path: title?.toLowerCase().replace(/\s+/g, '-') || documentId,
      projectId: '1', // TODO: Get from context
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      tags: [],
      wordCount: this.calculateWordCount(content)
    };

    // Always save to cache first (fast and reliable)
    if (this.options.enableCache) {
      const cacheStartTime = performance.now();
      documentCache.set(documentId, document);
      const cacheTime = performance.now() - cacheStartTime;
      debug(`Document ${documentId} saved to cache in ${cacheTime.toFixed(1)}ms`);
    }

    // If only local save requested, stop here
    if (forceLocal || !this.options.enableApiCalls) {
      const totalTime = performance.now() - startTime;
      debug(`Document ${documentId} local-only save completed in ${totalTime.toFixed(1)}ms`);
      return {
        success: true,
        document
      };
    }

    // Try to save to API
    try {
      // TODO: Implement conflict detection
      // const existingDoc = await this.loadDocumentFromApi(documentId);
      // const conflict = this.detectConflict(document, existingDoc);
      // if (conflict) {
      //   const resolution = await this.resolveConflict(document, existingDoc);
      //   // Handle conflict resolution...
      // }

      const updates: UpdateDocumentRequest = {
        title: document.title,
        content: document.content,
        tags: document.tags
      };

      const apiStartTime = performance.now();
      const response = await apiClient.updateDocument(documentId, updates as any);
      const apiTime = performance.now() - apiStartTime;
      
      if (response.error) {
        const totalTime = performance.now() - startTime;
        console.warn(`💾 Document ${documentId} API save failed in ${apiTime.toFixed(1)}ms (total: ${totalTime.toFixed(1)}ms):`, response.error);
        return {
          success: true, // Cache save succeeded
          document,
          error: response.error
        };
      }

      const savedDocument = response.data!;
      
      // Update cache with API response
      if (this.options.enableCache) {
        const cacheUpdateStartTime = performance.now();
        documentCache.set(documentId, savedDocument);
        const cacheUpdateTime = performance.now() - cacheUpdateStartTime;
        const totalTime = performance.now() - startTime;
        debug(`Document ${documentId} saved to API in ${apiTime.toFixed(1)}ms, cache updated in ${cacheUpdateTime.toFixed(1)}ms (total: ${totalTime.toFixed(1)}ms)`);
      } else {
        const totalTime = performance.now() - startTime;
        debug(`Document ${documentId} saved to API in ${apiTime.toFixed(1)}ms (total: ${totalTime.toFixed(1)}ms)`);
      }

      return {
        success: true,
        document: savedDocument as unknown as Document
      };

    } catch (error) {
      const totalTime = performance.now() - startTime;
      console.warn(`💾 Document ${documentId} API save error after ${totalTime.toFixed(1)}ms:`, error);
      return {
        success: true, // Cache save succeeded
        document,
        error: error instanceof Error ? error.message : 'API save failed'
      };
    }
  }

  /**
   * Check if document exists in cache
   */
  hasDocumentInCache(documentId: string): boolean {
    return this.options.enableCache && documentCache.has(documentId);
  }

  /**
   * Get document from cache only (no API fallback)
   */
  getDocumentFromCache(documentId: string): Document | null {
    if (!this.options.enableCache) return null;
    return documentCache.get(documentId);
  }

  /**
   * Remove document from cache
   */
  removeDocumentFromCache(documentId: string): boolean {
    if (!this.options.enableCache) return false;
    return documentCache.remove(documentId);
  }

  /**
   * Get cache metrics for debugging
   */
  getCacheMetrics() {
    return documentCache.getMetrics();
  }

  /**
   * Clear all cached documents
   */
  clearCache(): void {
    documentCache.clear();
  }

  /**
   * Bulk load multiple documents
   */
  async loadMultipleDocuments(documentIds: string[]): Promise<Map<string, LoadDocumentResult>> {
    const results = new Map<string, LoadDocumentResult>();
    
    // Load all documents in parallel
    const promises = documentIds.map(async (id) => {
      const result = await this.loadDocument(id);
      results.set(id, result);
    });
    
    await Promise.all(promises);
    return results;
  }

  /**
   * Get all cached document IDs
   */
  getCachedDocumentIds(): string[] {
    if (!this.options.enableCache) return [];
    return documentCache.getAllKeys();
  }

  /**
   * Preload documents into cache
   */
  async preloadDocuments(documentIds: string[]): Promise<void> {
    debug(`Preloading ${documentIds.length} documents into cache`);
    
    const promises = documentIds.map(async (id) => {
      if (!this.hasDocumentInCache(id)) {
        await this.loadDocument(id);
      }
    });
    
    await Promise.all(promises);
  }

  /**
   * Create a fallback document when API/cache fails
   */
  private createFallbackDocument(documentId: string): Document {
    return {
      id: documentId,
      title: `Document ${documentId}`,
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
      path: documentId,
      projectId: '1',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      tags: [],
      wordCount: 0,
      isTemp: true
    };
  }

  /**
   * Calculate word count from editor content
   */
  private calculateWordCount(content: EditorDocument): number {
    // Simple word count - traverse content and count words
    const text = this.extractTextFromContent(content);
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
  }

  /**
   * Extract plain text from editor content
   */
  private extractTextFromContent(content: EditorDocument): string {
    if (!content || !content.content) return '';
    
    const extractText = (node: any): string => {
      if (node.type === 'text') {
        return node.text || '';
      }
      
      if (node.content) {
        return node.content.map(extractText).join('');
      }
      
      return '';
    };
    
    return content.content.map(extractText).join(' ');
  }

  /**
   * TODO: Detect conflicts between local and remote versions
   */
  private detectConflict(localDoc: Document, remoteDoc: Document): boolean {
    // TODO: Implement conflict detection logic
    // - Compare lastModified timestamps
    // - Check for overlapping changes
    // - Return true if conflict detected
    return false;
  }

  /**
   * TODO: Resolve conflicts between documents
   */
  private async resolveConflict(
    localDoc: Document, 
    remoteDoc: Document
  ): Promise<ConflictResolution> {
    // TODO: Implement conflict resolution strategy
    // - Show user a diff/merge interface
    // - Allow choosing local vs remote
    // - Support three-way merge
    // For now, prefer local changes
    return {
      useLocal: true,
      useRemote: false,
      merged: localDoc
    };
  }
}

/**
 * Singleton document service instance
 */
export const documentService = new DocumentService({
  enableCache: true,
  enableApiCalls: true
});

/**
 * Log cache performance metrics to console
 */
export const logCacheMetrics = () => {
  const metrics = documentService.getCacheMetrics();
  console.group('📊 Document Cache Metrics');
  console.log(`Cache Hit Rate: ${(metrics.hitRate * 100).toFixed(1)}%`);
  console.log(`Total Accesses: ${metrics.totalAccesses}`);
  console.log(`Cache Hits: ${metrics.hits}`);
  console.log(`Cache Misses: ${metrics.misses}`);
  console.log(`Total Cache Size: ${(metrics.totalSize / 1024).toFixed(1)} KB`);
  console.log(`Cached Documents: ${metrics.entryCount}`);
  console.groupEnd();
};

/**
 * Convenience functions for common operations
 */
export const loadDocument = (documentId: string) => documentService.loadDocument(documentId);
export const saveDocument = (documentId: string, content: EditorDocument, title?: string) => 
  documentService.saveDocument(documentId, content, title);
export const hasDocumentInCache = (documentId: string) => documentService.hasDocumentInCache(documentId);
export const clearDocumentCache = () => documentService.clearCache();