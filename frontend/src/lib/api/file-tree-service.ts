/**
 * API-driven File Tree Service
 * Uses MSW API endpoints for file tree operations
 */

import { TreeItem, FileTreeResponse } from '@/types/api';
import { validateTreeItem, isFile, isFolder } from '@/data/file-tree';
import { fileTreeCache } from '@/lib/storage/cache-manager';

export interface FileTreeServiceOptions {
  enableCache?: boolean;
  enableApiCalls?: boolean;
  cacheTTL?: number; // Time to live in milliseconds
}

export interface LoadFileTreeResult {
  fileTree: TreeItem[];
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
   * Validate and clean file tree data from API
   */
  private validateFileTreeData(data: any[]): TreeItem[] {
    if (!Array.isArray(data)) {
      console.warn('File tree data is not an array:', data);
      return [];
    }

    const validItems: TreeItem[] = [];
    
    const validateRecursive = (items: any[]): TreeItem[] => {
      const result: TreeItem[] = [];
      
      for (const item of items) {
        if (validateTreeItem(item)) {
          // Recursively validate children for folders
          if (isFolder(item) && item.children) {
            const validatedItem = {
              ...item,
              children: validateRecursive(item.children)
            };
            result.push(validatedItem);
          } else {
            result.push(item);
          }
        } else {
          console.warn('Invalid file tree item:', item);
        }
      }
      
      return result;
    };

    return validateRecursive(data);
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
        
        // Extract file tree data - try both field names
        const rawFileTree = data.fileTree || data.file_tree || [];
        
        if (!Array.isArray(rawFileTree)) {
          console.warn(`API returned invalid fileTree structure for project ${projectId}:`, data);
          return {
            fileTree: [],
            source: 'fallback',
            fromCache: false,
            error: 'Invalid API response structure'
          };
        }
        
        // Validate and clean the file tree data
        const fileTree = this.validateFileTreeData(rawFileTree);
        
        if (fileTree.length !== rawFileTree.length) {
          console.warn(`Some file tree items were invalid and filtered out. Original: ${rawFileTree.length}, Valid: ${fileTree.length}`);
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
  getFileTreeFromCache(projectId: string): TreeItem[] | null {
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
   * Find item by ID in file tree
   */
  findItemById(fileTree: TreeItem[], itemId: string): TreeItem | null {
    for (const item of fileTree) {
      if (item.id === itemId) {
        return item;
      }
      
      if (isFolder(item) && item.children) {
        const found = this.findItemById(item.children, itemId);
        if (found) return found;
      }
    }
    
    return null;
  }

  /**
   * Get all files from file tree (flattened)
   */
  getAllFiles(fileTree: TreeItem[]): TreeItem[] {
    const files: TreeItem[] = [];
    
    const traverse = (items: TreeItem[]) => {
      for (const item of items) {
        if (isFile(item)) {
          files.push(item);
        }
        
        if (isFolder(item) && item.children) {
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
  getAllFolders(fileTree: TreeItem[]): TreeItem[] {
    const folders: TreeItem[] = [];
    
    const traverse = (items: TreeItem[]) => {
      for (const item of items) {
        if (isFolder(item)) {
          folders.push(item);
        }
        
        if (isFolder(item) && item.children) {
          traverse(item.children);
        }
      }
    };
    
    traverse(fileTree);
    return folders;
  }

  /**
   * Get item path from root
   */
  getItemPath(fileTree: TreeItem[], itemId: string): string | null {
    const findPath = (items: TreeItem[], targetId: string, currentPath = ''): string | null => {
      for (const item of items) {
        const path = currentPath ? `${currentPath}/${item.name}` : item.name;
        
        if (item.id === targetId) {
          return path;
        }
        
        if (isFolder(item) && item.children) {
          const found = findPath(item.children, targetId, path);
          if (found) return found;
        }
      }
      
      return null;
    };
    
    return findPath(fileTree, itemId);
  }

  /**
   * Get cached file tree with null check
   */
  private getCachedFileTree(cacheKey: string): TreeItem[] | null {
    if (!this.options.enableCache) return null;
    return fileTreeCache.get(cacheKey);
  }

  /**
   * Cache file tree with timestamp
   */
  private cacheFileTree(cacheKey: string, fileTree: TreeItem[]): void {
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
export const findItemById = (fileTree: TreeItem[], itemId: string) => fileTreeService.findItemById(fileTree, itemId);
export const getAllFiles = (fileTree: TreeItem[]) => fileTreeService.getAllFiles(fileTree);
export const getAllFolders = (fileTree: TreeItem[]) => fileTreeService.getAllFolders(fileTree);
export const getItemPath = (fileTree: TreeItem[], itemId: string) => fileTreeService.getItemPath(fileTree, itemId);