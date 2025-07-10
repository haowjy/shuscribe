/**
 * BeforeUnload Protection Hook
 * 
 * Protects users from accidentally losing unsaved work when closing the tab
 * or navigating away with Ctrl+W, clicking X, or other navigation actions.
 * 
 * Shows browser's built-in "Changes you made may not be saved" dialog
 * when there are unsaved changes.
 */

import { useEffect } from 'react';

interface UseBeforeUnloadProtectionOptions {
  /** Whether there are unsaved changes that need protection */
  hasUnsavedChanges: boolean;
  /** Optional custom message (note: modern browsers show generic message) */
  message?: string;
}

/**
 * Hook to protect against accidental data loss
 * 
 * @param hasUnsavedChanges - True when user has unsaved work
 * @param message - Custom message (browsers show generic message for security)
 */
export function useBeforeUnloadProtection(
  hasUnsavedChanges: boolean,
  message?: string
): void;
export function useBeforeUnloadProtection(
  options: UseBeforeUnloadProtectionOptions
): void;
export function useBeforeUnloadProtection(
  hasUnsavedChangesOrOptions: boolean | UseBeforeUnloadProtectionOptions,
  message?: string
): void {
  // Handle both function signatures
  const hasUnsavedChanges = typeof hasUnsavedChangesOrOptions === 'boolean' 
    ? hasUnsavedChangesOrOptions 
    : hasUnsavedChangesOrOptions.hasUnsavedChanges;
    
  const dialogMessage = typeof hasUnsavedChangesOrOptions === 'object'
    ? hasUnsavedChangesOrOptions.message
    : message;

  useEffect(() => {
    const beforeUnloadHandler = (event: BeforeUnloadEvent) => {
      // Modern standard approach
      event.preventDefault();
      
      // Legacy support for older browsers (Chrome/Edge < 119)
      event.returnValue = true;
      
      // Custom message (note: modern browsers ignore this for security)
      if (dialogMessage) {
        event.returnValue = dialogMessage;
        return dialogMessage;
      }
    };

    if (hasUnsavedChanges) {
      // Only add listener when there are actually unsaved changes
      window.addEventListener("beforeunload", beforeUnloadHandler);
    } else {
      // Remove listener when changes are saved to avoid unnecessary dialogs
      window.removeEventListener("beforeunload", beforeUnloadHandler);
    }

    // Cleanup on unmount
    return () => {
      window.removeEventListener("beforeunload", beforeUnloadHandler);
    };
  }, [hasUnsavedChanges, dialogMessage]);
}

/**
 * Helper function to determine if any tabs have unsaved changes
 * 
 * @param tabs - Array of editor tabs
 * @returns True if any tab has unsaved changes
 */
export function hasAnyUnsavedChanges(tabs: Array<{ isDirty: boolean; lastSaved?: string }>): boolean {
  return tabs.some(tab => tab.isDirty || (!tab.lastSaved && tab.isDirty));
}

/**
 * Get a user-friendly description of unsaved changes
 * 
 * @param tabs - Array of editor tabs
 * @returns Description of what has unsaved changes
 */
export function getUnsavedChangesDescription(tabs: Array<{ 
  isDirty: boolean; 
  title: string; 
  lastSaved?: string; 
}>): string {
  const unsavedTabs = tabs.filter(tab => tab.isDirty);
  
  if (unsavedTabs.length === 0) {
    return '';
  }
  
  if (unsavedTabs.length === 1) {
    return `"${unsavedTabs[0].title}" has unsaved changes`;
  }
  
  if (unsavedTabs.length === 2) {
    return `"${unsavedTabs[0].title}" and "${unsavedTabs[1].title}" have unsaved changes`;
  }
  
  return `${unsavedTabs.length} documents have unsaved changes`;
}

export default useBeforeUnloadProtection;