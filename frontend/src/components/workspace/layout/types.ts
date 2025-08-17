export type RailMode = 'workspace' | 'component-gallery' | 'devtools' | 'settings' | 'series' | 'articles' | 'projects'

export interface RailItem {
  id: RailMode
  label: string
  icon: React.ComponentType<{ className?: string }>
  shortcut?: string
  disabled?: boolean
}

export interface LeftRailProps {
  activeMode: RailMode
  onModeChange: (mode: RailMode) => void
  className?: string
}

// Panel configuration for activities
export interface PanelConfig {
  enabled: boolean
  defaultOpen: boolean
}

// Activity configuration - defines which panels are available for each activity
export interface ActivityConfiguration {
  leftPanel: PanelConfig
  rightPanel: PanelConfig
  bottomPanel: PanelConfig
}

// Panel states interface
export interface PanelStates {
  leftPanel: {
    isCollapsed: boolean
    toggle: () => void
    expand: () => void
    collapse: () => void
    onCollapse: () => void
    onExpand: () => void
    panelRef: React.RefObject<any>
  }
  rightPanel: {
    isCollapsed: boolean
    toggle: () => void
    expand: () => void
    collapse: () => void
    onCollapse: () => void
    onExpand: () => void
    panelRef: React.RefObject<any>
  }
  bottomPanel: {
    isCollapsed: boolean
    toggle: () => void
    expand: () => void
    collapse: () => void
    onCollapse: () => void
    onExpand: () => void
    panelRef: React.RefObject<any>
  }
}

export interface ActivityContainerProps {
  projectId: string
}

export interface WorkspaceLayoutProps {
  activityConfig: ActivityConfiguration
  panelStates: PanelStates
  railMode: RailMode
  projectId: string
}