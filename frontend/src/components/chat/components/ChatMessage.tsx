'use client'

import { useState } from 'react'
import { Copy, RotateCcw, Pencil, Check, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ReadOnlyDocumentRenderer } from '@/components/editor/renderers/ReadOnlyDocumentRenderer'
import { ChatComposer } from './ChatComposer'
import type { ChatMessage as ChatMessageType } from '../types'

interface ChatMessageProps {
  message: ChatMessageType
  onUpdateMessage: (messageId: string, content: string) => void
  onRegenerate?: () => void
}

function htmlToText(html: string): string {
  if (typeof window === 'undefined') return html
  const div = document.createElement('div')
  div.innerHTML = html
  return (div.textContent || div.innerText || '').trim()
}

export function ChatMessage({ message, onUpdateMessage, onRegenerate }: ChatMessageProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editContent, setEditContent] = useState('')

  const handleCopy = () => {
    navigator.clipboard.writeText(htmlToText(message.content))
  }

  const handleEdit = () => {
    if (message.role !== 'user') return
    setEditContent(message.content)
    setIsEditing(true)
  }

  const handleSaveEdit = () => {
    onUpdateMessage(message.id, editContent)
    setIsEditing(false)
    setEditContent('')
  }

  const handleCancelEdit = () => {
    setIsEditing(false)
    setEditContent('')
  }

  if (message.role === 'user') {
    return (
      <div className="border-y border-border py-3">
        {isEditing ? (
          <div>
            <ChatComposer
              value={editContent}
              onChange={setEditContent}
              onSend={handleSaveEdit}
              placeholder="Edit your message..."
              minHeight={80}
              maxHeight={240}
            />
            <div className="flex justify-end items-center gap-2 mt-2">
              <Button variant="secondary" size="sm" className="h-7" onClick={handleSaveEdit}>
                <Check className="h-3.5 w-3.5 mr-1" /> Save
              </Button>
              <Button variant="ghost" size="sm" className="h-7" onClick={handleCancelEdit}>
                <X className="h-3.5 w-3.5 mr-1" /> Cancel
              </Button>
            </div>
          </div>
        ) : (
          <div>
            <ReadOnlyDocumentRenderer html={message.content} className="tiptap max-w-none text-sm" />
            <div className="flex justify-end items-center gap-1 mt-2">
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-7 w-7" 
                onClick={handleCopy}
                aria-label="Copy message"
              >
                <Copy className="h-3.5 w-3.5" />
              </Button>
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-7 w-7" 
                onClick={handleEdit}
                aria-label="Edit"
              >
                <Pencil className="h-3.5 w-3.5" />
              </Button>
            </div>
          </div>
        )}
      </div>
    )
  }

  // Assistant message
  return (
    <div className="py-3">
      <ReadOnlyDocumentRenderer html={message.content} className="tiptap max-w-none text-sm" />
      <div className="flex justify-end items-center gap-1 mt-2">
        <Button 
          variant="ghost" 
          size="icon" 
          className="h-7 w-7" 
          onClick={handleCopy}
          aria-label="Copy"
        >
          <Copy className="h-3.5 w-3.5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7"
          onClick={onRegenerate}
          aria-label="Regenerate"
        >
          <RotateCcw className="h-3.5 w-3.5" />
        </Button>
      </div>
    </div>
  )
}