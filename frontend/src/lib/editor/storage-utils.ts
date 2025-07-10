import { EditorDocument, Draft, DocumentState } from './editor-types';
import { serializeContent, deserializeContent, createEmptyDocument } from './content-utils';

// Storage keys
const STORAGE_KEYS = {
  DRAFTS: 'tiptap-drafts',
  DOCUMENTS: 'tiptap-documents',
  EDITOR_STATE: 'tiptap-editor-state',
  AUTO_SAVE: 'tiptap-auto-save',
} as const;

/**
 * Check if localStorage is available
 */
function isLocalStorageAvailable(): boolean {
  try {
    const test = '__localStorage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch {
    return false;
  }
}

/**
 * Safe localStorage operations with error handling
 */
class SafeStorage {
  static getItem(key: string): string | null {
    if (!isLocalStorageAvailable()) return null;
    
    try {
      return localStorage.getItem(key);
    } catch (error) {
      console.error('Failed to read from localStorage:', error);
      return null;
    }
  }

  static setItem(key: string, value: string): boolean {
    if (!isLocalStorageAvailable()) return false;
    
    try {
      localStorage.setItem(key, value);
      return true;
    } catch (error) {
      console.error('Failed to write to localStorage:', error);
      return false;
    }
  }

  static removeItem(key: string): boolean {
    if (!isLocalStorageAvailable()) return false;
    
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error('Failed to remove from localStorage:', error);
      return false;
    }
  }
}

/**
 * Draft management functions
 */
export class DraftManager {
  static saveDraft(documentId: string, content: EditorDocument, title?: string): boolean {
    const draftsData = this.getAllDrafts();
    const draft: Draft = {
      id: documentId,
      content,
      timestamp: Date.now(),
      title
    };

    draftsData[documentId] = draft;
    return SafeStorage.setItem(STORAGE_KEYS.DRAFTS, JSON.stringify(draftsData));
  }

  static getDraft(documentId: string): Draft | null {
    const draftsData = this.getAllDrafts();
    return draftsData[documentId] || null;
  }

  static removeDraft(documentId: string): boolean {
    const draftsData = this.getAllDrafts();
    delete draftsData[documentId];
    return SafeStorage.setItem(STORAGE_KEYS.DRAFTS, JSON.stringify(draftsData));
  }

  static hasDraft(documentId: string): boolean {
    return this.getDraft(documentId) !== null;
  }

  static getAllDrafts(): Record<string, Draft> {
    const data = SafeStorage.getItem(STORAGE_KEYS.DRAFTS);
    if (!data) return {};

    try {
      return JSON.parse(data);
    } catch {
      return {};
    }
  }

  static clearAllDrafts(): boolean {
    return SafeStorage.removeItem(STORAGE_KEYS.DRAFTS);
  }

  static getDraftAge(documentId: string): number | null {
    const draft = this.getDraft(documentId);
    if (!draft) return null;
    
    return Date.now() - draft.timestamp;
  }

  static cleanupOldDrafts(maxAge: number = 7 * 24 * 60 * 60 * 1000): number {
    const drafts = this.getAllDrafts();
    const now = Date.now();
    let cleaned = 0;

    Object.keys(drafts).forEach(id => {
      if (now - drafts[id].timestamp > maxAge) {
        delete drafts[id];
        cleaned++;
      }
    });

    if (cleaned > 0) {
      SafeStorage.setItem(STORAGE_KEYS.DRAFTS, JSON.stringify(drafts));
    }

    return cleaned;
  }
}

/**
 * Document storage for offline-first functionality
 */
export class DocumentStorage {
  static saveDocument(documentId: string, state: DocumentState): boolean {
    const documents = this.getAllDocuments();
    documents[documentId] = {
      ...state,
      lastModified: Date.now()
    };
    return SafeStorage.setItem(STORAGE_KEYS.DOCUMENTS, JSON.stringify(documents));
  }

  static getDocument(documentId: string): DocumentState | null {
    const documents = this.getAllDocuments();
    return documents[documentId] || null;
  }

  static removeDocument(documentId: string): boolean {
    const documents = this.getAllDocuments();
    delete documents[documentId];
    return SafeStorage.setItem(STORAGE_KEYS.DOCUMENTS, JSON.stringify(documents));
  }

  static getAllDocuments(): Record<string, DocumentState> {
    const data = SafeStorage.getItem(STORAGE_KEYS.DOCUMENTS);
    if (!data) return {};

    try {
      return JSON.parse(data);
    } catch {
      return {};
    }
  }

  static clearAllDocuments(): boolean {
    return SafeStorage.removeItem(STORAGE_KEYS.DOCUMENTS);
  }

  static getDocumentContent(documentId: string): EditorDocument | null {
    const document = this.getDocument(documentId);
    return document?.content || null;
  }
}

/**
 * Editor state persistence (tabs, active document, etc.)
 */
export interface EditorState {
  activeDocumentId: string | null;
  openDocuments: string[];
  documentOrder: Record<string, number>;
  lastModified: number;
}

export class EditorStateManager {
  static saveState(state: EditorState): boolean {
    const stateWithTimestamp = {
      ...state,
      lastModified: Date.now()
    };
    return SafeStorage.setItem(STORAGE_KEYS.EDITOR_STATE, JSON.stringify(stateWithTimestamp));
  }

  static getState(): EditorState | null {
    const data = SafeStorage.getItem(STORAGE_KEYS.EDITOR_STATE);
    if (!data) return null;

    try {
      return JSON.parse(data);
    } catch {
      return null;
    }
  }

  static clearState(): boolean {
    return SafeStorage.removeItem(STORAGE_KEYS.EDITOR_STATE);
  }
}

/**
 * Auto-save functionality
 */
export class AutoSaveManager {
  private static timers: Map<string, NodeJS.Timeout> = new Map();
  private static defaultInterval = 2000; // 2 seconds

  static scheduleAutoSave(
    documentId: string, 
    content: EditorDocument, 
    callback: () => void,
    interval: number = this.defaultInterval
  ): void {
    // Clear existing timer
    this.clearAutoSave(documentId);

    // Set new timer
    const timer = setTimeout(() => {
      DraftManager.saveDraft(documentId, content);
      callback();
      this.timers.delete(documentId);
    }, interval);

    this.timers.set(documentId, timer);
  }

  static clearAutoSave(documentId: string): void {
    const timer = this.timers.get(documentId);
    if (timer) {
      clearTimeout(timer);
      this.timers.delete(documentId);
    }
  }

  static clearAllAutoSaves(): void {
    this.timers.forEach((timer) => clearTimeout(timer));
    this.timers.clear();
  }

  static isAutoSaveScheduled(documentId: string): boolean {
    return this.timers.has(documentId);
  }
}

/**
 * Storage utilities for migration and maintenance
 */
export class StorageUtils {
  static getStorageUsage(): number {
    if (!isLocalStorageAvailable()) return 0;

    let total = 0;
    for (let key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        total += (localStorage[key].length + key.length) * 2; // UTF-16 uses 2 bytes per character
      }
    }
    return total;
  }

  static getEditorStorageUsage(): number {
    if (!isLocalStorageAvailable()) return 0;

    const keys = Object.values(STORAGE_KEYS);
    let total = 0;

    keys.forEach(key => {
      const data = SafeStorage.getItem(key);
      if (data) {
        total += (data.length + key.length) * 2;
      }
    });

    return total;
  }

  static exportData(): object {
    return {
      drafts: DraftManager.getAllDrafts(),
      documents: DocumentStorage.getAllDocuments(),
      editorState: EditorStateManager.getState(),
      timestamp: Date.now()
    };
  }

  static importData(data: any): boolean {
    try {
      if (data.drafts) {
        SafeStorage.setItem(STORAGE_KEYS.DRAFTS, JSON.stringify(data.drafts));
      }
      if (data.documents) {
        SafeStorage.setItem(STORAGE_KEYS.DOCUMENTS, JSON.stringify(data.documents));
      }
      if (data.editorState) {
        SafeStorage.setItem(STORAGE_KEYS.EDITOR_STATE, JSON.stringify(data.editorState));
      }
      return true;
    } catch {
      return false;
    }
  }

  static clearAllEditorData(): boolean {
    const keys = Object.values(STORAGE_KEYS);
    let success = true;

    keys.forEach(key => {
      if (!SafeStorage.removeItem(key)) {
        success = false;
      }
    });

    AutoSaveManager.clearAllAutoSaves();
    return success;
  }
}