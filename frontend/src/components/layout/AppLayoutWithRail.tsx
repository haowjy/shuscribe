'use client'

import { useState, useEffect, ReactNode } from 'react'
import { usePathname } from 'next/navigation'
import { GlobalActivityRail } from './GlobalActivityRail'
import { SettingsModal } from '@/components/app/SettingsModal'
import { DevToolsPage } from '@/components/debug/DevToolsPage'

interface AppLayoutWithRailProps {
  children: ReactNode
}

export function AppLayoutWithRail({ children }: AppLayoutWithRailProps) {
  const pathname = usePathname()
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [currentView, setCurrentView] = useState<'projects' | 'devtools'>('projects')
  
  // Determine if this is an app route that should show the rail
  const isAppRoute = pathname.startsWith('/projects')
  
  // Global keyboard shortcut for settings (⌘,)
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.metaKey && event.key === ',' && isAppRoute) {
        event.preventDefault()
        setIsSettingsOpen(true)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isAppRoute])

  const handleSearchFocus = () => {
    // Only try to focus search if we're in projects view
    if (currentView === 'projects') {
      const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i]') as HTMLInputElement
      if (searchInput) {
        searchInput.focus()
      }
    }
  }

  const handleHomeClick = () => {
    setCurrentView('projects')
  }

  const handleDevToolsClick = () => {
    setCurrentView('devtools')
  }

  if (!isAppRoute) {
    // Non-app routes (landing, etc.) - no rail
    return <>{children}</>
  }

  // App routes - show rail + content with proper spacing
  return (
    <div className="relative min-h-screen">
      <GlobalActivityRail 
        onSettingsOpen={() => setIsSettingsOpen(true)}
        onSearchFocus={handleSearchFocus}
        onHomeClick={handleHomeClick}
        onDevToolsClick={handleDevToolsClick}
        currentView={currentView}
      />
      
      {/* Main content with left margin to account for rail on desktop, no margin on mobile (floating dock) */}
      <main className="md:ml-14">
        {currentView === 'projects' ? children : (
          <DevToolsPage onBackToProjects={() => setCurrentView('projects')} />
        )}
      </main>

      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
    </div>
  )
}