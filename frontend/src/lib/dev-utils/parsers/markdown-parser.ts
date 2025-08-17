/**
 * Markdown to ProseMirror JSON conversion utilities
 * Uses TipTap editor to parse markdown into ProseMirror format
 */

import { Editor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Placeholder from "@tiptap/extension-placeholder";
import CharacterCount from "@tiptap/extension-character-count";
import Underline from "@tiptap/extension-underline";
import TextAlign from "@tiptap/extension-text-align";
import Highlight from "@tiptap/extension-highlight";
import Subscript from "@tiptap/extension-subscript";
import Superscript from "@tiptap/extension-superscript";
import Link from "@tiptap/extension-link";
import Image from "@tiptap/extension-image";
import TaskList from "@tiptap/extension-task-list";
import TaskItem from "@tiptap/extension-task-item";
import { TableKit } from "@tiptap/extension-table";
import { TextStyle } from "@tiptap/extension-text-style";

// Default TipTap configuration matching editor setup
const DEFAULT_EXTENSIONS = [
  StarterKit.configure({
    heading: { levels: [1, 2, 3] },
    codeBlock: { HTMLAttributes: { class: 'rounded-md bg-muted p-4' } }
  }),
  Placeholder.configure({ placeholder: '' }),
  CharacterCount,
  Underline,
  TextStyle,
  TextAlign.configure({ types: ['heading', 'paragraph'] }),
  Highlight.configure({ multicolor: false }),
  Subscript,
  Superscript,
  Link.configure({ openOnClick: false }),
  Image.configure({ HTMLAttributes: { class: 'rounded-md' } }),
  TaskList,
  TaskItem.configure({ nested: true }),
  TableKit.configure({
    table: { resizable: true }
  }),
];

/**
 * Convert markdown string to ProseMirror JSON using TipTap editor
 */
export function markdownToProseMirror(markdown: string): Record<string, any> {
  // Create temporary editor instance
  const tempEditor = new Editor({
    extensions: DEFAULT_EXTENSIONS,
    content: '',
  });

  try {
    // Set markdown content with whitespace preservation
    tempEditor.commands.setContent(markdown, {
      parseOptions: {
        preserveWhitespace: 'full',
      },
    });

    // Extract ProseMirror JSON
    const prosemirrorJSON = tempEditor.getJSON();
    
    return prosemirrorJSON;
  } catch (error) {
    console.error('Failed to parse markdown:', error);
    // Return basic paragraph fallback
    return {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: markdown }]
        }
      ]
    };
  } finally {
    // Always clean up editor instance
    tempEditor.destroy();
  }
}

/**
 * Calculate word count from ProseMirror JSON
 */
export function calculateWordCount(prosemirrorJSON: Record<string, any>): number {
  function extractText(node: any): string {
    if (node.type === 'text') {
      return node.text || '';
    }
    
    if (node.content && Array.isArray(node.content)) {
      return node.content.map(extractText).join(' ');
    }
    
    return '';
  }

  const text = extractText(prosemirrorJSON);
  return text.trim() ? text.trim().split(/\s+/).length : 0;
}

/**
 * Create document with markdown content
 */
export function createMarkdownDocument(
  markdown: string,
  metadata: {
    title: string;
    path: string;
    projectId: string;
    tags?: string[];
  }
): {
  content: Record<string, any>;
  wordCount: number;
} {
  const content = markdownToProseMirror(markdown);
  const wordCount = calculateWordCount(content);
  
  return {
    content,
    wordCount,
  };
}

/**
 * Batch convert multiple markdown files
 */
export function batchConvertMarkdown(
  markdownFiles: Array<{
    content: string;
    title: string;
    path: string;
    projectId: string;
    tags?: string[];
  }>
): Array<{
  title: string;
  path: string;
  projectId: string;
  content: Record<string, any>;
  wordCount: number;
  tags: string[];
}> {
  return markdownFiles.map(file => {
    const { content, wordCount } = createMarkdownDocument(file.content, file);
    
    return {
      title: file.title,
      path: file.path,
      projectId: file.projectId,
      content,
      wordCount,
      tags: file.tags || [],
    };
  });
}