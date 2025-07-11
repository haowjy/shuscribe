/**
 * LRU Cache Manager for localStorage with size limits
 * Manages document caching with automatic eviction when approaching storage limits
 */

export interface CacheEntry<T> {
  data: T;
  accessTime: number;
  size: number; // Size in bytes
}

export interface CacheMetrics {
  totalSize: number;
  entryCount: number;
  hitRate: number;
  totalAccesses: number;
  hits: number;
  misses: number;
}

export class LRUCacheManager<T> {
  private keyPrefix: string;
  private maxSizeBytes: number;
  private metricsKey: string;

  constructor(keyPrefix: string, maxSizeBytes: number = 2.5 * 1024 * 1024) { // 2.5MB default (half of typical 5MB localStorage)
    this.keyPrefix = keyPrefix;
    this.maxSizeBytes = maxSizeBytes;
    this.metricsKey = `${keyPrefix}_metrics`;
  }

  /**
   * Get item from cache, updating access time
   */
  get(key: string): T | null {
    const fullKey = `${this.keyPrefix}_${key}`;
    const metrics = this.getMetrics();
    
    try {
      const item = localStorage.getItem(fullKey);
      if (!item) {
        this.updateMetrics({ ...metrics, misses: metrics.misses + 1, totalAccesses: metrics.totalAccesses + 1 });
        return null;
      }

      const cacheEntry: CacheEntry<T> = JSON.parse(item);
      
      // Update access time
      cacheEntry.accessTime = Date.now();
      localStorage.setItem(fullKey, JSON.stringify(cacheEntry));
      
      this.updateMetrics({ 
        ...metrics, 
        hits: metrics.hits + 1, 
        totalAccesses: metrics.totalAccesses + 1,
        hitRate: (metrics.hits + 1) / (metrics.totalAccesses + 1)
      });
      
      return cacheEntry.data;
    } catch (error) {
      console.warn(`Cache get error for key ${key}:`, error);
      this.updateMetrics({ ...metrics, misses: metrics.misses + 1, totalAccesses: metrics.totalAccesses + 1 });
      return null;
    }
  }

  /**
   * Set item in cache, with automatic eviction if needed
   */
  set(key: string, data: T): boolean {
    const fullKey = `${this.keyPrefix}_${key}`;
    const serializedData = JSON.stringify(data);
    const entrySize = new Blob([serializedData]).size;
    
    const cacheEntry: CacheEntry<T> = {
      data,
      accessTime: Date.now(),
      size: entrySize
    };

    try {
      // Check if we need to make space
      this.ensureSpace(entrySize, key);
      
      // Store the item
      localStorage.setItem(fullKey, JSON.stringify(cacheEntry));
      
      // Update metrics
      const metrics = this.getMetrics();
      this.updateMetrics({
        ...metrics,
        totalSize: this.calculateTotalSize(),
        entryCount: this.getEntryCount()
      });
      
      return true;
    } catch (error) {
      console.warn(`Cache set error for key ${key}:`, error);
      return false;
    }
  }

  /**
   * Remove item from cache
   */
  remove(key: string): boolean {
    const fullKey = `${this.keyPrefix}_${key}`;
    
    try {
      localStorage.removeItem(fullKey);
      
      // Update metrics
      const metrics = this.getMetrics();
      this.updateMetrics({
        ...metrics,
        totalSize: this.calculateTotalSize(),
        entryCount: this.getEntryCount()
      });
      
      return true;
    } catch (error) {
      console.warn(`Cache remove error for key ${key}:`, error);
      return false;
    }
  }

  /**
   * Check if item exists in cache
   */
  has(key: string): boolean {
    const fullKey = `${this.keyPrefix}_${key}`;
    return localStorage.getItem(fullKey) !== null;
  }

  /**
   * Get all cache keys (without prefix)
   */
  getAllKeys(): string[] {
    const keys: string[] = [];
    const prefixLength = this.keyPrefix.length + 1; // +1 for underscore
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(`${this.keyPrefix}_`)) {
        keys.push(key.substring(prefixLength));
      }
    }
    
    return keys;
  }

  /**
   * Get cache metrics
   */
  getMetrics(): CacheMetrics {
    try {
      const stored = localStorage.getItem(this.metricsKey);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (error) {
      console.warn('Error reading cache metrics:', error);
    }
    
    // Default metrics
    return {
      totalSize: 0,
      entryCount: 0,
      hitRate: 0,
      totalAccesses: 0,
      hits: 0,
      misses: 0
    };
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    const keys = this.getAllKeys();
    keys.forEach(key => {
      localStorage.removeItem(`${this.keyPrefix}_${key}`);
    });
    
    // Reset metrics
    this.updateMetrics({
      totalSize: 0,
      entryCount: 0,
      hitRate: 0,
      totalAccesses: 0,
      hits: 0,
      misses: 0
    });
  }

  /**
   * Get cache entry info (for debugging)
   */
  getEntryInfo(key: string): { size: number; accessTime: number } | null {
    const fullKey = `${this.keyPrefix}_${key}`;
    
    try {
      const item = localStorage.getItem(fullKey);
      if (!item) return null;
      
      const cacheEntry: CacheEntry<T> = JSON.parse(item);
      return {
        size: cacheEntry.size,
        accessTime: cacheEntry.accessTime
      };
    } catch (error) {
      return null;
    }
  }

  /**
   * Ensure we have enough space for a new entry
   */
  private ensureSpace(requiredSize: number, excludeKey?: string): void {
    let currentSize = this.calculateTotalSize();
    
    // If we're already within limits, no need to evict
    if (currentSize + requiredSize <= this.maxSizeBytes) {
      return;
    }
    
    // Get all entries sorted by access time (LRU first)
    const entries = this.getAllEntries().filter(entry => entry.key !== excludeKey);
    entries.sort((a, b) => a.accessTime - b.accessTime);
    
    // Evict oldest entries until we have enough space
    for (const entry of entries) {
      if (currentSize + requiredSize <= this.maxSizeBytes) {
        break;
      }
      
      console.log(`Cache evicting LRU entry: ${entry.key} (${entry.size} bytes, accessed ${new Date(entry.accessTime).toISOString()})`);
      localStorage.removeItem(`${this.keyPrefix}_${entry.key}`);
      currentSize -= entry.size;
    }
  }

  /**
   * Get all cache entries with metadata
   */
  private getAllEntries(): Array<{ key: string; size: number; accessTime: number }> {
    const entries: Array<{ key: string; size: number; accessTime: number }> = [];
    const prefixLength = this.keyPrefix.length + 1;
    
    for (let i = 0; i < localStorage.length; i++) {
      const fullKey = localStorage.key(i);
      if (fullKey && fullKey.startsWith(`${this.keyPrefix}_`)) {
        try {
          const item = localStorage.getItem(fullKey);
          if (item) {
            const cacheEntry: CacheEntry<T> = JSON.parse(item);
            entries.push({
              key: fullKey.substring(prefixLength),
              size: cacheEntry.size,
              accessTime: cacheEntry.accessTime
            });
          }
        } catch (error) {
          // Skip malformed entries
          console.warn(`Skipping malformed cache entry: ${fullKey}`);
        }
      }
    }
    
    return entries;
  }

  /**
   * Calculate total size of all cache entries
   */
  private calculateTotalSize(): number {
    return this.getAllEntries().reduce((total, entry) => total + entry.size, 0);
  }

  /**
   * Get count of cache entries
   */
  private getEntryCount(): number {
    return this.getAllEntries().length;
  }

  /**
   * Update cache metrics
   */
  private updateMetrics(metrics: CacheMetrics): void {
    try {
      localStorage.setItem(this.metricsKey, JSON.stringify(metrics));
    } catch (error) {
      console.warn('Error updating cache metrics:', error);
    }
  }
}

/**
 * Singleton cache managers for different data types
 */
export const documentCache = new LRUCacheManager<any>('doc_cache', 2.5 * 1024 * 1024); // 2.5MB for documents
export const fileTreeCache = new LRUCacheManager<any>('tree_cache', 512 * 1024); // 512KB for file trees