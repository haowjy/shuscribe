'use client'

import { useEffect, useRef } from 'react'
import { ChatMessage } from './ChatMessage'
import type { ChatMessage as ChatMessageType } from '../types'

interface ChatMessageListProps {
  messages: ChatMessageType[]
  isLoading: boolean
  onUpdateMessage: (messageId: string, content: string) => void
  onRegenerate: () => void
}

export function ChatMessageList({ 
  messages, 
  isLoading, 
  onUpdateMessage, 
  onRegenerate 
}: ChatMessageListProps) {
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, isLoading])

  return (
    <div className="flex-1 min-h-0 overflow-auto p-2 space-y-2">
      {messages.length === 0 && !isLoading ? (
        <div className="text-center py-8 text-muted-foreground text-sm">
          Start a conversation with your AI assistant
        </div>
      ) : (
        messages.map(message => (
          <div key={message.id}>
            <ChatMessage
              message={message}
              onUpdateMessage={onUpdateMessage}
              onRegenerate={message.role === 'assistant' ? onRegenerate : undefined}
            />
          </div>
        ))
      )}
      {isLoading && (
        <div className="py-2 text-xs text-muted-foreground">AI is thinking…</div>
      )}
      <div ref={endRef} />
    </div>
  )
}