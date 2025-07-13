/**
 * API-driven File Tree Service
 * Uses MSW API endpoints for file tree operations
 */

import { FileTreeItem, FileTreeResponse } from '@/types/api';
import { fileTreeCache } from '@/lib/storage/cache-manager';

export interface FileTreeServiceOptions {
  enableCache?: boolean;
  enableApiCalls?: boolean;
  cacheTTL?: number; // Time to live in milliseconds
}

export interface LoadFileTreeResult {
  fileTree: FileTreeItem[];
  source: 'cache' | 'api' | 'fallback';
  fromCache: boolean;
  error?: string;
}

/**
 * Service for loading and managing file tree data
 */
export class FileTreeService {
  private options: Required<FileTreeServiceOptions>;

  constructor(options: FileTreeServiceOptions = {}) {
    this.options = {
      enableCache: true,
      enableApiCalls: true,
      cacheTTL: 5 * 60 * 1000, // 5 minutes default TTL
      ...options
    };
  }

  /**
   * Load file tree with caching strategy
   * 1. Check cache first (with TTL validation)
   * 2. Fall back to API if cache miss or expired
   * 3. Use fallback mock data if API fails
   */
  async loadFileTree(projectId: string): Promise<LoadFileTreeResult> {
    const cacheKey = `project_${projectId}_tree`;

    // Step 1: Try cache first
    if (this.options.enableCache) {
      const cached = this.getCachedFileTree(cacheKey);
      if (cached && this.isCacheValid(cacheKey)) {
        console.log(`File tree for project ${projectId} loaded from cache`);
        return {
          fileTree: cached,
          source: 'cache',
          fromCache: true
        };
      }
    }

    // Step 2: Try API if cache miss or expired
    if (this.options.enableApiCalls) {
      try {
        // Use real backend API endpoint
        const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
        const response = await fetch(`${apiBaseUrl}/projects/${projectId}/file-tree`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.getAuthToken()}`,
          },
        });

        if (!response.ok) {
          throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }

        const data: FileTreeResponse = await response.json();
        // Validate API response structure and provide fallback
        // Backend uses alias "fileTree" for the field
        const fileTree = Array.isArray(data.fileTree) ? data.fileTree : [];
        
        if (!Array.isArray(data.fileTree)) {
          console.warn(`API returned invalid fileTree structure for project ${projectId}:`, data);
        }
        
        // Cache the result
        if (this.options.enableCache) {
          this.cacheFileTree(cacheKey, fileTree);
          console.log(`File tree for project ${projectId} loaded from API and cached`);
        }

        return {
          fileTree,
          source: 'api',
          fromCache: false
        };
      } catch (error) {
        console.warn(`API error loading file tree for project ${projectId}:`, error);
        // Return empty array as fallback instead of mock data
        return {
          fileTree: [],
          source: 'fallback',
          fromCache: false,
          error: error instanceof Error ? error.message : 'API error'
        };
      }
    }

    // Step 3: Fallback
    return {
      fileTree: [],
      source: 'fallback',
      fromCache: false,
      error: 'No cache or API available'
    };
  }

  /**
   * Refresh file tree (force API call)
   */
  async refreshFileTree(projectId: string): Promise<LoadFileTreeResult> {
    const cacheKey = `project_${projectId}_tree`;
    
    // Clear cache first
    if (this.options.enableCache) {
      fileTreeCache.remove(cacheKey);
      fileTreeCache.remove(`${cacheKey}_timestamp`);
    }
    
    // Load fresh data
    return this.loadFileTree(projectId);
  }

  /**
   * Check if file tree is cached
   */
  hasFileTreeInCache(projectId: string): boolean {
    const cacheKey = `project_${projectId}_tree`;
    return this.options.enableCache && 
           fileTreeCache.has(cacheKey) && 
           this.isCacheValid(cacheKey);
  }

  /**
   * Get file tree from cache only
   */
  getFileTreeFromCache(projectId: string): FileTreeItem[] | null {
    const cacheKey = `project_${projectId}_tree`;
    return this.getCachedFileTree(cacheKey);
  }

  /**
   * Clear file tree cache
   */
  clearCache(): void {
    fileTreeCache.clear();
  }

  /**
   * Get cache metrics
   */
  getCacheMetrics() {
    return fileTreeCache.getMetrics();
  }

  /**
   * Get authentication token from localStorage
   */
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

  /**
   * Find file by ID in file tree
   */
  findFileById(fileTree: FileTreeItem[], fileId: string): FileTreeItem | null {
    for (const item of fileTree) {
      if (item.id === fileId) {
        return item;
      }
      
      if (item.children) {
        const found = this.findFileById(item.children, fileId);
        if (found) return found;
      }
    }
    
    return null;
  }

  /**
   * Get all files from file tree (flattened)
   */
  getAllFiles(fileTree: FileTreeItem[]): FileTreeItem[] {
    const files: FileTreeItem[] = [];
    
    const traverse = (items: FileTreeItem[]) => {
      for (const item of items) {
        if (item.type === 'file') {
          files.push(item);
        }
        
        if (item.children) {
          traverse(item.children);
        }
      }
    };
    
    traverse(fileTree);
    return files;
  }

  /**
   * Get all folders from file tree (flattened)
   */
  getAllFolders(fileTree: FileTreeItem[]): FileTreeItem[] {
    const folders: FileTreeItem[] = [];
    
    const traverse = (items: FileTreeItem[]) => {
      for (const item of items) {
        if (item.type === 'folder') {
          folders.push(item);
        }
        
        if (item.children) {
          traverse(item.children);
        }
      }
    };
    
    traverse(fileTree);
    return folders;
  }

  /**
   * Get file path from root
   */
  getFilePath(fileTree: FileTreeItem[], fileId: string): string | null {
    const findPath = (items: FileTreeItem[], targetId: string, currentPath = ''): string | null => {
      for (const item of items) {
        const path = currentPath ? `${currentPath}/${item.name}` : item.name;
        
        if (item.id === targetId) {
          return path;
        }
        
        if (item.children) {
          const found = findPath(item.children, targetId, path);
          if (found) return found;
        }
      }
      
      return null;
    };
    
    return findPath(fileTree, fileId);
  }

  /**
   * Get cached file tree with null check
   */
  private getCachedFileTree(cacheKey: string): FileTreeItem[] | null {
    if (!this.options.enableCache) return null;
    return fileTreeCache.get(cacheKey);
  }

  /**
   * Cache file tree with timestamp
   */
  private cacheFileTree(cacheKey: string, fileTree: FileTreeItem[]): void {
    if (!this.options.enableCache) return;
    
    fileTreeCache.set(cacheKey, fileTree);
    fileTreeCache.set(`${cacheKey}_timestamp`, Date.now());
  }

  /**
   * Check if cached file tree is still valid
   */
  private isCacheValid(cacheKey: string): boolean {
    if (!this.options.enableCache) return false;
    
    const timestamp = fileTreeCache.get(`${cacheKey}_timestamp`);
    if (!timestamp) return false;
    
    return (Date.now() - timestamp) < this.options.cacheTTL;
  }

  /**
   * Simulate API delay for development
   */
  private async simulateApiDelay(): Promise<void> {
    // Simulate 200-500ms API delay
    const delay = 200 + Math.random() * 300;
    await new Promise(resolve => setTimeout(resolve, delay));
  }
}

/**
 * Singleton file tree service instance
 */
export const fileTreeService = new FileTreeService({
  enableCache: true,
  enableApiCalls: true,
  cacheTTL: 5 * 60 * 1000 // 5 minutes
});

/**
 * Convenience functions
 */
export const loadFileTree = (projectId: string) => fileTreeService.loadFileTree(projectId);
export const refreshFileTree = (projectId: string) => fileTreeService.refreshFileTree(projectId);
export const findFileById = (fileTree: FileTreeItem[], fileId: string) => fileTreeService.findFileById(fileTree, fileId);
export const getAllFiles = (fileTree: FileTreeItem[]) => fileTreeService.getAllFiles(fileTree);
export const getFilePath = (fileTree: FileTreeItem[], fileId: string) => fileTreeService.getFilePath(fileTree, fileId);