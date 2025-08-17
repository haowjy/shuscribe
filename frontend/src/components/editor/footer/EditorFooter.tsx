'use client'

import React from 'react'
import { useEditorState } from '@tiptap/react'
import { getEditorStats } from '../utils/editor-helpers'
import type { EditorFooterProps } from '../types/editor.types'

export const EditorFooter = React.memo<EditorFooterProps>(({ editor, config = {} }) => {
  // Use useEditorState for reactive updates when content changes
  const stats = useEditorState({
    editor,
    selector: ({ editor }) => {
      return getEditorStats(editor)
    },
  })

  if (!editor) {
    return (
      <div className="text-xs text-muted-foreground bg-muted/50 px-3 py-2 border-t border-border flex justify-between">
        {config.showCharacterCount !== false && <span>0 characters</span>}
        {config.showWordCount !== false && <span>0 words</span>}
      </div>
    )
  }

  return (
    <div className="text-xs text-muted-foreground bg-muted/50 px-3 py-2 border-t border-border flex justify-between">
      {config.showCharacterCount !== false && (
        <span>{stats?.characters ?? 0} characters</span>
      )}
      {config.showWordCount !== false && (
        <span>{stats?.words ?? 0} words</span>
      )}
      {config.showStats && (
        <span>
          {stats?.sentences ?? 0} sentences | {stats?.paragraphs ?? 0} paragraphs
        </span>
      )}
    </div>
  )
})

EditorFooter.displayName = 'EditorFooter'