'use client'

import { useState } from 'react'
import { Send } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ChatMessageList } from './components/ChatMessageList'
import { ChatComposer } from './components/ChatComposer'
import { useChat } from './hooks/useChat'
import type { ChatProps } from './types'

function htmlToText(html: string): string {
  if (typeof window === 'undefined') return html
  const div = document.createElement('div')
  div.innerHTML = html
  return (div.textContent || div.innerText || '').trim()
}

export function AIChat({ thread, onUpdateMessages, onNewThread }: ChatProps) {
  const [composerContent, setComposerContent] = useState('')
  
  const {
    messages,
    isLoading,
    sendMessage,
    updateMessage,
    regenerateLastAssistantMessage
  } = useChat(thread, onUpdateMessages)

  const handleSend = async () => {
    // Validate non-empty message by checking textual content
    const text = htmlToText(composerContent)
    if (!text || isLoading) return

    await sendMessage(composerContent)
    setComposerContent('')
  }

  return (
    <div className="h-full flex flex-col">
      <ChatMessageList
        messages={messages}
        isLoading={isLoading}
        onUpdateMessage={updateMessage}
        onRegenerate={regenerateLastAssistantMessage}
      />

      {/* Composer */}
      <div className="border-t border-border bg-background p-3 sticky bottom-0">
        <div className="space-y-2">
          <ChatComposer
            value={composerContent}
            onChange={setComposerContent}
            onSend={handleSend}
            placeholder="Type your message..."
            disabled={isLoading}
            minHeight={80}
            maxHeight={240}
          />
          <div className="flex items-center justify-between">
            <div className="text-xs text-muted-foreground">
              {typeof navigator !== 'undefined' && navigator.platform?.toLowerCase().includes('mac') ? '⌘' : 'Ctrl'}+Enter to send • Enter for new line
            </div>
            <Button size="sm" onClick={handleSend} disabled={isLoading} className="h-7">
              <Send className="h-3 w-3 mr-1" /> Send
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Re-export types and components for convenience
export type { ChatMessage, Thread, ChatProps } from './types'