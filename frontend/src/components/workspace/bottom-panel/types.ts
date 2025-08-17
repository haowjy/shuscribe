export type BottomPanelTab = 'ai-tools' | 'links' | 'tags'

export interface BottomPanelProps {
  isCollapsed: boolean
  onToggle: () => void
  activeTab?: BottomPanelTab
  onTabChange?: (tab: BottomPanelTab) => void
  className?: string
}

export interface TabItem {
  id: BottomPanelTab
  label: string
  icon: React.ComponentType<{ className?: string }>
}

export interface DocumentLink {
  id: string
  target: string
  text: string
  type: 'character' | 'location' | 'item' | 'other'
}