import { Extension } from '@tiptap/core';
import { Editor } from '@tiptap/react';

// Base content type for Tiptap JSON documents
export interface TiptapContent {
  type: string;
  content?: TiptapContent[];
  attrs?: Record<string, any>;
  marks?: Array<{
    type: string;
    attrs?: Record<string, any>;
  }>;
  text?: string;
}

// Document structure for our application
export interface EditorDocument {
  type: 'doc';
  content: TiptapContent[];
}

// Editor configuration interface
export interface EditorConfig {
  extensions?: Extension[];
  placeholder?: string;
  editable?: boolean;
  className?: string;
  autofocus?: boolean;
  enableToolbar?: boolean;
  toolbarOptions?: ToolbarOptions;
}

// Toolbar configuration
export interface ToolbarOptions {
  showBold?: boolean;
  showItalic?: boolean;
  showCode?: boolean;
  showStrike?: boolean;
  showHeadings?: boolean;
  showLists?: boolean;
  showCodeBlock?: boolean;
  showBlockquote?: boolean;
  showLink?: boolean;
  showUndo?: boolean;
  showRedo?: boolean;
  showTextAlign?: boolean;
}

// Editor variant types
export type EditorVariant = 'basic' | 'rich' | 'fiction' | 'minimal';

// Storage types
export interface StorageConfig {
  enableLocalStorage?: boolean;
  enableAutoSave?: boolean;
  autoSaveInterval?: number; // milliseconds
  enableDrafts?: boolean;
}

// Draft management
export interface Draft {
  id: string;
  content: EditorDocument;
  timestamp: number;
  title?: string;
}

// Document state for tab system
export interface DocumentState {
  id: string;
  title: string;
  content: EditorDocument;
  isDirty: boolean;
  isTemp: boolean;
  lastModified: number;
  order: number;
}

// Editor instance interface
export interface EditorInstance {
  editor: Editor | null;
  getContent: () => EditorDocument;
  setContent: (content: EditorDocument) => void;
  getHTML: () => string;
  getText: () => string;
  focus: () => void;
  blur: () => void;
  isEmpty: () => boolean;
  canUndo: () => boolean;
  canRedo: () => void;
  undo: () => void;
  redo: () => void;
  save: () => Promise<boolean>;
}

// Event handlers
export interface EditorEventHandlers {
  onCreate?: (editor: Editor) => void;
  onUpdate?: (content: EditorDocument) => void;
  onChange?: (content: EditorDocument) => void;
  onFocus?: () => void;
  onBlur?: () => void;
  onSelectionUpdate?: () => void;
  onSave?: (content: EditorDocument) => Promise<boolean>;
  onSaveSuccess?: () => void;
  onSaveError?: (error: string) => void;
}

// Complete editor props
export interface BaseEditorProps extends EditorConfig, StorageConfig, EditorEventHandlers {
  documentId?: string;
  initialContent?: EditorDocument;
  variant?: EditorVariant;
}