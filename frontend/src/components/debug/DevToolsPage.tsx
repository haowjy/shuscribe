'use client'

import { useState } from 'react'
import { useUser } from '@/hooks/useUser'
import { useToastContext } from '@/components/providers/ToastProvider'
import { StorageStats } from './StorageStats'
import { DataManagement } from './DataManagement'
import { ImportExport } from './ImportExport'
import { ReferenceIndexDebug } from './ReferenceIndexDebug'
// ComponentGallery now accessed via dedicated route from the rail

interface DevToolsPageProps {
  onBackToProjects: () => void
}

export function DevToolsPage({ }: DevToolsPageProps) {
  const { user } = useUser()
  const { success, error } = useToastContext()
  const [statsRefreshTrigger, setStatsRefreshTrigger] = useState(0)

  const handleDebugSuccess = (successMessage: string) => {
    success(successMessage)
    // Trigger stats refresh
    setStatsRefreshTrigger(prev => prev + 1)
  }

  const handleDebugError = (errorMessage: string) => {
    error('Operation Failed', errorMessage)
  }

  return (
    <div className="min-h-full bg-background">
      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">

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