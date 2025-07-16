import { useEffect, useCallback } from "react";
import { storage, STORAGE_KEYS } from "@/lib/storage";

export interface LayoutPreferences {
  fileExplorerSize: number;
  editorSize: number;
  aiPanelSize: number;
  isFileExplorerCollapsed: boolean;
  isAiPanelCollapsed: boolean;
}

interface UsePersistedLayoutParams {
  projectId?: string;
  onLayoutLoaded?: (layout: LayoutPreferences) => void;
}

const DEFAULT_LAYOUT: LayoutPreferences = {
  fileExplorerSize: 20,
  editorSize: 55,
  aiPanelSize: 25,
  isFileExplorerCollapsed: false,
  isAiPanelCollapsed: false,
};

export function usePersistedLayout({ 
  projectId, 
  onLayoutLoaded 
}: UsePersistedLayoutParams = {}) {
  
  /**
   * Load layout preferences from localStorage
   */
  const loadLayout = useCallback((): LayoutPreferences => {
    // Try project-specific layout first, then global
    const projectLayout = projectId 
      ? storage.get<LayoutPreferences>(STORAGE_KEYS.LAYOUT_PREFERENCES, projectId)
      : null;
    
    const globalLayout = storage.get<LayoutPreferences>(STORAGE_KEYS.LAYOUT_PREFERENCES, null);
    
    return projectLayout || globalLayout || DEFAULT_LAYOUT;
  }, [projectId]);

  /**
   * Save layout preferences to localStorage
   */
  const saveLayout = useCallback((layout: Partial<LayoutPreferences>) => {
    const currentLayout = loadLayout();
    const updatedLayout = { ...currentLayout, ...layout };
    
    // Save to project-specific storage if projectId is provided
    const storageKey = projectId || null;
    storage.set(STORAGE_KEYS.LAYOUT_PREFERENCES, updatedLayout, storageKey);
  }, [projectId, loadLayout]);

  /**
   * Update panel sizes
   */
  const updatePanelSizes = useCallback((sizes: {
    fileExplorerSize?: number;
    editorSize?: number;
    aiPanelSize?: number;
  }) => {
    saveLayout(sizes);
  }, [saveLayout]);

  /**
   * Update panel collapsed states
   */
  const updateCollapsedStates = useCallback((states: {
    isFileExplorerCollapsed?: boolean;
    isAiPanelCollapsed?: boolean;
  }) => {
    saveLayout(states);
  }, [saveLayout]);

  /**
   * Reset layout to defaults
   */
  const resetLayout = useCallback(() => {
    const storageKey = projectId || null;
    storage.set(STORAGE_KEYS.LAYOUT_PREFERENCES, DEFAULT_LAYOUT, storageKey);
    onLayoutLoaded?.(DEFAULT_LAYOUT);
  }, [projectId, onLayoutLoaded]);

  /**
   * Toggle file explorer collapsed state
   */
  const toggleFileExplorer = useCallback(() => {
    const currentLayout = loadLayout();
    const newState = !currentLayout.isFileExplorerCollapsed;
    updateCollapsedStates({ isFileExplorerCollapsed: newState });
    return newState;
  }, [loadLayout, updateCollapsedStates]);

  /**
   * Toggle AI panel collapsed state
   */
  const toggleAiPanel = useCallback(() => {
    const currentLayout = loadLayout();
    const newState = !currentLayout.isAiPanelCollapsed;
    updateCollapsedStates({ isAiPanelCollapsed: newState });
    return newState;
  }, [loadLayout, updateCollapsedStates]);

  /**
   * Initialize layout on mount
   */
  useEffect(() => {
    const savedLayout = loadLayout();
    if (onLayoutLoaded) {
      onLayoutLoaded(savedLayout);
    }
  }, [loadLayout, onLayoutLoaded]);

  return {
    loadLayout,
    saveLayout,
    updatePanelSizes,
    updateCollapsedStates,
    resetLayout,
    toggleFileExplorer,
    toggleAiPanel,
    DEFAULT_LAYOUT,
  };
}