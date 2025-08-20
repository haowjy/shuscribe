/**
 * File Tree Hook - Real Dexie Data Integration
 * 
 * WHY: This hook now provides real file tree data from Dexie instead of mock data.
 * It bridges the gap between the workspace explorer UI and the localStorage-first
 * data architecture, enabling instant file tree operations.
 * 
 * Migration Note: This replaces the previous mock data with actual project data
 * from the local database while maintaining the same interface for components.
 * 
 * Integration Points:
 * - Uses data hooks for real-time file tree updates
 * - Maintains compatibility with existing FileTreeView components
 * - Supports both FileTreeItem (data) and FileNode (UI) type systems
 */

import { useMemo } from 'react'
import { useFileTree as useFileTreeData } from '@/hooks/data'
import type { FileNode } from '../types'
import type { FileTreeItem } from '@/lib/localdb/types'

// Extended type for hierarchical tree structure (matches data hook)
type FileTreeItemWithChildren = FileTreeItem & {
  children?: FileTreeItemWithChildren[]
}

// Helper function to convert FileTreeItem to FileNode for UI compatibility
function convertToFileNode(item: FileTreeItemWithChildren): FileNode {
  return {
    id: item.id,
    name: item.name,
    type: item.type,
    tags: item.tags,
    // TODO: Determine hasUnsavedChanges from document state
    hasUnsavedChanges: false,
    children: item.children ? item.children.map(convertToFileNode) : undefined,
    collapsed: item.collapsed,
    documentId: item.documentId // Preserve document ID for proper content loading
  }
}

export function useFileTree(projectId?: string) {
  // Get real file tree data from Dexie via TanStack Query
  const { 
    data: fileTreeData = [], 
    isLoading,
    error 
  } = useFileTreeData(projectId || '')

  // Convert data format for UI compatibility
  const fileTree = useMemo(() => {
    console.log('🌲 useFileTree: Processing data', { 
      projectId, 
      hasProjectId: !!projectId, 
      fileTreeDataLength: fileTreeData.length,
      isLoading,
      willUseMockData: !projectId || !fileTreeData.length
    })
    
    if (!projectId || !fileTreeData.length) {
      // Return mock data for development when no project is selected
      console.log('🎭 useFileTree: Using mock data')
      return getMockFileTree()
    }
    
    console.log('💾 useFileTree: Using real data')
    return fileTreeData.map(convertToFileNode)
  }, [fileTreeData, projectId, isLoading])

  return {
    data: fileTree,
    isLoading,
    error
  }
}

// Fallback mock data for development and component gallery
function getMockFileTree(): FileNode[] {
  return [
    {
      id: 'characters',
      name: 'characters',
      type: 'folder',
      children: [
        {
          id: 'protagonists',
          name: 'protagonists',
          type: 'folder',
          children: [
            {
              id: 'elara',
              name: 'elara.md',
              type: 'file',
              tags: ['fire-magic'],
              hasUnsavedChanges: true
            },
            {
              id: 'thomas',
              name: 'thomas.md',
              type: 'file',
              tags: ['mentor']
            }
          ]
        },
        {
          id: 'antagonists',
          name: 'antagonists',
          type: 'folder',
          children: [
            {
              id: 'shadow-lord',
              name: 'shadow-lord.md',
              type: 'file',
              tags: ['dark-magic', 'final-boss']
            }
          ]
        }
      ]
    },
    {
      id: 'world',
      name: 'world',
      type: 'folder',
      children: [
        {
          id: 'locations',
          name: 'locations',
          type: 'folder',
          children: [
            {
              id: 'thornfield-manor',
              name: 'thornfield-manor.md',
              type: 'file',
              tags: ['gothic', 'mysterious']
            }
          ]
        }
      ]
    },
    {
      id: 'documents',
      name: 'documents',
      type: 'folder',
      children: [
        {
          id: 'chapter-01',
          name: 'chapter-01.md',
          type: 'file',
          hasUnsavedChanges: true
        },
        {
          id: 'outline',
          name: 'outline.md',
          type: 'file'
        }
      ]
    }
  ]
}

/*
 * TODO: ENHANCED FILE TREE INTEGRATION
 * 
 * When components are fully migrated to use real data:
 * 
 * 1. REMOVE MOCK DATA FALLBACK:
 *    - Remove getMockFileTree() once all components provide projectId
 *    - Add proper error handling for missing projects
 *    - Implement loading states in UI components
 * 
 * 2. UNSAVED CHANGES DETECTION:
 *    - Integrate with document editor state
 *    - Track pending mutations in TanStack Query
 *    - Show visual indicators for modified files
 * 
 * 3. REAL-TIME UPDATES:
 *    - Listen for file tree mutations from other components
 *    - Auto-refresh when documents are created/deleted
 *    - Handle concurrent file operations gracefully
 * 
 * 4. PERFORMANCE OPTIMIZATIONS:
 *    - Implement virtual scrolling for large trees
 *    - Lazy load deeply nested folders
 *    - Cache expanded/collapsed states per project
 */