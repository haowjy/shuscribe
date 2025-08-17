'use client'

import { useState, useEffect } from 'react'
import { getStorageStats } from '@/lib/localdb/admin'

interface StorageStatsProps {
  className?: string
  refreshTrigger?: number // Increment this to trigger a refresh
}

export function StorageStats({ className = '', refreshTrigger }: StorageStatsProps) {
  const [stats, setStats] = useState<{
    projects: number;
    documents: number;
    fileTree: number;
    tags: number;
    referenceIndex: number;
    meta: number;
  } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [refreshTrigger])

  const loadStats = async () => {
    try {
      setLoading(true)
      const storageStats = await getStorageStats()
      setStats(storageStats)
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className={`bg-muted/50 p-4 rounded-lg ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-muted rounded w-32 mb-2"></div>
          <div className="grid grid-cols-3 gap-4">
            <div className="h-12 bg-muted rounded"></div>
            <div className="h-12 bg-muted rounded"></div>
            <div className="h-12 bg-muted rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!stats) return null

  return (
    <div className={`bg-muted/50 p-4 rounded-lg ${className}`}>
      <h3 className="font-semibold mb-3 text-sm">Storage Statistics</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <div className="text-center">
          <div className="text-lg font-bold text-primary">{stats.projects}</div>
          <div className="text-xs text-muted-foreground">Projects</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-success">{stats.documents}</div>
          <div className="text-xs text-muted-foreground">Documents</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-accent-foreground">{stats.fileTree}</div>
          <div className="text-xs text-muted-foreground">File Tree</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-warning">{stats.tags}</div>
          <div className="text-xs text-muted-foreground">Tags</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-info">{stats.referenceIndex}</div>
          <div className="text-xs text-muted-foreground">Indexes</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-muted-foreground">{stats.meta}</div>
          <div className="text-xs text-muted-foreground">Meta</div>
        </div>
      </div>
    </div>
  )
}