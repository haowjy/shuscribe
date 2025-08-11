'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { exportAllData, importAllData } from '@/lib/localdb/admin'
import { Download, Upload } from 'lucide-react'

interface ImportExportProps {
  onSuccess?: (message: string) => void
  onError?: (error: string) => void
  className?: string
}

export function ImportExport({ 
  onSuccess, 
  onError, 
  className = '' 
}: ImportExportProps) {
  const [isLoading, setIsLoading] = useState(false)

  const handleAction = async (action: () => Promise<void>, successMessage: string) => {
    setIsLoading(true)
    try {
      await action()
      if (onSuccess) {
        onSuccess(successMessage)
      }
    } catch (error: unknown) {
      if (onError) {
        onError(error instanceof Error ? error.message : 'Unknown error')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      await handleAction(
        () => importAllData(file),
        'Data imported successfully'
      )
      // Clear the file input
      e.target.value = ''
    }
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <h3 className="font-semibold mb-3 text-sm flex items-center gap-2">
        <Upload className="h-4 w-4" />
        Import/Export
      </h3>
      
      <div className="space-y-2">
        <Button
          onClick={() => handleAction(exportAllData, 'Data exported to file')}
          disabled={isLoading}
          size="sm"
          variant="outline"
          className="w-full justify-start"
        >
          <Download className="h-3 w-3 mr-2" />
          Export Data (JSON)
        </Button>
        
        <div className="space-y-1">
          <label className="text-xs font-medium text-muted-foreground">
            Import Data:
          </label>
          <Input
            type="file"
            accept=".json"
            onChange={handleFileImport}
            disabled={isLoading}
            className="text-xs h-8"
          />
        </div>
      </div>
    </div>
  )
}