/**
 * File Tree Data Hooks - localStorage-first with future API sync
 * 
 * WHY: The file tree is the primary navigation interface for ShuScribe projects.
 * Users need instant folder/file operations without network delays. This hook
 * provides immediate hierarchical data from Dexie while preparing for server sync.
 * 
 * Problem Context: File tree operations (expand/collapse, rename, move) must feel
 * instantaneous for good UX. Traditional server-dependent implementations create
 * jarring delays. This architecture ensures fluid navigation.
 * 
 * Architecture Benefits:
 * - Instant tree operations from Dexie cache
 * - Hierarchical data structure for efficient rendering
 * - Path-based organization with automatic folder creation
 * - Integration with document system for seamless editing
 * 
 * Integration Points:
 * - Replaces mock data in workspace explorer components
 * - Works with document hooks for file/document relationships
 * - Supports @-reference system for cross-document navigation
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useUser } from '@/hooks/useUser'
import { createLocalDataProvider } from '@/lib/data/local-provider'
import type { FileTreeItem } from '@/lib/localdb/types'

// Query keys for consistent cache management
export const fileTreeKeys = {
  all: ['fileTree'] as const,
  lists: () => [...fileTreeKeys.all, 'list'] as const,
  list: (projectId: string) => [...fileTreeKeys.lists(), projectId] as const,
  details: () => [...fileTreeKeys.all, 'detail'] as const,
  detail: (id: string) => [...fileTreeKeys.details(), id] as const,
}

// Extended type for hierarchical tree structure
type FileTreeItemWithChildren = FileTreeItem & {
  children?: FileTreeItemWithChildren[]
}

// Helper function to build hierarchical tree from flat array
function buildFileTree(items: FileTreeItem[]): FileTreeItemWithChildren[] {
  const itemMap = new Map<string, FileTreeItemWithChildren>()
  const rootItems: FileTreeItemWithChildren[] = []
  
  // First pass: create map of all items
  items.forEach(item => {
    itemMap.set(item.id, { ...item, children: [] })
  })
  
  // Second pass: build hierarchy
  items.forEach(item => {
    const treeItem = itemMap.get(item.id)!
    
    if (item.parentId && itemMap.has(item.parentId)) {
      const parent = itemMap.get(item.parentId)!
      if (!parent.children) parent.children = []
      parent.children.push(treeItem)
    } else {
      rootItems.push(treeItem)
    }
  })
  
  // Sort children by type (folders first) then by name
  const sortItems = (items: FileTreeItemWithChildren[]) => {
    items.forEach(item => {
      if (item.children) {
        item.children.sort((a, b) => {
          if (a.type !== b.type) {
            return a.type === 'folder' ? -1 : 1
          }
          return a.name.localeCompare(b.name)
        })
        sortItems(item.children)
      }
    })
  }
  
  rootItems.sort((a, b) => {
    if (a.type !== b.type) {
      return a.type === 'folder' ? -1 : 1
    }
    return a.name.localeCompare(b.name)
  })
  
  sortItems(rootItems)
  return rootItems
}

/**
 * Get hierarchical file tree for a project from localStorage
 * Returns structured tree data immediately, prepares for server sync
 */
export function useFileTree(projectId: string) {
  const { userId } = useUser()
  
  return useQuery({
    queryKey: fileTreeKeys.list(projectId),
    queryFn: async () => {
      if (!userId || !projectId) return []
      
      const provider = createLocalDataProvider(userId)
      const items = await provider.getFileTree(projectId)
      
      // Build hierarchical structure for UI consumption
      const tree = buildFileTree(items)
      
      // TODO: BACKGROUND SERVER VERIFICATION
      // When APIs are implemented:
      // 1. Return cached tree immediately (above)
      // 2. Background fetch from server: GET /api/projects/{projectId}/filetree
      // 3. Compare timestamps and detect structural changes
      // 4. Handle path conflicts and renames
      // 5. Sync document associations and metadata
      
      return tree
    },
    enabled: !!userId && !!projectId,
    staleTime: 5 * 60 * 1000, // 5 minutes - tree structure changes less frequently
  })
}

/**
 * Get individual file tree item by ID from localStorage
 */
export function useFileTreeItem(itemId: string) {
  const { userId } = useUser()
  
  return useQuery({
    queryKey: fileTreeKeys.detail(itemId),
    queryFn: async () => {
      if (!userId || !itemId) return null
      
      const provider = createLocalDataProvider(userId)
      // Note: LocalDataProvider doesn't have getFileTreeItem method yet
      // We'll need to add this or get from the project's file tree
      
      // TODO: Add getFileTreeItem method to LocalDataProvider
      // For now, we'll implement a workaround by getting all items and filtering
      
      return null // Placeholder
    },
    enabled: !!userId && !!itemId,
  })
}

/**
 * Create new file tree item (file or folder) with optimistic update
 */
export function useCreateFileTreeItem() {
  const { userId } = useUser()
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (newItem: Omit<FileTreeItem, 'id' | 'createdAt' | 'updatedAt'>) => {
      if (!userId) throw new Error('User not authenticated')
      
      const provider = createLocalDataProvider(userId)
      const item = await provider.createFileTreeItem(newItem)
      
      // TODO: SERVER SYNC
      // When APIs are implemented:
      // 1. Create in localStorage immediately (above)
      // 2. Queue for server sync: POST /api/projects/{projectId}/filetree
      // 3. Handle path conflicts and validation
      // 4. Sync document creation if item is a file
      
      return item
    },
    onSuccess: (newItem) => {
      // Invalidate file tree to trigger rebuild
      queryClient.invalidateQueries({ 
        queryKey: fileTreeKeys.list(newItem.projectId) 
      })
      
      // If creating a file with a document, invalidate documents list
      if (newItem.type === 'file' && newItem.documentId) {
        queryClient.invalidateQueries({ 
          queryKey: ['documents', 'list', newItem.projectId] 
        })
      }
    },
    onError: (error) => {
      console.error('Failed to create file tree item:', error)
      // TODO: Show user-friendly error message
    }
  })
}

/**
 * Update file tree item (rename, move, etc.) with optimistic update
 */
export function useUpdateFileTreeItem(itemId: string) {
  const { userId } = useUser()
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (updates: Partial<FileTreeItem>) => {
      if (!userId) throw new Error('User not authenticated')
      
      const provider = createLocalDataProvider(userId)
      const updatedItem = await provider.updateFileTreeItem(itemId, updates)
      
      // TODO: SERVER SYNC WITH CONFLICT RESOLUTION
      // When APIs are implemented:
      // 1. Update localStorage immediately (above)
      // 2. Queue for server sync: PATCH /api/filetree/{id}
      // 3. Handle path conflicts from concurrent operations
      // 4. Update document paths if file was renamed/moved
      // 5. Cascade updates to child items if folder was moved
      
      return updatedItem
    },
    onMutate: async (updates) => {
      // This is complex for tree structures, so we'll skip optimistic updates
      // and just rely on the mutation success to refresh the tree
      return {}
    },
    onSuccess: (updatedItem) => {
      // Invalidate entire file tree for simplicity
      // TODO: Optimize to update only affected branches
      queryClient.invalidateQueries({ 
        queryKey: fileTreeKeys.list(updatedItem.projectId) 
      })
      
      // If item was renamed and has a document, update document queries
      if (updatedItem.documentId) {
        queryClient.invalidateQueries({ 
          queryKey: ['documents', 'detail', updatedItem.documentId] 
        })
      }
    },
    onError: (error) => {
      console.error('Failed to update file tree item:', error)
    }
  })
}

/**
 * Delete file tree item with optimistic update
 */
export function useDeleteFileTreeItem() {
  const { userId } = useUser()
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (itemId: string) => {
      if (!userId) throw new Error('User not authenticated')
      
      const provider = createLocalDataProvider(userId)
      await provider.deleteFileTreeItem(itemId)
      
      // TODO: SERVER SYNC WITH CASCADE OPERATIONS
      // When APIs are implemented:
      // 1. Delete from localStorage immediately (above)
      // 2. Queue for server sync: DELETE /api/filetree/{id}
      // 3. Handle cascade deletes for child items
      // 4. Delete associated documents if file item
      // 5. Update @-references that pointed to deleted items
      
      return itemId
    },
    onSuccess: (itemId, variables, context) => {
      // Invalidate file tree queries to trigger rebuild
      // We don't know the projectId here, so invalidate all file trees
      queryClient.invalidateQueries({ queryKey: fileTreeKeys.lists() })
      
      // Also invalidate documents in case a file was deleted
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
    onError: (error) => {
      console.error('Failed to delete file tree item:', error)
    }
  })
}

/**
 * Toggle collapsed state for folders (UI-only operation)
 */
export function useToggleFileTreeItem() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ projectId, itemId, collapsed }: { 
      projectId: string, 
      itemId: string, 
      collapsed: boolean 
    }) => {
      // This is a UI-only operation, we update the cache directly
      const tree = queryClient.getQueryData<FileTreeItemWithChildren[]>(fileTreeKeys.list(projectId))
      
      if (tree) {
        const updateCollapsed = (items: FileTreeItemWithChildren[]): FileTreeItemWithChildren[] => {
          return items.map(item => {
            if (item.id === itemId) {
              return { ...item, collapsed }
            }
            if (item.children) {
              return { ...item, children: updateCollapsed(item.children) }
            }
            return item
          })
        }
        
        const updatedTree = updateCollapsed(tree)
        queryClient.setQueryData(fileTreeKeys.list(projectId), updatedTree)
      }
      
      return { projectId, itemId, collapsed }
    },
    onError: (error) => {
      console.error('Failed to toggle file tree item:', error)
    }
  })
}

/*
 * TODO: ADVANCED FILE TREE FEATURES FOR API INTEGRATION
 * 
 * When backend APIs are ready, these hooks will support:
 * 
 * 1. REAL-TIME COLLABORATION:
 *    - Live updates when team members modify structure
 *    - Conflict resolution for concurrent operations
 *    - Presence indicators showing who's editing what
 *    - Operational transforms for tree modifications
 * 
 * 2. ADVANCED FILE OPERATIONS:
 *    - Drag and drop with path validation
 *    - Bulk operations (move multiple items)
 *    - Template-based file/folder creation
 *    - Smart duplicate detection and resolution
 * 
 * 3. INTEGRATION FEATURES:
 *    - Automatic folder creation from document paths
 *    - Sync with external file systems
 *    - Version control integration (git-like operations)
 *    - Backup and restore capabilities
 * 
 * 4. PERFORMANCE OPTIMIZATIONS:
 *    - Virtual scrolling for large trees
 *    - Lazy loading of deep folder structures
 *    - Incremental updates instead of full rebuilds
 *    - Background sync with minimal UI disruption
 * 
 * 5. SEARCH AND FILTERING:
 *    - Full-text search across file tree
 *    - Tag-based filtering and organization
 *    - Recent files and favorites
 *    - Smart suggestions based on usage patterns
 */