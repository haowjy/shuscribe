'use client'

import { useMemo, useState, useCallback } from 'react'
import { Bot } from 'lucide-react'
import { SidebarContainer } from '@/components/workspace/shared/SidebarContainer'
import { AIChat } from '@/components/chat/AIChat'
import type { ChatMessage, Thread } from '@/components/chat/types'

export function RightSidebar({ onHide }: { onHide?: () => void }) {
  const [threads, setThreads] = useState<Thread[]>(() => [{ id: crypto.randomUUID(), title: 'Chat 1', messages: [] }])
  const [activeId, setActiveId] = useState<string | null>(() => threads[0]?.id ?? null)

  const activeThread = useMemo(() => threads.find((t) => t.id === activeId) ?? null, [threads, activeId])

  const newThread = () => {
    setThreads((prev) => {
      const t: Thread = { id: crypto.randomUUID(), title: `Chat ${prev.length + 1}`, messages: [] }
      setActiveId(t.id)
      return [t, ...prev]
    })
  }

  const updateMessages = useCallback((msgs: ChatMessage[]) => {
    if (!activeId) return
    setThreads((prev) => prev.map((t) => (t.id === activeId ? { ...t, messages: msgs } : t)))
  }, [activeId])

  return (
    <SidebarContainer
      mode="simple"
      title="AI Assistant"
      titleIcon={Bot}
      side="right"
      onToggle={onHide}
    >
      <AIChat
        key={activeThread?.id || 'no-thread'}
        thread={activeThread}
        onUpdateMessages={updateMessages}
        onNewThread={newThread}
      />
    </SidebarContainer>
  )
}