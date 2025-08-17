export type Role = 'user' | 'assistant'

export interface ChatMessage {
  id: string
  role: Role
  content: string
}

export interface Thread {
  id: string
  title: string
  messages: ChatMessage[]
}

export interface ChatProps {
  thread: Thread | null
  onUpdateMessages: (messages: ChatMessage[]) => void
  onNewThread: () => void
}