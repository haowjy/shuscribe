# TiptapEditor Component Documentation

## Overview

The `TiptapEditor` is a highly configurable rich text editor built on Tiptap/ProseMirror, designed for maximum reusability across different use cases - from full-featured document editing to lightweight chat interfaces.

## Configuration Props

```tsx
interface TiptapEditorProps {
  // Content management
  content?: string;
  placeholder?: string;
  onUpdate?: (content: string) => void;
  className?: string;
  
  // Toolbar customization
  toolbar?: {
    show?: boolean; // Show entire toolbar (default: true)
    sections?: ToolbarSection[]; // Which sections to include (default: all)
    commands?: EditorCommand[]; // Which specific commands to include (default: all)
  };
  
  // Footer customization
  footer?: {
    show?: boolean; // Hide entire footer (default: true)
    showCharacterCount?: boolean; // Show character count (default: true)
    showWordCount?: boolean; // Show word count (default: true)
    showStats?: boolean; // Show sentences/paragraphs (default: false)
  };
  
  // Extension configuration
  extensions?: {
    overrides?: {
      starterKit?: Partial<StarterKitConfig>;
      textAlign?: Partial<TextAlignConfig>;
      highlight?: Partial<HighlightConfig>;
      link?: Partial<LinkConfig>;
      image?: Partial<ImageConfig>;
      taskItem?: Partial<TaskItemConfig>;
      table?: Partial<TableConfig>;
    };
  };
}
```

## Usage Examples

### Full-Featured Editor (Default)
```tsx
<TiptapEditor
  placeholder="Start writing your story..."
  onUpdate={(content) => saveDocument(content)}
/>
```

### Lightweight Chat Editor
```tsx
<TiptapEditor
  placeholder="Type a message..."
  onUpdate={(content) => updateMessage(content)}
  toolbar={{
    sections: ['history', 'formatting', 'lists', 'alignment'],
    commands: ['undo', 'redo', 'toggleBold', 'toggleItalic', 'toggleBulletList', 'setTextAlign']
  }}
  footer={{ show: false }}
/>
```

### Minimal Editor (Comments/Notes)
```tsx
<TiptapEditor
  placeholder="Add a note..."
  toolbar={{
    sections: ['formatting'],
    commands: ['toggleBold', 'toggleItalic']
  }}
  footer={{
    showCharacterCount: false,
    showWordCount: false
  }}
/>
```

### Custom Extension Configuration
```tsx
<TiptapEditor
  extensions={{
    overrides: {
      highlight: { multicolor: false },
      link: { openOnClick: true },
      table: { resizable: false }
    }
  }}
/>
```

## Reusability Patterns

### 1. Component Composition Approach
For maximum customization, compose your own editor using the exported hooks and components:

```tsx
import { EditorContent } from '@tiptap/react'
import { useEditorConfig, useEditorToolbarState } from '@/components/editor/hooks'
import { executeEditorCommand } from '@/components/editor/utils/editor-helpers'
import { Button } from '@/components/tiptap-ui-primitive/button'

export function CustomChatEditor() {
  const { editor, editorState } = useEditorConfig({
    placeholder: 'Type a message...',
    extensions: {
      overrides: {
        highlight: { multicolor: false }
      }
    }
  })
  
  if (!editor) return null

  return (
    <div className="border rounded-lg">
      {/* Custom minimal toolbar */}
      <div className="flex gap-1 p-2 border-b">
        <Button onClick={() => executeEditorCommand(editor, 'toggleBold')}>
          <Bold size={16} />
        </Button>
        <Button onClick={() => executeEditorCommand(editor, 'toggleItalic')}>
          <Italic size={16} />
        </Button>
      </div>
      
      {/* Editor content */}
      <div className="p-3">
        <EditorContent editor={editor} />
      </div>
    </div>
  )
}
```

### 2. Shared Hook Pattern
Create reusable configuration hooks for different editor types:

```tsx
// hooks/use-chat-editor.ts
export function useChatEditor(onUpdate?: (content: string) => void) {
  return useEditorConfig({
    placeholder: 'Type a message...',
    onUpdate,
    extensions: {
      overrides: {
        starterKit: {
          heading: false,
          codeBlock: false
        }
      }
    }
  })
}

// hooks/use-document-editor.ts
export function useDocumentEditor(onUpdate?: (content: string) => void) {
  return useEditorConfig({
    placeholder: 'Start writing...',
    onUpdate,
    // Full feature set (default)
  })
}
```

## Future Customization TODO

The editor is designed to be extended further. Planned additions include:

```tsx
// TODO: Additional props for even more customization
interface FutureTiptapEditorProps extends TiptapEditorProps {
  // Editor behavior
  editable?: boolean;
  autofocus?: boolean | 'start' | 'end' | number;
  editorProps?: Record<string, any>;
  
  // Custom handlers
  onImageUpload?: (file: File) => Promise<string>;
  
  // Constraints
  characterLimit?: number;
  minHeight?: number;
  
  // Advanced customization
  extraExtensions?: Extension[];
}
```

## Live Examples

The editor is demonstrated in three variants at `/editor-test/`:

1. **Full-Featured Editor**: All toolbar sections and features enabled
2. **Lightweight Chat Editor**: Basic formatting only (history, formatting, lists, alignment)  
3. **Minimal Notes Editor**: Essential formatting only (bold, italic)

## Current Features

- **Toolbar Sections**: history, textStyle, formatting, lists, alignment, blocks, insert, table
- **Content Support**: Rich text, images (paste/drop), tables, lists, headings, code blocks
- **Formatting**: Bold, italic, underline, strikethrough, code, highlight, sub/superscript
- **Advanced**: Text alignment, task lists, blockquotes, horizontal rules
- **Customization**: Configurable toolbar, footer, and extension overrides
- **Accessibility**: Keyboard navigation, screen reader support
- **Performance**: Optimized for fast typing and large documents