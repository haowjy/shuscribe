import { useState, useEffect } from 'react'
import type { ChatMessage, Thread } from '../types'

export function useChat(thread: Thread | null, onUpdateMessages: (messages: ChatMessage[]) => void) {
  const [messages, setMessages] = useState<ChatMessage[]>(thread?.messages || [])
  const [isLoading, setIsLoading] = useState(false)

  // Sync with thread changes
  useEffect(() => {
    setMessages(thread?.messages || [])
  }, [thread?.id])

  // Sync messages with parent component when they change
  useEffect(() => {
    if (thread && JSON.stringify(messages) !== JSON.stringify(thread.messages)) {
      onUpdateMessages(messages)
    }
  }, [messages, onUpdateMessages, thread?.messages])

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return

    const userMsg: ChatMessage = { 
      id: crypto.randomUUID(), 
      role: 'user', 
      content 
    }
    
    setMessages(prev => [...prev, userMsg])
    setIsLoading(true)

    // Mock AI response
    setTimeout(() => {
      setMessages(prev => {
        const text = htmlToText(content)
        const replyHtml = textToHtmlParagraph(`You said:\n\n${text}\n\n(Mock) Here's a helpful response.`)
        
        // Replace last assistant message if exists, else append
        const lastIndex = [...prev].reverse().findIndex(m => m.role === 'assistant')
        if (lastIndex === -1) {
          const assistantMsg: ChatMessage = { 
            id: crypto.randomUUID(), 
            role: 'assistant', 
            content: replyHtml 
          }
          return [...prev, assistantMsg]
        }
        
        const indexFromStart = prev.length - 1 - lastIndex
        const next = [...prev]
        next[indexFromStart] = { ...next[indexFromStart], content: replyHtml }
        return next
      })
      setIsLoading(false)
    }, 700)
  }

  const updateMessage = (messageId: string, content: string) => {
    setMessages(prev => 
      prev.map(m => m.id === messageId ? { ...m, content } : m)
    )
  }

  const regenerateLastAssistantMessage = () => {
    setIsLoading(true)
    setTimeout(() => {
      setMessages(prev => {
        const lastAssistantIndex = [...prev].reverse().findIndex(msg => msg.role === 'assistant')
        if (lastAssistantIndex === -1) return prev
        
        const idx = prev.length - 1 - lastAssistantIndex
        const next = [...prev]
        const replacedHtml = textToHtmlParagraph(
          htmlToText(next[idx].content).replace(/^/, '(Regenerated) ')
        )
        next[idx] = { ...next[idx], content: replacedHtml }
        return next
      })
      setIsLoading(false)
    }, 500)
  }

  return {
    messages,
    isLoading,
    sendMessage,
    updateMessage,
    regenerateLastAssistantMessage
  }
}

// Utility functions
function htmlToText(html: string): string {
  if (typeof window === 'undefined') return html
  const div = document.createElement('div')
  div.innerHTML = html
  return (div.textContent || div.innerText || '').trim()
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

function textToHtmlParagraph(text: string): string {
  const safe = escapeHtml(text)
  const lines = safe.split(/\n+/).map(line => line.length ? `<p>${line}</p>` : '')
  return lines.join('') || '<p></p>'
}