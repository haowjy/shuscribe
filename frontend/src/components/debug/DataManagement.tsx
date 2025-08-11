'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { clearAllLocalData } from '@/lib/localdb/admin'
import { seedSampleProject, seedLargeDemo } from '@/lib/localdb/seeds'
import { Trash2, Plus, Database } from 'lucide-react'

interface DataManagementProps {
  userId?: string
  onSuccess?: (message: string, projectId?: string) => void
  onError?: (error: string) => void
  className?: string
}

export function DataManagement({ 
  userId, 
  onSuccess, 
  onError, 
  className = '' 
}: DataManagementProps) {
  const [isLoading, setIsLoading] = useState(false)

  const handleAction = async (
    action: () => Promise<void | string>, 
    successMessage: string
  ) => {
    setIsLoading(true)
    try {
      const result = await action()
      if (onSuccess) {
        onSuccess(successMessage, typeof result === 'string' ? result : undefined)
      }
    } catch (error: unknown) {
      if (onError) {
        onError(error instanceof Error ? error.message : 'Unknown error')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearData = () => {
    if (confirm('Are you sure you want to clear all local data? This cannot be undone.')) {
      handleAction(clearAllLocalData, 'All data cleared')
    }
  }

  const handleSeedSample = () => {
    handleAction(() => seedSampleProject(userId), 'Sample project created')
  }

  const handleSeedLarge = () => {
    handleAction(() => seedLargeDemo(userId), 'Large demo created')
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <h3 className="font-semibold mb-3 text-sm flex items-center gap-2">
        <Database className="h-4 w-4" />
        Data Management
      </h3>
      
      <div className="space-y-2">
        <Button
          onClick={handleSeedSample}
          disabled={isLoading}
          size="sm"
          className="w-full justify-start"
          variant="outline"
        >
          <Plus className="h-3 w-3 mr-2" />
          Create Sample Project
        </Button>
        
        <Button
          onClick={handleSeedLarge}
          disabled={isLoading}
          size="sm"
          className="w-full justify-start"
          variant="outline"
        >
          <Plus className="h-3 w-3 mr-2" />
          Create Large Demo
        </Button>
        
        <Button
          onClick={handleClearData}
          disabled={isLoading}
          size="sm"
          variant="destructive"
          className="w-full justify-start"
        >
          <Trash2 className="h-3 w-3 mr-2" />
          Clear All Data
        </Button>
      </div>
    </div>
  )
}