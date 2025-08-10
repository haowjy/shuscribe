'use client'

import React from 'react'
import { EditorContent } from '@tiptap/react'
import { EditorToolbar } from './toolbar'
import { EditorFooter } from './footer'
import { useEditorConfig } from './hooks/use-editor-config'
import { useEditorToolbarState } from './hooks/use-editor-toolbar-state'
import type { TiptapEditorProps } from './types/editor.types'

export function TiptapEditor({
  content,
  placeholder,
  onUpdate,
  className = "",
  toolbar = {},
  footer = {},
  extensions = {},
}: TiptapEditorProps) {
  // Initialize editor with configuration hook
  const { editor, editorState } = useEditorConfig({
    content,
    placeholder,
    onUpdate,
    extensions,
  })

  // Initialize toolbar state hook
  const toolbarState = useEditorToolbarState({
    editor,
    editorState,
  })

  // Show loading state while editor initializes
  if (!editor) {
    return (
      <div className="flex items-center justify-center py-8">
        Loading editor...
      </div>
    )
  }

  return (
    <div className={`border border-border rounded-lg overflow-hidden ${className}`}>
      {/* Toolbar */}
      {toolbar.show !== false && (
        <EditorToolbar
          editor={editor}
          editorState={editorState}
          toolbarState={toolbarState}
          config={toolbar}
        />
      )}

      {/* Editor Content */}
      <div className="bg-background p-4 min-h-[300px]">
        <EditorContent editor={editor} />
      </div>

      {/* Footer */}
      {footer.show !== false && (
        <EditorFooter 
          editor={editor} 
          config={footer}
        />
      )}
    </div>
  )
}

export default TiptapEditor