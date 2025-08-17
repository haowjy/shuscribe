'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { createLocalDataProvider } from '@/lib/data/local-provider'
import { buildReferenceIndex, searchReferenceIndex, type ReferenceIndexEntry } from '@/lib/localdb/reference-index'
import { Search, RefreshCw, Hash } from 'lucide-react'

interface ReferenceIndexDebugProps {
  userId?: string
  onSuccess?: (message: string) => void
  onError?: (error: string) => void
  className?: string
}

export function ReferenceIndexDebug({ 
  userId, 
  onSuccess, 
  onError, 
  className = '' 
}: ReferenceIndexDebugProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null)
  const [referenceIndex, setReferenceIndex] = useState<ReferenceIndexEntry[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<ReferenceIndexEntry[]>([])

  useEffect(() => {
    loadProjects()
  }, [userId]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (searchQuery && referenceIndex.length > 0) {
      const results = searchReferenceIndex(referenceIndex, searchQuery)
      setSearchResults(results)
    } else {
      setSearchResults([])
    }
  }, [searchQuery, referenceIndex])

  const loadProjects = async () => {
    if (!userId) return
    
    try {
      const provider = createLocalDataProvider(userId)
      const projects = await provider.getProjects()
      if (projects.length > 0) {
        setCurrentProjectId(projects[0].id)
        await refreshIndex(projects[0].id)
      }
    } catch (error) {
      console.error('Failed to load projects:', error)
    }
  }

  const refreshIndex = async (projectId?: string) => {
    const targetProjectId = projectId || currentProjectId
    if (!targetProjectId) return

    setIsLoading(true)
    try {
      const index = await buildReferenceIndex(targetProjectId)
      setReferenceIndex(index)
      if (onSuccess) {
        onSuccess(`Reference index refreshed with ${index.length} entries`)
      }
    } catch (error: unknown) {
      if (onError) {
        onError(`Error refreshing index: ${error instanceof Error ? error.message : 'Unknown error'}`)
      }
    } finally {
      setIsLoading(false)
    }
  }

  if (!currentProjectId) {
    return (
      <div className={`text-center py-6 text-muted-foreground text-sm ${className}`}>
        No projects available. Create a sample project to test the reference index.
      </div>
    )
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex justify-between items-center">
        <h3 className="font-semibold text-sm flex items-center gap-2">
          <Hash className="h-4 w-4" />
          Reference Index ({referenceIndex.length} entries)
        </h3>
        <Button
          onClick={() => refreshIndex()}
          disabled={isLoading}
          size="sm"
          variant="outline"
        >
          <RefreshCw className="h-3 w-3 mr-1" />
          Refresh
        </Button>
      </div>

      <div className="space-y-3">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 text-muted-foreground h-3 w-3" />
          <Input
            type="text"
            placeholder="Search references..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-7 text-xs h-8"
          />
        </div>

        {searchResults.length > 0 && (
          <div className="bg-muted/30 rounded-lg p-3 max-h-48 overflow-y-auto">
            <div className="text-xs font-medium mb-2 text-muted-foreground">
              Search Results ({searchResults.length}):
            </div>
            <div className="space-y-2">
              {searchResults.slice(0, 10).map((entry, index) => (
                <div key={index} className="bg-background p-2 rounded border text-xs">
                  <div className="font-medium flex items-center gap-2">
                    <span className={`inline-block w-8 text-xs px-1 py-0.5 rounded text-white ${
                      entry.type === 'file' ? 'bg-primary' :
                      entry.type === 'folder' ? 'bg-success' :
                      'bg-accent-foreground'
                    }`}>
                      {entry.type}
                    </span>
                    <span className="truncate">{entry.name}</span>
                  </div>
                  {entry.path && (
                    <div className="text-xs text-muted-foreground mt-1 truncate">
                      {entry.path}
                    </div>
                  )}
                  {entry.tags && entry.tags.length > 0 && (
                    <div className="flex gap-1 mt-1 flex-wrap">
                      {entry.tags.slice(0, 3).map(tag => (
                        <span key={tag} className="text-xs bg-muted px-1 rounded">
                          {tag}
                        </span>
                      ))}
                      {entry.tags.length > 3 && (
                        <span className="text-xs text-muted-foreground">
                          +{entry.tags.length - 3}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))}
              {searchResults.length > 10 && (
                <div className="text-xs text-muted-foreground text-center py-1">
                  Showing first 10 of {searchResults.length} results
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}