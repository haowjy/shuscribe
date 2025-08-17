export interface Tab {
  id: string
  name: string
  hasUnsavedChanges: boolean
  path?: string
}

export interface EditorTabsProps {
  tabs: Tab[]
  activeTabId: string
  onTabSelect: (tabId: string) => void
  onTabClose: (tabId: string) => void
  onNewTab: () => void
  onReorderTabs?: (fromIndex: number, toIndex: number) => void
  onToggleRightSidebar?: () => void
  isRightSidebarCollapsed?: boolean
}