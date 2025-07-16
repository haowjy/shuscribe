"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import { 
  EditorStateManager, 
  StorageUtils, 
  DraftManager,
  AutoSaveManager 
} from '@/lib/editor/storage-utils';
import { useSyncLocalChanges } from '@/lib/query/enhanced-hooks';

interface StorageContextValue {
  isStorageAvailable: boolean;
  storageUsage: number;
  syncPending: boolean;
  lastSyncTime: Date | null;
  triggerSync: () => void;
  clearAllData: () => void;
  exportData: () => object;
  importData: (data: any) => boolean;
}

const StorageContext = createContext<StorageContextValue | null>(null);

interface StorageProviderProps {
  children: React.ReactNode;
  enableAutoSync?: boolean;
  autoSyncInterval?: number; // milliseconds
  maxDraftAge?: number; // milliseconds
}

export function StorageProvider({
  children,
  enableAutoSync = true,
  autoSyncInterval = 5 * 60 * 1000, // 5 minutes
  maxDraftAge = 7 * 24 * 60 * 60 * 1000, // 7 days
}: StorageProviderProps) {
  const [isStorageAvailable, setIsStorageAvailable] = useState(false);
  const [storageUsage, setStorageUsage] = useState(0);
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);
  
  const syncMutation = useSyncLocalChanges();
  
  // Check storage availability on mount
  useEffect(() => {
    try {
      const test = '__storage_test__';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      setIsStorageAvailable(true);
    } catch {
      setIsStorageAvailable(false);
      console.warn('localStorage is not available');
    }
  }, []);
  
  // Update storage usage periodically
  useEffect(() => {
    const updateUsage = () => {
      if (isStorageAvailable) {
        setStorageUsage(StorageUtils.getEditorStorageUsage());
      }
    };
    
    updateUsage();
    const interval = setInterval(updateUsage, 30000); // Every 30 seconds
    
    return () => clearInterval(interval);
  }, [isStorageAvailable]);
  
  // Auto-sync local changes to API
  useEffect(() => {
    if (!enableAutoSync || !isStorageAvailable) return;
    
    const performSync = async () => {
      try {
        await syncMutation.mutateAsync();
        setLastSyncTime(new Date());
      } catch (error) {
        console.warn('Auto-sync failed:', error);
      }
    };
    
    // Initial sync after a short delay
    const initialTimeout = setTimeout(performSync, 5000);
    
    // Regular sync interval
    const interval = setInterval(performSync, autoSyncInterval);
    
    return () => {
      clearTimeout(initialTimeout);
      clearInterval(interval);
    };
  }, [enableAutoSync, isStorageAvailable, autoSyncInterval, syncMutation]);
  
  // Cleanup old drafts periodically
  useEffect(() => {
    if (!isStorageAvailable) return;
    
    const cleanupOldDrafts = () => {
      const cleaned = DraftManager.cleanupOldDrafts(maxDraftAge);
      if (cleaned > 0) {
        console.log(`Cleaned up ${cleaned} old drafts`);
      }
    };
    
    // Initial cleanup
    cleanupOldDrafts();
    
    // Daily cleanup
    const interval = setInterval(cleanupOldDrafts, 24 * 60 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [isStorageAvailable, maxDraftAge]);
  
  // Cleanup auto-saves on unmount
  useEffect(() => {
    return () => {
      AutoSaveManager.clearAllAutoSaves();
    };
  }, []);
  
  // Handle page visibility change for sync
  useEffect(() => {
    if (!enableAutoSync || !isStorageAvailable) return;
    
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        // Sync when page becomes visible
        setTimeout(() => {
          syncMutation.mutate();
        }, 1000);
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [enableAutoSync, isStorageAvailable, syncMutation]);
  
  // Handle page unload to save state
  useEffect(() => {
    if (!isStorageAvailable) return;
    
    const handleBeforeUnload = () => {
      // Save any pending editor state
      AutoSaveManager.clearAllAutoSaves();
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isStorageAvailable]);
  
  const triggerSync = async () => {
    try {
      await syncMutation.mutateAsync();
      setLastSyncTime(new Date());
    } catch (error) {
      console.error('Manual sync failed:', error);
      throw error;
    }
  };
  
  const clearAllData = () => {
    if (isStorageAvailable) {
      StorageUtils.clearAllEditorData();
      setStorageUsage(0);
      setLastSyncTime(null);
    }
  };
  
  const exportData = () => {
    return StorageUtils.exportData();
  };
  
  const importData = (data: any) => {
    return StorageUtils.importData(data);
  };
  
  const contextValue: StorageContextValue = {
    isStorageAvailable,
    storageUsage,
    syncPending: syncMutation.isPending,
    lastSyncTime,
    triggerSync,
    clearAllData,
    exportData,
    importData,
  };
  
  return (
    <StorageContext.Provider value={contextValue}>
      {children}
    </StorageContext.Provider>
  );
}

export function useStorage() {
  const context = useContext(StorageContext);
  if (!context) {
    throw new Error('useStorage must be used within a StorageProvider');
  }
  return context;
}

export default StorageProvider;