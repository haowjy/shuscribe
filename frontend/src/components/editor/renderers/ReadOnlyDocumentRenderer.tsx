'use client'

import React from 'react'
import { EditorContent, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
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

type ReadOnlyDocumentRendererProps = {
  html: string
  className?: string
}

export function ReadOnlyDocumentRenderer({ html, className }: ReadOnlyDocumentRendererProps) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: { levels: [1, 2, 3] },
        codeBlock: {
          HTMLAttributes: {
            class: 'bg-muted border border-border rounded-md p-3 font-mono text-sm',
          },
        },
      }),
      Underline,
      TextAlign.configure({ types: ['heading', 'paragraph'] }),
      Highlight.configure({ multicolor: true }),
      Subscript,
      Superscript,
      Link.configure({ openOnClick: false, HTMLAttributes: { class: 'text-primary underline cursor-pointer' } }),
      Image.configure({ HTMLAttributes: { class: 'max-w-full h-auto rounded-lg' } }),
      TaskList,
      TaskItem.configure({ nested: true }),
      TableKit.configure({ table: { resizable: true } }),
    ],
    content: html,
    editable: false,
    immediatelyRender: false,
    editorProps: {
      attributes: {
        class: 'tiptap focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background max-w-none',
      },
    },
  })

  if (!editor) return null

  return (
    <div className={className}>
      <div className="prose prose-slate dark:prose-invert max-w-none">
        <EditorContent editor={editor} />
      </div>
    </div>
  )
}


