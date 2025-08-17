'use client'

import { useState, useEffect } from 'react'
import { ProjectsHeader } from './ProjectsHeader'
import { SettingsModal } from '@/components/app/SettingsModal'
import { DevToolsPage } from '@/components/debug/DevToolsPage'

interface ProjectsLayoutProps {
  children: React.ReactNode
  onSettingsOpen: () => void
}

export function ProjectsLayout({ children, onSettingsOpen }: ProjectsLayoutProps) {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [currentView, setCurrentView] = useState<'projects' | 'devtools'>('projects')

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

  const handleBackToProjects = () => {
    setCurrentView('projects')
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <ProjectsHeader
        onSettingsClick={handleSettingsClick}
        onDevToolsClick={handleDevToolsClick}
        onBackToProjects={handleBackToProjects}
        currentView={currentView}
      />

      {/* Main Content */}
      <main className="flex-1">
        {currentView === 'projects' ? children : (
          <DevToolsPage onBackToProjects={handleBackToProjects} />
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