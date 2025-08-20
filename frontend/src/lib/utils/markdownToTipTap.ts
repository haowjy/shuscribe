/**
 * Markdown to TipTap ProseMirror conversion utility
 * 
 * WHY: The seeded content was showing raw markdown text (# Chapter 1) instead of 
 * properly formatted HTML because the existing markdownToProseMirror function
 * wasn't correctly parsing markdown syntax into TipTap's ProseMirror format.
 * 
 * This utility uses TipTap's Editor class combined with the 'marked' library 
 * to properly convert markdown to rich text format that displays correctly in the editor.
 */

import { Editor } from '@tiptap/react'
import { marked } from 'marked'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import CharacterCount from '@tiptap/extension-character-count'
import Underline from '@tiptap/extension-underline'
import TextAlign from '@tiptap/extension-text-align'
import Highlight from '@tiptap/extension-highlight'
import Subscript from '@tiptap/extension-subscript'
import Superscript from '@tiptap/extension-superscript'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import { TableKit } from '@tiptap/extension-table'
import { TextStyle } from '@tiptap/extension-text-style'

// Configure marked for consistent HTML output
marked.setOptions({
  async: false,
  breaks: true,
  gfm: true
})

// TipTap extensions matching the editor configuration
const EXTENSIONS = [
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
]

/**
 * Convert markdown string to TipTap ProseMirror JSON
 * 
 * This function:
 * 1. Converts markdown to HTML using 'marked'
 * 2. Creates a temporary TipTap editor with the HTML content
 * 3. Extracts the ProseMirror JSON from the editor
 * 4. Returns properly formatted content that displays as rich text
 */
export function markdownToTipTap(markdown: string): Record<string, any> {
  try {
    // Step 1: Convert markdown to HTML using marked
    const html = marked(markdown) as string
    
    // Step 2: Create temporary TipTap editor with HTML content
    const tempEditor = new Editor({
      extensions: EXTENSIONS,
      content: html, // TipTap can parse HTML directly
    })
    
    try {
      // Step 3: Extract ProseMirror JSON from the editor
      const prosemirrorJSON = tempEditor.getJSON()
      
      return prosemirrorJSON
    } finally {
      // Always clean up the editor instance
      tempEditor.destroy()
    }
    
  } catch (error) {
    console.error('Failed to convert markdown to TipTap format:', error)
    
    // Return basic paragraph fallback with the original markdown
    return {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: markdown }]
        }
      ]
    }
  }
}


/**
 * Convert HTML string back to TipTap ProseMirror JSON
 * 
 * This function:
 * 1. Takes HTML content from TipTap editor
 * 2. Creates a temporary TipTap editor with the HTML content  
 * 3. Extracts the ProseMirror JSON for storage in Dexie
 * 4. Returns properly formatted JSON that can be restored in editor
 */
export function htmlToTipTap(html: string): Record<string, any> {
  try {
    // Create temporary TipTap editor with HTML content
    const tempEditor = new Editor({
      extensions: EXTENSIONS,
      content: html, // TipTap can parse HTML directly
    })
    
    try {
      // Extract ProseMirror JSON from the editor
      const prosemirrorJSON = tempEditor.getJSON()
      
      return prosemirrorJSON
    } finally {
      // Always clean up the editor instance
      tempEditor.destroy()
    }
    
  } catch (error) {
    console.error('Failed to convert HTML to TipTap format:', error)
    
    // Return basic paragraph fallback with the original HTML as text
    return {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: html }]
        }
      ]
    }
  }
}

/**
 * Calculate word count from ProseMirror JSON
 */
export function calculateWordCount(prosemirrorJSON: Record<string, any>): number {
  function extractText(node: any): string {
    if (node.type === 'text') {
      return node.text || ''
    }
    
    if (node.content && Array.isArray(node.content)) {
      return node.content.map(extractText).join(' ')
    }
    
    return ''
  }

  const text = extractText(prosemirrorJSON)
  return text.trim() ? text.trim().split(/\s+/).length : 0
}