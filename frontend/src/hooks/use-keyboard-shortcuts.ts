/**
 * Essential Keyboard Shortcuts Hook
 * 
 * Provides global keyboard shortcuts for the editor workspace:
 * - Ctrl+S: Save current document
 * 
 * Note: Other browser shortcuts (Ctrl+W, Ctrl+T, Ctrl+Tab) cannot be 
 * overridden for security reasons and are handled by the browser.
 */

import { useEffect, useCallback } from 'react';

export interface KeyboardShortcutHandlers {
  onSave?: () => void;
}

export function useKeyboardShortcuts({
  onSave,
}: KeyboardShortcutHandlers) {
  
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Only handle shortcuts when not typing in inputs/textareas
    // (except for the editor, which we want to handle)
    const target = event.target as HTMLElement;
    const isInput = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA';
    const isSelect = target.tagName === 'SELECT';
    
    // Allow shortcuts in the Tiptap editor (contentEditable) but not other inputs
    if (isInput || isSelect) {
      return;
    }

    // Handle Ctrl/Cmd + S for save (only reliable cross-browser shortcut)
    const isCtrlOrCmd = event.ctrlKey || event.metaKey;
    
    if (isCtrlOrCmd && (event.key === 's' || event.key === 'S')) {
      event.preventDefault();
      onSave?.();
    }
  }, [onSave]);

  useEffect(() => {
    // Add global event listener
    document.addEventListener('keydown', handleKeyDown);
    
    // Cleanup on unmount
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);
}

/**
 * Shortcut display helper for UI tooltips
 */
export const KEYBOARD_SHORTCUTS = {
  SAVE: 'Ctrl+S',
} as const;

/**
 * Get platform-specific shortcut display
 * (Shows Cmd on Mac, Ctrl on other platforms)
 */
export function getPlatformShortcut(shortcut: string): string {
  const isMac = typeof window !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  return isMac ? shortcut.replace('Ctrl', 'Cmd') : shortcut;
}