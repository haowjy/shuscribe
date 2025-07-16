// Base Tiptap editor
export { TiptapEditor, type EditorInstance } from './tiptap-editor';

// Editor variants
export { BasicEditor } from './variants/basic-editor';
export { RichEditor } from './variants/rich-editor';
export { MinimalEditor } from './variants/minimal-editor';

// Convenience exports for different use cases
export { RichEditor as Editor } from './variants/rich-editor'; // Default editor
export { BasicEditor as SimpleEditor } from './variants/basic-editor';
export { MinimalEditor as PlainEditor } from './variants/minimal-editor';