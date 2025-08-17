'use client'

import { useState, useEffect } from 'react'
import { StudioHeader } from './StudioHeader'
import { SettingsModal } from '@/components/app/SettingsModal'
import { DevToolsPage } from '@/components/debug/DevToolsPage'

interface StudioLayoutProps {
  children: React.ReactNode
  onSettingsOpen: () => void
}

export function StudioLayout({ children, onSettingsOpen }: StudioLayoutProps) {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [currentView, setCurrentView] = useState<'studio' | 'devtools'>('studio')

  // Global keyboard shortcut for settings (⌘,)
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.metaKey && event.key === ',') {
        event.preventDefault()
        setIsSettingsOpen(true)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  const handleSettingsClick = () => {
    setIsSettingsOpen(true)
    onSettingsOpen()
  }


  const handleDevToolsClick = () => {
    setCurrentView('devtools')
  }

  const handleBackToStudio = () => {
    setCurrentView('studio')
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <StudioHeader
        onSettingsClick={handleSettingsClick}
        onDevToolsClick={handleDevToolsClick}
        onBackToStudio={handleBackToStudio}
        currentView={currentView}
      />

      {/* Main Content */}
      <main className="flex-1">
        {currentView === 'studio' ? children : (
          <DevToolsPage onBackToProjects={handleBackToStudio} />
        )}
      </main>

      {/* Settings Modal */}
      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
    </div>
  )
}