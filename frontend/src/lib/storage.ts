/**
 * localStorage utilities for ShuScribe
 * Provides type-safe storage with versioning, error handling, and size management
 */

export interface StorageItem<T> {
  data: T;
  version: string;
  timestamp: number;
  projectId?: string;
}

export class StorageService {
  private static instance: StorageService;
  private readonly VERSION = "v1";
  private readonly MAX_SIZE_MB = 5;
  private readonly STORAGE_PREFIX = "shuscribe";

  static getInstance(): StorageService {
    if (!StorageService.instance) {
      StorageService.instance = new StorageService();
    }
    return StorageService.instance;
  }

  private constructor() {}

  /**
   * Generate a scoped storage key
   */
  private getKey(projectId: string | null, dataType: string): string {
    const parts = [this.STORAGE_PREFIX];
    if (projectId) parts.push(projectId);
    parts.push(dataType);
    return parts.join("-");
  }

  /**
   * Set data in localStorage with metadata
   */
  set<T>(
    dataType: string,
    data: T,
    projectId: string | null = null
  ): boolean {
    try {
      const item: StorageItem<T> = {
        data,
        version: this.VERSION,
        timestamp: Date.now(),
        projectId: projectId || undefined,
      };

      const key = this.getKey(projectId, dataType);
      const serialized = JSON.stringify(item);

      // Check size before setting
      if (!this.checkStorageSize(serialized)) {
        console.warn("localStorage size limit exceeded");
        return false;
      }

      localStorage.setItem(key, serialized);
      return true;
    } catch (error) {
      console.error("Failed to save to localStorage:", error);
      return false;
    }
  }

  /**
   * Get data from localStorage with type safety
   */
  get<T>(
    dataType: string,
    projectId: string | null = null
  ): T | null {
    try {
      const key = this.getKey(projectId, dataType);
      const stored = localStorage.getItem(key);

      if (!stored) return null;

      const item: StorageItem<T> = JSON.parse(stored);

      // Check version compatibility
      if (item.version !== this.VERSION) {
        console.warn(`Version mismatch for ${key}, clearing`);
        this.remove(dataType, projectId);
        return null;
      }

      return item.data;
    } catch (error) {
      console.error("Failed to read from localStorage:", error);
      return null;
    }
  }

  /**
   * Remove specific item from localStorage
   */
  remove(dataType: string, projectId: string | null = null): void {
    try {
      const key = this.getKey(projectId, dataType);
      localStorage.removeItem(key);
    } catch (error) {
      console.error("Failed to remove from localStorage:", error);
    }
  }

  /**
   * Clear all project-specific data
   */
  clearProject(projectId: string): void {
    try {
      const prefix = `${this.STORAGE_PREFIX}-${projectId}-`;
      const keysToRemove: string[] = [];

      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(prefix)) {
          keysToRemove.push(key);
        }
      }

      keysToRemove.forEach(key => localStorage.removeItem(key));
    } catch (error) {
      console.error("Failed to clear project data:", error);
    }
  }

  /**
   * Clear all ShuScribe data
   */
  clearAll(): void {
    try {
      const keysToRemove: string[] = [];

      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(this.STORAGE_PREFIX)) {
          keysToRemove.push(key);
        }
      }

      keysToRemove.forEach(key => localStorage.removeItem(key));
    } catch (error) {
      console.error("Failed to clear all data:", error);
    }
  }

  /**
   * Get storage usage statistics
   */
  getStorageStats(): { usedMB: number; maxMB: number; percentage: number } {
    try {
      let totalSize = 0;
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(this.STORAGE_PREFIX)) {
          const value = localStorage.getItem(key);
          if (value) {
            totalSize += new Blob([value]).size;
          }
        }
      }

      const usedMB = totalSize / (1024 * 1024);
      const percentage = (usedMB / this.MAX_SIZE_MB) * 100;

      return {
        usedMB: Math.round(usedMB * 100) / 100,
        maxMB: this.MAX_SIZE_MB,
        percentage: Math.round(percentage),
      };
    } catch (error) {
      console.error("Failed to calculate storage stats:", error);
      return { usedMB: 0, maxMB: this.MAX_SIZE_MB, percentage: 0 };
    }
  }

  /**
   * Check if adding data would exceed size limit
   */
  private checkStorageSize(newData: string): boolean {
    try {
      const stats = this.getStorageStats();
      const newDataSizeMB = new Blob([newData]).size / (1024 * 1024);
      
      return stats.usedMB + newDataSizeMB <= this.MAX_SIZE_MB;
    } catch {
      return true; // Allow if we can't check
    }
  }

  /**
   * Check if data is stale (older than maxAge in minutes)
   */
  isStale(
    dataType: string,
    maxAgeMinutes: number,
    projectId: string | null = null
  ): boolean {
    try {
      const key = this.getKey(projectId, dataType);
      const stored = localStorage.getItem(key);

      if (!stored) return true;

      const item: StorageItem<unknown> = JSON.parse(stored);
      const ageMinutes = (Date.now() - item.timestamp) / (1000 * 60);
      
      return ageMinutes > maxAgeMinutes;
    } catch {
      return true; // Consider stale if we can't check
    }
  }

  /**
   * Clean up old data (older than maxAge in days)
   */
  cleanup(maxAgeDays: number = 7): void {
    try {
      const maxAgeMs = maxAgeDays * 24 * 60 * 60 * 1000;
      const keysToRemove: string[] = [];

      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (!key || !key.startsWith(this.STORAGE_PREFIX)) continue;

        const stored = localStorage.getItem(key);
        if (!stored) continue;

        try {
          const item: StorageItem<unknown> = JSON.parse(stored);
          const age = Date.now() - item.timestamp;
          
          if (age > maxAgeMs) {
            keysToRemove.push(key);
          }
        } catch {
          // Remove corrupted data
          keysToRemove.push(key);
        }
      }

      keysToRemove.forEach(key => localStorage.removeItem(key));
      
      if (keysToRemove.length > 0) {
        console.log(`Cleaned up ${keysToRemove.length} old localStorage items`);
      }
    } catch (error) {
      console.error("Failed to cleanup localStorage:", error);
    }
  }
}

// Singleton instance
export const storage = StorageService.getInstance();

// Data type constants
export const STORAGE_KEYS = {
  EDITOR_STATE: "editor-state",
  EDITOR_DRAFTS: "editor-drafts",
  LAYOUT_PREFERENCES: "layout-preferences",
  FILE_EXPLORER_STATE: "file-explorer-state",
  PROJECT_CACHE: "project-cache",
  RECENT_FILES: "recent-files",
  USER_PREFERENCES: "user-preferences",
} as const;

export type StorageKey = typeof STORAGE_KEYS[keyof typeof STORAGE_KEYS];