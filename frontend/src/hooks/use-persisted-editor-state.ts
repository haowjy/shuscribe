import { useEffect, useCallback, useRef } from "react";
import { EditorTab } from "@/data/editor-tabs";
import { storage, STORAGE_KEYS } from "@/lib/storage";

export interface EditorState {
  tabs: EditorTab[];
  activeTabId: string;
  tempFileCounter: number;
}

export interface EditorDraft {
  [tabId: string]: {
    content: string;
    timestamp: number;
    isDirty: boolean;
  };
}

interface UsePersistedEditorStateParams {
  projectId: string;
}

export function usePersistedEditorState({ 
  projectId
}: UsePersistedEditorStateParams) {
  const saveDraftsTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const saveStateTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Ensure all tabs have valid order properties
   */
  const ensureTabOrder = useCallback((tabs: EditorTab[]): EditorTab[] => {
    return tabs.map((tab, index) => ({
      ...tab,
      order: tab.order ?? index
    }));
  }, []);

  /**
   * Load editor state from localStorage
   */
  const loadEditorState = useCallback((): EditorState | null => {
    const state = storage.get<EditorState>(STORAGE_KEYS.EDITOR_STATE, projectId);
    if (state) {
      // Ensure all tabs have order property
      return {
        ...state,
        tabs: ensureTabOrder(state.tabs)
      };
    }
    return state;
  }, [projectId, ensureTabOrder]);

  /**
   * Save editor state to localStorage (debounced)
   */
  const saveEditorState = useCallback((state: EditorState) => {
    // Clear existing timeout
    if (saveStateTimeoutRef.current) {
      clearTimeout(saveStateTimeoutRef.current);
    }

    // Debounce saves to avoid too frequent writes
    saveStateTimeoutRef.current = setTimeout(() => {
      storage.set(STORAGE_KEYS.EDITOR_STATE, state, projectId);
    }, 500);
  }, [projectId]);

  /**
   * Load drafts from localStorage
   */
  const loadDrafts = useCallback((): EditorDraft => {
    return storage.get<EditorDraft>(STORAGE_KEYS.EDITOR_DRAFTS, projectId) || {};
  }, [projectId]);

  /**
   * Save single draft to localStorage (debounced)
   */
  const saveDraft = useCallback((tabId: string, content: string, isDirty: boolean) => {
    // Clear existing timeout
    if (saveDraftsTimeoutRef.current) {
      clearTimeout(saveDraftsTimeoutRef.current);
    }

    // Debounce draft saves to avoid too frequent writes
    saveDraftsTimeoutRef.current = setTimeout(() => {
      const currentDrafts = loadDrafts();
      const updatedDrafts = {
        ...currentDrafts,
        [tabId]: {
          content,
          timestamp: Date.now(),
          isDirty,
        },
      };

      storage.set(STORAGE_KEYS.EDITOR_DRAFTS, updatedDrafts, projectId);
    }, 1000); // 1 second debounce for drafts
  }, [projectId, loadDrafts]);

  /**
   * Remove draft from localStorage
   */
  const removeDraft = useCallback((tabId: string) => {
    const currentDrafts = loadDrafts();
    const { [tabId]: removed, ...remainingDrafts } = currentDrafts;
    
    if (removed) {
      storage.set(STORAGE_KEYS.EDITOR_DRAFTS, remainingDrafts, projectId);
    }
  }, [projectId, loadDrafts]);

  /**
   * Clear all drafts for the project
   */
  const clearAllDrafts = useCallback(() => {
    storage.remove(STORAGE_KEYS.EDITOR_DRAFTS, projectId);
  }, [projectId]);

  /**
   * Get draft for a specific tab
   */
  const getDraft = useCallback((tabId: string) => {
    const drafts = loadDrafts();
    return drafts[tabId] || null;
  }, [loadDrafts]);

  /**
   * Check if tab has unsaved changes
   */
  const hasDraft = useCallback((tabId: string): boolean => {
    const draft = getDraft(tabId);
    return draft ? draft.isDirty : false;
  }, [getDraft]);

  /**
   * Get all tabs with unsaved changes
   */
  const getDirtyTabs = useCallback((): string[] => {
    const drafts = loadDrafts();
    return Object.keys(drafts).filter(tabId => drafts[tabId].isDirty);
  }, [loadDrafts]);

  /**
   * Restore content from draft if available
   */
  const restoreContentFromDraft = useCallback((tab: EditorTab): EditorTab => {
    const draft = getDraft(tab.id);
    if (draft && draft.isDirty) {
      try {
        // Parse JSON content
        const content = JSON.parse(draft.content);
        return {
          ...tab,
          content,
          isDirty: true,
        };
      } catch (error) {
        console.error("Error parsing draft content:", error);
        // Return original tab if JSON parsing fails
        return tab;
      }
    }
    return tab;
  }, [getDraft]);

  /**
   * Cleanup timeouts on unmount
   */
  useEffect(() => {
    return () => {
      if (saveDraftsTimeoutRef.current) {
        clearTimeout(saveDraftsTimeoutRef.current);
      }
      if (saveStateTimeoutRef.current) {
        clearTimeout(saveStateTimeoutRef.current);
      }
    };
  }, []);

  return {
    // State management
    loadEditorState,
    saveEditorState,
    
    // Draft management
    saveDraft,
    removeDraft,
    clearAllDrafts,
    getDraft,
    hasDraft,
    getDirtyTabs,
    restoreContentFromDraft,
    
    // Utilities
    loadDrafts,
    ensureTabOrder,
  };
}