'use client'

import { useState, useEffect, ReactNode } from 'react'
import { usePathname } from 'next/navigation'
import { GlobalActivityRail } from './GlobalActivityRail'
import { SettingsModal } from '@/components/app/SettingsModal'
import { DevToolsPage } from '@/components/debug/DevToolsPage'
import { ComponentGallery } from '@/components/debug/ComponentGallery'

interface AppLayoutWithRailProps {
  children: ReactNode
}

export function AppLayoutWithRail({ children }: AppLayoutWithRailProps) {
  const pathname = usePathname()
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [currentView, setCurrentView] = useState<'projects' | 'devtools' | 'component-gallery'>('projects')
  
  // Determine if this is a projects route (now using ProjectsLayout instead of rail)
  const isProjectsRoute = pathname.startsWith('/projects')
  
  // Global keyboard shortcut for settings (⌘,) - only for non-projects routes
  useEffect(() => {
    if (isProjectsRoute) return // Don't add listener for projects routes

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.metaKey && event.key === ',') {
        event.preventDefault()
        setIsSettingsOpen(true)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isProjectsRoute])

  // Ensure routed pages always render in main area by exiting devtools view on navigation
  useEffect(() => {
    setCurrentView('projects')
  }, [pathname])

  // For projects routes, skip the rail entirely since ProjectsLayout handles the UI
  if (isProjectsRoute) {
    return <>{children}</>
  }

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

  const handleComponentGalleryClick = () => {
    setCurrentView('component-gallery')
  }

  // Non-projects app routes - show rail + content with proper spacing
  return (
    <div className="relative min-h-screen">
      <GlobalActivityRail 
        onSettingsOpen={() => setIsSettingsOpen(true)}
        onSearchFocus={handleSearchFocus}
        onHomeClick={handleHomeClick}
        onDevToolsClick={handleDevToolsClick}
        onComponentGalleryClick={handleComponentGalleryClick}
        currentView={currentView}
      />
      
      {/* Main content with left margin to account for rail on desktop, no margin on mobile (floating dock) */}
      <main className="md:ml-14">
        {currentView === 'projects' ? children : 
         currentView === 'devtools' ? (
          <DevToolsPage onBackToProjects={() => setCurrentView('projects')} />
         ) : currentView === 'component-gallery' ? (
          <ComponentGallery />
         ) : children}
      </main>

      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
    </div>
  )
}