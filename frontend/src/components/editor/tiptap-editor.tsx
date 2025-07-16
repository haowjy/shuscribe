"use client";

import React, { useEffect, useRef, useCallback, useMemo } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import CharacterCount from '@tiptap/extension-character-count';
import TextAlign from '@tiptap/extension-text-align';
import { Extension } from '@tiptap/core';
import { Plugin, PluginKey } from '@tiptap/pm/state';
import { Selection } from '@tiptap/pm/state';
import { common, createLowlight } from 'lowlight';
import { ReferenceExtension } from '@/lib/editor/extensions/reference-extension';
import { useSuggestionItems } from '@/hooks/use-reference-items';

import { 
  BaseEditorProps, 
  EditorDocument, 
  EditorInstance,
  ToolbarOptions 
} from '@/lib/editor/editor-types';
import { 
  createEmptyDocument, 
  sanitizeContent,
  isEmptyDocument 
} from '@/lib/editor/content-utils';
import { 
  DraftManager, 
  AutoSaveManager 
} from '@/lib/editor/storage-utils';
import { EditorToolbar } from './editor-toolbar';
import { cn } from '@/lib/utils';
import { TreeItem } from '@/types/api';

// Lowlight instance for syntax highlighting
const lowlight = createLowlight(common);

// Debounce utility for performance optimization
function useDebounce<T extends (...args: any[]) => void>(
  callback: T,
  delay: number
): T {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  return useCallback((...args: Parameters<T>) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    timeoutRef.current = setTimeout(() => {
      callback(...args);
    }, delay);
  }, [callback, delay]) as T;
}

// Extension to handle clicking in empty space
const ClickToFocusExtension = Extension.create({
  name: 'clickToFocus',
  
  addProseMirrorPlugins() {
    return [
      new Plugin({
        key: new PluginKey('clickToFocus'),
        props: {
          handleClick: (view, pos) => {
            // If click is beyond the last line, move cursor to end
            const { doc } = view.state;
            const lastPos = doc.content.size;
            
            if (pos >= lastPos - 1) {
              const endPos = Math.max(0, lastPos - 1);
              const tr = view.state.tr.setSelection(
                Selection.near(view.state.doc.resolve(endPos))
              );
              view.dispatch(tr);
              return true;
            }
            return false;
          },
        },
      })
    ];
  },
});

// Default toolbar options
const DEFAULT_TOOLBAR_OPTIONS: ToolbarOptions = {
  showBold: true,
  showItalic: true,
  showCode: true,
  showStrike: true,
  showHeadings: true,
  showLists: true,
  showCodeBlock: true,
  showBlockquote: true,
  showUndo: true,
  showRedo: true,
  showTextAlign: true,
};

interface TiptapEditorProps extends BaseEditorProps {
  content?: EditorDocument;
  isSaving?: boolean;
  lastSaved?: string;
  onReferenceClick?: (referenceId: string, referenceLabel: string) => void;
  fileTree?: TreeItem[]; // File tree for @ references
}

export function TiptapEditor({
  // Content props
  content,
  initialContent,
  
  // Editor config
  extensions = [],
  placeholder = "Start writing...",
  editable = true,
  className,
  autofocus = false,
  enableToolbar = true,
  toolbarOptions = DEFAULT_TOOLBAR_OPTIONS,
  
  // Storage config
  enableLocalStorage = true,
  enableAutoSave = true,
  autoSaveInterval = 5000, // Increased from 2s to 5s for better performance
  enableDrafts = true,
  
  // Event handlers
  onCreate,
  onUpdate,
  onChange,
  onFocus,
  onBlur,
  onSelectionUpdate,
  onSave,
  onSaveSuccess,
  onSaveError,
  
  // Document management
  documentId,
  isSaving = false,
  lastSaved,
  onReferenceClick,
  fileTree = []
}: TiptapEditorProps) {
  
  const lastContentRef = useRef<EditorDocument | null>(null);
  const lastContentHashRef = useRef<string>('');
  const lastAutoSaveHashRef = useRef<string>('');
  
  // Get suggestion items for @ references - stable reference for extensions
  const stableSuggestionItems = useRef<(props: { query: string }) => any[] | null>(null);
  const { getSuggestionItems } = useSuggestionItems(fileTree);
  
  // Update stable reference when getSuggestionItems changes
  useEffect(() => {
    stableSuggestionItems.current = getSuggestionItems;
  }, [getSuggestionItems]);
  
  // Debounced content change handler for performance
  const debouncedContentChange = useDebounce((newContent: EditorDocument) => {
    // Generate a simple hash for faster comparison
    const contentHash = JSON.stringify(newContent);
    
    if (contentHash !== lastContentHashRef.current) {
      lastContentHashRef.current = contentHash;
      lastContentRef.current = newContent;
      
      // Call update handlers
      onUpdate?.(newContent);
      onChange?.(newContent);
      
      console.log('📝 [TiptapEditor] Content changed for document:', documentId);
      
      // Handle auto-save with improved change detection
      if (enableAutoSave && documentId && enableDrafts && contentHash !== lastAutoSaveHashRef.current) {
        lastAutoSaveHashRef.current = contentHash;
        
        AutoSaveManager.scheduleAutoSave(
          documentId,
          newContent,
          () => {
            console.log(`📝 [TiptapEditor] Draft auto-saved for document ${documentId}`);
          },
          autoSaveInterval
        );
      }
    }
  }, 150); // 150ms debounce for performance
  
  // Create base extensions with stable dependencies
  const createExtensions = useCallback(() => {
    const baseExtensions = [
      StarterKit.configure({
        codeBlock: false, // We'll use the lowlight version instead
      }),
      Placeholder.configure({
        placeholder,
      }),
      CodeBlockLowlight.configure({
        lowlight,
      }),
      CharacterCount.configure({
        limit: null, // No character limit
      }),
      TextAlign.configure({
        types: ['heading', 'paragraph', 'listItem'],
        alignments: ['left', 'center', 'right', 'justify'],
        defaultAlignment: 'left',
      }),
      ReferenceExtension.configure({
        suggestions: {
          items: (props: { query: string }) => {
            // Use stable reference to prevent extension recreation
            return stableSuggestionItems.current?.(props) || [];
          },
        },
        onReferenceClick,
      }),
      ClickToFocusExtension,
      ...extensions
    ];
    
    return baseExtensions;
  }, [extensions, placeholder, onReferenceClick]); // Removed fileTree and getSuggestionItems dependencies
  
  // Initialize editor
  const editor = useEditor({
    extensions: createExtensions(),
    content: content || initialContent || createEmptyDocument(),
    editable,
    autofocus: autofocus || 'end', // Auto-focus at end by default
    
    onCreate: ({ editor }) => {
      onCreate?.(editor);
    },
    
    onUpdate: ({ editor }) => {
      const newContent = editor.getJSON() as EditorDocument;
      
      // Use debounced handler for better performance
      debouncedContentChange(newContent);
    },
    
    onFocus: () => {
      onFocus?.();
    },
    
    onBlur: () => {
      onBlur?.();
    },
    
    onSelectionUpdate: () => {
      onSelectionUpdate?.();
    },
  });
  
  // Update content when prop changes
  useEffect(() => {
    if (editor && content) {
      const sanitizedContent = sanitizeContent(content);
      const currentContent = editor.getJSON() as EditorDocument;
      
      // Only update if content is different
      if (JSON.stringify(sanitizedContent) !== JSON.stringify(currentContent)) {
        editor.commands.setContent(sanitizedContent);
        lastContentRef.current = sanitizedContent;
      }
    }
  }, [editor, content]);
  
  // Load draft on mount if enabled
  useEffect(() => {
    if (editor && documentId && enableDrafts && enableLocalStorage) {
      const draft = DraftManager.getDraft(documentId);
      if (draft && !content) {
        editor.commands.setContent(draft.content);
        lastContentRef.current = draft.content;
      }
    }
  }, [editor, documentId, enableDrafts, enableLocalStorage, content]);
  
  // Cleanup auto-save on unmount
  useEffect(() => {
    return () => {
      if (documentId) {
        AutoSaveManager.clearAutoSave(documentId);
      }
    };
  }, [documentId]);

  // Manual save function
  const handleSave = useCallback(async (): Promise<boolean> => {
    if (!editor || !onSave) return false;
    
    console.log('📝 [TiptapEditor] Manual save triggered for document:', documentId);
    
    try {
      const content = editor.getJSON() as EditorDocument;
      const success = await onSave(content);
      
      if (success) {
        console.log('📝 [TiptapEditor] Save successful for document:', documentId);
        onSaveSuccess?.();
        return true;
      } else {
        console.log('📝 [TiptapEditor] Save failed for document:', documentId);
        onSaveError?.('Save failed');
        return false;
      }
    } catch (error) {
      console.error('📝 [TiptapEditor] Save error for document:', documentId, error);
      onSaveError?.(error instanceof Error ? error.message : 'Save failed');
      return false;
    }
  }, [editor, onSave, onSaveSuccess, onSaveError, documentId]);

  // Handle keyboard shortcuts (Ctrl+S / Cmd+S)
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Check for Ctrl+S (Windows/Linux) or Cmd+S (Mac)
      if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault();
        if (onSave) {
          handleSave();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleSave, onSave]);

  // Create editor instance API
  const editorInstance: EditorInstance = useMemo(() => ({
    editor,
    getContent: () => editor?.getJSON() as EditorDocument || createEmptyDocument(),
    setContent: (newContent: EditorDocument) => {
      if (editor) {
        editor.commands.setContent(sanitizeContent(newContent));
      }
    },
    getHTML: () => editor?.getHTML() || '',
    getText: () => editor?.getText() || '',
    focus: () => editor?.commands.focus(),
    blur: () => editor?.commands.blur(),
    isEmpty: () => {
      if (!editor) return true;
      return isEmptyDocument(editor.getJSON() as EditorDocument);
    },
    canUndo: () => editor?.can().undo() || false,
    canRedo: () => editor?.can().redo() || false,
    undo: () => editor?.commands.undo(),
    redo: () => editor?.commands.redo(),
    save: handleSave,
  }), [editor, handleSave]);
  
  // Note: EditorInstance is available through the returned editorInstance object
  
  if (!editor) {
    return (
      <div className={cn("flex items-center justify-center h-32", className)}>
        <div className="text-sm text-muted-foreground">Loading editor...</div>
      </div>
    );
  }
  
  return (
    <div className={cn("w-full h-full flex flex-col", className)}>
      {/* Toolbar */}
      {enableToolbar && (
        <EditorToolbar 
          editor={editor} 
          options={toolbarOptions}
        />
      )}
      
      {/* Editor Content */}
      <div 
        className="flex-1 overflow-hidden h-0"
        onClick={(e) => {
          // If clicking in empty space below content, focus at end of document
          if (editor && e.target === e.currentTarget) {
            editor.commands.focus('end');
          }
        }}
      >
        <div className="h-full overflow-auto">
          <EditorContent 
            editor={editor}
            className={cn(
              "w-full min-h-full min-h-[200px]",
              "prose prose-base max-w-[70ch] mx-auto focus:outline-none",
              "text-foreground text-base leading-relaxed",
              "[&_.ProseMirror]:outline-none [&_.ProseMirror]:p-4 [&_.ProseMirror]:min-h-[calc(100vh-200px)]",
              "[&_.ProseMirror]:cursor-text", // Make entire editor area show text cursor
            "[&_.ProseMirror_h1]:text-2xl [&_.ProseMirror_h1]:font-bold [&_.ProseMirror_h1]:mb-4 [&_.ProseMirror_h1]:mt-6",
            "[&_.ProseMirror_h2]:text-xl [&_.ProseMirror_h2]:font-semibold [&_.ProseMirror_h2]:mb-3 [&_.ProseMirror_h2]:mt-5",
            "[&_.ProseMirror_h3]:text-lg [&_.ProseMirror_h3]:font-medium [&_.ProseMirror_h3]:mb-2 [&_.ProseMirror_h3]:mt-4",
            "[&_.ProseMirror_p]:mb-4 [&_.ProseMirror_p]:leading-relaxed",
            "[&_.ProseMirror_strong]:font-semibold [&_.ProseMirror_em]:italic",
            "[&_.ProseMirror_ul]:mb-4 [&_.ProseMirror_ul]:ml-6 [&_.ProseMirror_ul]:list-disc",
            "[&_.ProseMirror_ol]:mb-4 [&_.ProseMirror_ol]:ml-6 [&_.ProseMirror_ol]:list-decimal",
            "[&_.ProseMirror_li]:mb-1",
            "[&_.ProseMirror_blockquote]:border-l-4 [&_.ProseMirror_blockquote]:border-muted-foreground [&_.ProseMirror_blockquote]:pl-4 [&_.ProseMirror_blockquote]:text-muted-foreground [&_.ProseMirror_blockquote]:italic",
            "[&_.ProseMirror_code]:bg-muted [&_.ProseMirror_code]:px-1 [&_.ProseMirror_code]:py-0.5 [&_.ProseMirror_code]:rounded [&_.ProseMirror_code]:text-sm",
            "[&_.ProseMirror_pre]:bg-muted [&_.ProseMirror_pre]:p-4 [&_.ProseMirror_pre]:rounded [&_.ProseMirror_pre]:overflow-x-auto",
            "[&_.ProseMirror_pre_code]:bg-transparent [&_.ProseMirror_pre_code]:p-0"
            )}
          />
        </div>
      </div>
      
      {/* Status bar */}
      {documentId && (
        <div className="border-t px-4 py-1 bg-secondary/20 text-xs text-muted-foreground flex justify-between">
          <span>
            {isSaving ? (
              'Saving...'
            ) : lastSaved ? (
              `Saved ${lastSaved}`
            ) : DraftManager.hasDraft(documentId) ? (
              'Draft saved'
            ) : (
              'Ready'
            )}
          </span>
          <span>
            Words: {editor.storage.characterCount?.words() || 0} | 
            Characters: {editor.storage.characterCount?.characters() || 0}
          </span>
        </div>
      )}
    </div>
  );
}

export type { EditorInstance };
export default TiptapEditor;