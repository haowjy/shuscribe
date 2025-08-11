'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { useUser } from '@/hooks/useUser'
import { StorageStats } from './StorageStats'
import { DataManagement } from './DataManagement'
import { ImportExport } from './ImportExport'
import { ReferenceIndexDebug } from './ReferenceIndexDebug'
import { ChevronLeft, Database } from 'lucide-react'

interface DevToolsPageProps {
  onBackToProjects: () => void
}

export function DevToolsPage({ onBackToProjects }: DevToolsPageProps) {
  const { user } = useUser()
  const [message, setMessage] = useState('')
  const [statsRefreshTrigger, setStatsRefreshTrigger] = useState(0)

  const handleDebugSuccess = (successMessage: string) => {
    setMessage(successMessage)
    // Trigger stats refresh
    setStatsRefreshTrigger(prev => prev + 1)
    // Clear message after 3 seconds
    setTimeout(() => setMessage(''), 3000)
  }

  const handleDebugError = (errorMessage: string) => {
    setMessage(`Error: ${errorMessage}`)
    // Clear message after 5 seconds
    setTimeout(() => setMessage(''), 5000)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Header with breadcrumb */}
        <div className="flex items-center justify-start mb-8">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={onBackToProjects}
              className="flex items-center gap-2 text-muted-foreground hover:text-foreground"
            >
              <ChevronLeft className="h-4 w-4" />
              Projects
            </Button>
            <span className="text-muted-foreground">/</span>
            <div className="flex items-center gap-3">
              <Database className="h-5 w-5 text-muted-foreground" />
              <h1 className="text-2xl font-bold">Developer Tools</h1>
            </div>
          </div>
        </div>

        {/* Status Message */}
        {message && (
          <div className={`mb-6 p-3 rounded border text-sm ${
            message.startsWith('Error') 
              ? 'bg-destructive/10 text-destructive border-destructive/20' 
              : 'bg-muted border-border'
          }`}>
            {message}
          </div>
        )}

        {/* Content Grid */}
        <div className="max-w-6xl space-y-8">
          {/* Storage Stats - Full Width */}
          <div className="w-full">
            <StorageStats refreshTrigger={statsRefreshTrigger} />
          </div>

          {/* Data Management Tools - Two Column Grid */}
          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-6">
              <DataManagement 
                userId={user?.id}
                onSuccess={handleDebugSuccess}
                onError={handleDebugError}
              />
            </div>
            
            <div className="space-y-6">
              <ImportExport 
                onSuccess={handleDebugSuccess}
                onError={handleDebugError}
              />
            </div>
          </div>

          {/* Reference Index - Full Width */}
          <div className="w-full">
            <div className="border rounded-lg p-6">
              <ReferenceIndexDebug 
                userId={user?.id}
                onSuccess={handleDebugSuccess}
                onError={handleDebugError}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}