'use client'

import { cn } from '@/lib/utils'
import { EditorContent, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import CharacterCount from '@tiptap/extension-character-count'

interface ChatComposerProps {
  // HTML content string
  value: string
  onChange: (value: string) => void
  onSend: () => void
  onCancel?: () => void
  placeholder?: string
  disabled?: boolean
  minHeight?: number
  maxHeight?: number
  className?: string
}

export function ChatComposer({
  value,
  onChange,
  onSend,
  onCancel,
  placeholder = 'Type a message...',
  disabled = false,
  minHeight = 80,
  maxHeight = 200,
  className,
}: ChatComposerProps) {
  const editor = useEditor({
    extensions: [StarterKit, Placeholder.configure({ placeholder }), CharacterCount],
    content: value || '<p></p>',
    editable: !disabled,
    autofocus: false,
    immediatelyRender: false,
    editorProps: {
      attributes: {
        class: cn(
          'tiptap focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background max-w-none',
          'w-full rounded-md border border-border bg-background px-3 py-2',
          'text-sm placeholder:text-muted-foreground',
          'min-h-[80px]',
        ),
        style: `min-height:${minHeight}px; max-height:${maxHeight}px; overflow:auto;`,
      },
      handleKeyDown(view, event) {
        if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
          event.preventDefault()
          if (!disabled) onSend()
          return true
        }
        if (event.key === 'Escape') {
          if (onCancel) {
            event.preventDefault()
            onCancel()
            return true
          }
        }
        // Let Enter create new line by default
        return false
      },
    },
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML())
    },
  })

  // Keep external value in sync if it changes externally
  if (editor && editor.getHTML() !== (value || '<p></p>')) {
    // Only update if content truly differs to avoid loop
    // This allows parent to clear content after send
    // Do not preserve selection when external reset
    editor.commands.setContent(value || '<p></p>', { emitUpdate: false })
  }

  // Show loading state while editor initializes
  if (!editor) {
    return (
      <div className={cn('relative', className)}>
        <div className="flex items-center justify-center py-4 text-sm text-muted-foreground">
          Loading editor...
        </div>
      </div>
    )
  }

  return (
    <div className={cn('relative', className)}>
      <EditorContent editor={editor} />
    </div>
  )
}