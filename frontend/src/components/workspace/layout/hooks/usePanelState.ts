import { useState, useRef, useCallback, useEffect } from 'react'
import type { ImperativePanelHandle } from 'react-resizable-panels'

export interface PanelState {
  isCollapsed: boolean
  panelRef: React.RefObject<ImperativePanelHandle | null>
  toggle: () => void
  expand: () => void
  collapse: () => void
  onCollapse: () => void
  onExpand: () => void
}

export function usePanelState(initialCollapsed: boolean = false): PanelState {
  const [isCollapsed, setIsCollapsed] = useState(initialCollapsed)
  const panelRef = useRef<ImperativePanelHandle>(null)

  // Automatically collapse panel on mount if it should start collapsed
  useEffect(() => {
    if (initialCollapsed && panelRef.current) {
      // Use a small delay to ensure the panel is mounted
      const timer = setTimeout(() => {
        if (panelRef.current) {
          panelRef.current.collapse()
        }
      }, 50)
      return () => clearTimeout(timer)
    }
  }, [initialCollapsed])

  const toggle = useCallback(() => {
    if (panelRef.current) {
      if (isCollapsed) {
        panelRef.current.expand()
      } else {
        panelRef.current.collapse()
      }
    }
  }, [isCollapsed])

  const expand = useCallback(() => {
    if (panelRef.current && isCollapsed) {
      panelRef.current.expand()
    }
  }, [isCollapsed])

  const collapse = useCallback(() => {
    if (panelRef.current && !isCollapsed) {
      panelRef.current.collapse()
    }
  }, [isCollapsed])

  const onCollapse = useCallback(() => {
    setIsCollapsed(true)
  }, [])

  const onExpand = useCallback(() => {
    setIsCollapsed(false)
  }, [])

  return {
    isCollapsed,
    panelRef,
    toggle,
    expand,
    collapse,
    onCollapse,
    onExpand
  }
}