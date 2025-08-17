import { useEffect } from 'react'

interface WorkspaceShortcuts {
  onToggleLeft?: () => void
  onToggleRight?: () => void
  onToggleBottom?: () => void
  onSettings?: () => void
}

export function useWorkspaceShortcuts({
  onToggleLeft,
  onToggleRight, 
  onToggleBottom,
  onSettings
}: WorkspaceShortcuts) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.metaKey || event.ctrlKey) {
        switch (event.key) {
          case 'b':
            event.preventDefault()
            onToggleLeft?.()
            break
          case 'j':
            event.preventDefault()
            onToggleBottom?.()
            break
          case '\\':
            event.preventDefault()
            onToggleRight?.()
            break
          case ',':
            event.preventDefault()
            onSettings?.()
            break
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [onToggleLeft, onToggleRight, onToggleBottom, onSettings])
}