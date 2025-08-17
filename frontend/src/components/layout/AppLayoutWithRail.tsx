'use client'

import { useState, useEffect, ReactNode } from 'react'
import { usePathname } from 'next/navigation'
import { GlobalActivityRail } from './GlobalActivityRail'
import { StudioContainer } from './StudioContainer'
import { SettingsModal } from '@/components/app/SettingsModal'
import { DevToolsPage } from '@/components/debug/DevToolsPage'
import { ComponentGallery } from '@/components/debug/ComponentGallery'

interface AppLayoutWithRailProps {
  children: ReactNode
}

export function AppLayoutWithRail({ children }: AppLayoutWithRailProps) {
  const pathname = usePathname()
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [currentView, setCurrentView] = useState<'studio' | 'devtools' | 'component-gallery'>('studio')
  
  // Determine if this is a studio route (now using StudioContainer)
  const isStudioRoute = pathname.startsWith('/studio')
  
  // Global keyboard shortcut for settings (⌘,) - only for non-studio routes 
  // (studio routes handle this in StudioContainer)
  useEffect(() => {
    if (isStudioRoute) return // Don't add listener for studio routes

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.metaKey && event.key === ',') {
        event.preventDefault()
        setIsSettingsOpen(true)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isStudioRoute])

  // Ensure routed pages always render in main area by exiting devtools view on navigation
  useEffect(() => {
    setCurrentView('studio')
  }, [pathname])

  // For studio routes, use StudioContainer with unified rail
  if (isStudioRoute) {
    return <StudioContainer>{children}</StudioContainer>
  }

  const handleSearchFocus = () => {
    // Only try to focus search if we're in studio view
    if (currentView === 'studio') {
      const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i]') as HTMLInputElement
      if (searchInput) {
        searchInput.focus()
      }
    }
  }

  const handleHomeClick = () => {
    setCurrentView('studio')
  }

  const handleDevToolsClick = () => {
    setCurrentView('devtools')
  }

  const handleComponentGalleryClick = () => {
    setCurrentView('component-gallery')
  }

  // Non-studio app routes - show rail + content with proper spacing
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
        {currentView === 'studio' ? children : 
         currentView === 'devtools' ? (
          <DevToolsPage onBackToProjects={() => setCurrentView('studio')} />
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