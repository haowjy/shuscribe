"use client";

import React, { useEffect, useRef, useCallback, useMemo } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import CharacterCount from '@tiptap/extension-character-count';
import { Extension } from '@tiptap/core';
import { Plugin, PluginKey } from '@tiptap/pm/state';
import { Selection } from '@tiptap/pm/state';
import { common, createLowlight } from 'lowlight';

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

// Lowlight instance for syntax highlighting
const lowlight = createLowlight(common);

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
};

interface TiptapEditorProps extends BaseEditorProps {
  content?: EditorDocument;
  onContentChange?: (content: EditorDocument) => void;
}

export function TiptapEditor({
  // Content props
  content,
  onContentChange,
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
  autoSaveInterval = 2000,
  enableDrafts = true,
  
  // Event handlers
  onCreate,
  onUpdate,
  onChange,
  onFocus,
  onBlur,
  onSelectionUpdate,
  
  // Document management
  documentId
}: TiptapEditorProps) {
  
  const lastContentRef = useRef<EditorDocument | null>(null);
  
  // Create base extensions
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
      ClickToFocusExtension,
      ...extensions
    ];
    
    return baseExtensions;
  }, [extensions, placeholder]);
  
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
      
      // Avoid infinite loops by comparing content
      if (JSON.stringify(newContent) !== JSON.stringify(lastContentRef.current)) {
        lastContentRef.current = newContent;
        
        // Call update handlers
        onUpdate?.(newContent);
        onContentChange?.(newContent);
        onChange?.(newContent);
        
        // Handle auto-save
        if (enableAutoSave && documentId && enableDrafts) {
          AutoSaveManager.scheduleAutoSave(
            documentId,
            newContent,
            () => {
              console.log(`Draft auto-saved for document ${documentId}`);
            },
            autoSaveInterval
          );
        }
      }
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
  }), [editor]);
  
  // Expose editor instance to parent (useful for imperative operations)
  React.useImperativeHandle(React.forwardRef(function EditorRef() { return null; }).ref, () => editorInstance, [editorInstance]);
  
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
        className="flex-1 overflow-auto"
        onClick={(e) => {
          // If clicking in empty space below content, focus at end of document
          if (editor && e.target === e.currentTarget) {
            editor.commands.focus('end');
          }
        }}
      >
        <EditorContent 
          editor={editor}
          className={cn(
            "w-full h-full min-h-[200px]",
            "prose prose-sm max-w-none focus:outline-none",
            "text-foreground text-sm leading-relaxed",
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
      
      {/* Status bar */}
      {documentId && (
        <div className="border-t px-4 py-1 bg-secondary/20 text-xs text-muted-foreground flex justify-between">
          <span>
            {DraftManager.hasDraft(documentId) ? 'Draft saved' : 'Ready'}
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