/**
 * Document Data Hooks - localStorage-first with future API sync
 * 
 * WHY: Documents are the core content in ShuScribe. Writers need instant access
 * to their documents without network latency. These hooks provide zero-delay
 * document loading from Dexie while preparing for server synchronization.
 * 
 * Problem Context: Document editing requires instant responsiveness. Any delay
 * in loading or saving content breaks the creative flow. This architecture
 * ensures instant UI updates while preparing for robust server sync.
 * 
 * Architecture Pattern:
 * 1. Immediate response from Dexie cache
 * 2. TODO: Background server verification with conflict detection
 * 3. TODO: Operational transforms for collaborative editing
 * 4. Optimistic updates for seamless editing experience
 * 
 * Integration Points:
 * - Works with existing DocumentEditor components
 * - Integrates with file tree for navigation
 * - Supports @-reference system for cross-document links
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useUser } from '@/hooks/useUser'
import { createLocalDataProvider } from '@/lib/data/local-provider'
import type { Document } from '@/lib/localdb/types'

// Query keys for consistent cache management
export const documentKeys = {
  all: ['documents'] as const,
  lists: () => [...documentKeys.all, 'list'] as const,
  list: (projectId: string) => [...documentKeys.lists(), projectId] as const,
  details: () => [...documentKeys.all, 'detail'] as const,
  detail: (id: string) => [...documentKeys.details(), id] as const,
}

/**
 * Get all documents for a project from localStorage
 * Returns cached data immediately, prepares for server sync
 */
export function useDocuments(projectId: string) {
  const { userId } = useUser()
  
  return useQuery({
    queryKey: documentKeys.list(projectId),
    queryFn: async () => {
      if (!userId || !projectId) return []
      
      const provider = createLocalDataProvider(userId)
      const documents = await provider.getDocuments(projectId)
      
      // TODO: BACKGROUND SERVER VERIFICATION
      // When APIs are implemented:
      // 1. Return cached documents immediately (above)
      // 2. Background fetch from server: GET /api/projects/{projectId}/documents
      // 3. Compare document versions and timestamps
      // 4. Detect conflicts and queue for resolution
      // 5. Update cache with resolved data
      
      return documents
    },
    enabled: !!userId && !!projectId,
    staleTime: 5 * 60 * 1000, // 5 minutes - documents change frequently
  })
}

/**
 * Get individual document by ID from localStorage
 * Returns cached data immediately, prepares for server sync
 */
export function useDocument(documentId: string) {
  const { userId } = useUser()
  
  return useQuery({
    queryKey: documentKeys.detail(documentId),
    queryFn: async () => {
      if (!userId || !documentId) return null
      
      const provider = createLocalDataProvider(userId)
      const document = await provider.getDocument(documentId)
      
      // TODO: BACKGROUND SERVER VERIFICATION
      // When APIs are implemented:
      // 1. Return cached document immediately (above)
      // 2. Background fetch from server: GET /api/documents/{id}
      // 3. Compare document.version and document.updatedAt
      // 4. Handle content conflicts with operational transforms
      // 5. Implement three-way merge for collaborative editing
      
      return document
    },
    enabled: !!userId && !!documentId,
    staleTime: 2 * 60 * 1000, // 2 minutes - documents are actively edited
  })
}

/**
 * Create new document with optimistic update
 */
export function useCreateDocument() {
  const { userId } = useUser()
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (newDocument: Omit<Document, 'id' | 'createdAt' | 'updatedAt'>) => {
      if (!userId) throw new Error('User not authenticated')
      
      const provider = createLocalDataProvider(userId)
      const document = await provider.createDocument(newDocument)
      
      // TODO: SERVER SYNC
      // When APIs are implemented:
      // 1. Create in localStorage immediately (above)
      // 2. Queue for server sync: POST /api/projects/{projectId}/documents
      // 3. Handle server validation (path conflicts, etc.)
      // 4. Update local cache with server-assigned metadata
      
      return document
    },
    onSuccess: (newDocument) => {
      // Invalidate documents list for the project
      queryClient.invalidateQueries({ 
        queryKey: documentKeys.list(newDocument.projectId) 
      })
      
      // Add to cache for immediate access
      queryClient.setQueryData(documentKeys.detail(newDocument.id), newDocument)
      
      // Invalidate file tree since it includes document references
      queryClient.invalidateQueries({ queryKey: ['fileTree', newDocument.projectId] })
    },
    onError: (error) => {
      console.error('Failed to create document:', error)
      // TODO: Show user-friendly error message
    }
  })
}

/**
 * Update document with optimistic update and auto-save support
 */
export function useUpdateDocument(documentId: string) {
  const { userId } = useUser()
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (updates: Partial<Document>) => {
      if (!userId) throw new Error('User not authenticated')
      
      const provider = createLocalDataProvider(userId)
      const updatedDocument = await provider.updateDocument(documentId, updates)
      
      // TODO: SERVER SYNC WITH CONFLICT RESOLUTION
      // When APIs are implemented:
      // 1. Update localStorage immediately (above)
      // 2. Queue for server sync: PATCH /api/documents/{id}
      // 3. Implement operational transforms for concurrent edits
      // 4. Handle version conflicts with three-way merge
      // 5. Real-time collaboration with WebSocket updates
      
      return updatedDocument
    },
    onMutate: async (updates) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: documentKeys.detail(documentId) })
      
      // Snapshot previous value for rollback
      const previousDocument = queryClient.getQueryData<Document>(documentKeys.detail(documentId))
      
      // Optimistically update cache for instant UI feedback
      if (previousDocument) {
        queryClient.setQueryData(documentKeys.detail(documentId), {
          ...previousDocument,
          ...updates,
          updatedAt: new Date().toISOString()
        })
      }
      
      return { previousDocument }
    },
    onError: (error, updates, context) => {
      // Rollback optimistic update
      if (context?.previousDocument) {
        queryClient.setQueryData(documentKeys.detail(documentId), context.previousDocument)
      }
      console.error('Failed to update document:', error)
    },
    onSuccess: (updatedDocument) => {
      // Update cache with actual result
      queryClient.setQueryData(documentKeys.detail(documentId), updatedDocument)
      
      // Invalidate related queries
      queryClient.invalidateQueries({ 
        queryKey: documentKeys.list(updatedDocument.projectId) 
      })
    }
  })
}

/**
 * Delete document with optimistic update
 */
export function useDeleteDocument() {
  const { userId } = useUser()
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (documentId: string) => {
      if (!userId) throw new Error('User not authenticated')
      
      const provider = createLocalDataProvider(userId)
      await provider.deleteDocument(documentId)
      
      // TODO: SERVER SYNC
      // When APIs are implemented:
      // 1. Delete from localStorage immediately (above)
      // 2. Queue for server sync: DELETE /api/documents/{id}
      // 3. Handle cascade operations (file tree cleanup)
      // 4. Update reference index for @-mentions
      
      return documentId
    },
    onMutate: async (documentId) => {
      // Get document info before deletion for cleanup
      const document = queryClient.getQueryData<Document>(documentKeys.detail(documentId))
      
      if (document) {
        // Cancel outgoing refetches
        await queryClient.cancelQueries({ queryKey: documentKeys.all })
        
        // Remove from documents list cache
        const previousDocuments = queryClient.getQueryData<Document[]>(
          documentKeys.list(document.projectId)
        )
        if (previousDocuments) {
          queryClient.setQueryData(
            documentKeys.list(document.projectId),
            previousDocuments.filter(d => d.id !== documentId)
          )
        }
        
        // Remove individual document cache
        queryClient.removeQueries({ queryKey: documentKeys.detail(documentId) })
        
        return { document, previousDocuments }
      }
      
      return {}
    },
    onError: (error, documentId, context) => {
      // Rollback optimistic update
      if (context?.document && context?.previousDocuments) {
        queryClient.setQueryData(
          documentKeys.list(context.document.projectId),
          context.previousDocuments
        )
      }
      console.error('Failed to delete document:', error)
    },
    onSuccess: (documentId, variables, context) => {
      if (context?.document) {
        // Invalidate related queries
        queryClient.invalidateQueries({ 
          queryKey: documentKeys.list(context.document.projectId) 
        })
        queryClient.invalidateQueries({ 
          queryKey: ['fileTree', context.document.projectId] 
        })
      }
    }
  })
}

/*
 * TODO: ADVANCED DOCUMENT FEATURES FOR API INTEGRATION
 * 
 * When backend APIs are ready, these hooks will support:
 * 
 * 1. COLLABORATIVE EDITING:
 *    - Real-time operational transforms
 *    - Conflict-free replicated data types (CRDTs)
 *    - Live cursor positions and selections
 *    - User presence indicators
 * 
 * 2. VERSION CONTROL:
 *    - Document revision history
 *    - Branch and merge operations
 *    - Diff visualization for changes
 *    - Rollback to previous versions
 * 
 * 3. AUTO-SAVE OPTIMIZATION:
 *    - Debounced saves to prevent API spam
 *    - Delta compression for large documents
 *    - Conflict detection during save
 *    - Recovery from failed saves
 * 
 * 4. CROSS-DOCUMENT FEATURES:
 *    - @-reference validation and updates
 *    - Dependency tracking between documents
 *    - Bulk operations (rename, move, etc.)
 *    - Search across document content
 * 
 * 5. PERFORMANCE OPTIMIZATIONS:
 *    - Lazy loading for large documents
 *    - Partial content loading
 *    - Background prefetching
 *    - Memory management for editor state
 */