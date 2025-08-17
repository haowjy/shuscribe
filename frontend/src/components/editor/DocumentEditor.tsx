'use client'

import React, { useCallback } from 'react'
import { EditorContent } from '@tiptap/react'
import { EditorToolbar } from './toolbar'
import { EditorFooter } from './footer'
import { useEditorConfig } from './hooks/useEditorConfig'
import { useEditorToolbarState } from './hooks/useEditorToolbarState'
import type { DocumentEditorProps } from './types/editor.types'

export function DocumentEditor({
  content,
  placeholder,
  onUpdate,
  className = "",
  toolbar = {},
  footer = {},
  extensions = {},
  editable = true,
  border = true,
  rounded = true,
  container,
  height,
  minHeight,
  paperMode = false,
  autoPagination = false,
  railMode = 'workspace',
}: DocumentEditorProps) {
  // Initialize editor with configuration hook
  const { editor, editorState } = useEditorConfig({
    content,
    placeholder,
    onUpdate,
    extensions,
    paperMode,
    autoPagination,
  })

  // Initialize toolbar state hook
  const toolbarState = useEditorToolbarState({
    editor,
    editorState,
  })

  // Handle clicks in empty space below content to position cursor at end
  const handleWrapperClick = useCallback((event: React.MouseEvent<HTMLDivElement>) => {
    if (!editor) return

    // Only handle clicks on the wrapper itself, not on the editor content
    if (event.target === event.currentTarget) {
      // Get click position and editor content bounds for efficiency
      const clickY = event.clientY
      
      // Find the TipTap editor element inside the wrapper
      const tiptapElement = event.currentTarget.querySelector('.tiptap')
      if (!tiptapElement) return
      
      const tiptapRect = tiptapElement.getBoundingClientRect()
      const contentBottom = tiptapRect.bottom
      
      // Only position cursor at end if click is below actual content
      if (clickY > contentBottom) {
        const endPos = editor.state.doc.content.size
        editor.chain().focus().setTextSelection(endPos).run()
      }
    }
  }, [editor])

  // Show loading state while editor initializes
  if (!editor) {
    return (
      <div className="flex items-center justify-center py-8">
        Loading editor...
      </div>
    )
  }

  // Build dynamic container classes
  const getBorderClasses = () => {
    if (border === false) return ''
    if (typeof border === 'string') return border
    return 'border border-border'
  }
  
  const getRoundedClasses = () => {
    if (rounded === false) return ''
    if (typeof rounded === 'string') return rounded
    return 'rounded-lg'
  }

  const getPaperModeClasses = () => {
    if (!paperMode) return ''
    
    let paperClasses = 'tiptap-paper-mode'
    
    if (paperMode === true) {
      paperClasses += ' tiptap-paper-mode-default'
    } else if (paperMode === 'A4') {
      paperClasses += ' tiptap-paper-mode-a4'
    } else if (paperMode === 'letter') {
      paperClasses += ' tiptap-paper-mode-letter'
    } else if (paperMode === 'legal') {
      paperClasses += ' tiptap-paper-mode-legal'
    }
    
    return paperClasses
  }
  
  const containerClasses = `h-full flex flex-col ${getBorderClasses()} ${getRoundedClasses()} ${getPaperModeClasses()} ${container || ''} overflow-hidden ${className}`.trim()

  // Build height styling for the editor content
  const editorStyles: React.CSSProperties = {}
  if (height) {
    editorStyles.height = height
  }
  if (minHeight) {
    editorStyles.minHeight = typeof minHeight === 'number' ? `${minHeight}px` : minHeight
  }

  // Apply editability
  if (editor && editor.isEditable !== editable) {
    editor.setEditable(editable)
  }


  return (
    <div className={containerClasses}>
      {/* Toolbar */}
      {toolbar.show !== false && (
        <EditorToolbar
          editor={editor}
          editorState={editorState}
          toolbarState={toolbarState}
          config={toolbar}
          railMode={railMode}
        />
      )}

      {/* Editor Content */}
      <div 
        className="flex-1 min-h-0 overflow-y-auto cursor-text" 
        onClick={handleWrapperClick}
      >
        <EditorContent 
          editor={editor} 
          style={Object.keys(editorStyles).length > 0 ? editorStyles : undefined}
        />
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

export default DocumentEditor