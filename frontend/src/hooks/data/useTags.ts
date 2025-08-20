/**
 * Tag Management Hooks - localStorage-first with future API sync
 * 
 * WHY: Tags are essential for organizing content in ShuScribe. Writers need
 * instant tag operations (create, assign, filter) without network delays.
 * This hook provides immediate tag management from Dexie while preparing
 * for server sync and collaborative tagging.
 * 
 * Problem Context: Content organization requires fluid tagging operations.
 * Any delay in creating tags or applying them to content disrupts the
 * creative workflow. This architecture ensures instant tag responsiveness.
 * 
 * Architecture Benefits:
 * - Instant tag creation and assignment from Dexie cache
 * - Support for both project-specific and global tags
 * - Usage count tracking for tag popularity
 * - System tag support for built-in functionality
 * 
 * Integration Points:
 * - Works with document and file tree systems for content tagging
 * - Supports tag-based filtering and search
 * - Integrates with @-reference system for tag mentions
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useUser } from '@/hooks/useUser'
import { createLocalDataProvider } from '@/lib/data/local-provider'
import type { Tag } from '@/lib/localdb/types'

// Query keys for consistent cache management
export const tagKeys = {
  all: ['tags'] as const,
  lists: () => [...tagKeys.all, 'list'] as const,
  list: (projectId: string) => [...tagKeys.lists(), projectId] as const,
  global: () => [...tagKeys.all, 'global'] as const,
  details: () => [...tagKeys.all, 'detail'] as const,
  detail: (id: string) => [...tagKeys.details(), id] as const,
}

/**
 * Get all tags for a project from localStorage
 * Returns cached data immediately, prepares for server sync
 */
export function useTags(projectId: string) {
  const { userId } = useUser()
  
  return useQuery({
    queryKey: tagKeys.list(projectId),
    queryFn: async () => {
      if (!userId || !projectId) return []
      
      const provider = createLocalDataProvider(userId)
      const tags = await provider.getTags(projectId)
      
      // TODO: BACKGROUND SERVER VERIFICATION
      // When APIs are implemented:
      // 1. Return cached tags immediately (above)
      // 2. Background fetch from server: GET /api/projects/{projectId}/tags
      // 3. Compare usage counts and metadata
      // 4. Sync tag assignments across documents
      // 5. Handle tag merges and renames from other users
      
      return tags
    },
    enabled: !!userId && !!projectId,
    staleTime: 10 * 60 * 1000, // 10 minutes - tags change less frequently
  })
}

/**
 * Get global tags available to user (system tags + personal tags)
 * These tags can be used across multiple projects
 */
export function useGlobalTags() {
  const { userId } = useUser()
  
  return useQuery({
    queryKey: tagKeys.global(),
    queryFn: async () => {
      if (!userId) return []
      
      // TODO: Implement global tag fetching in LocalDataProvider
      // For now, return empty array as placeholder
      
      // TODO: BACKGROUND SERVER VERIFICATION
      // When APIs are implemented:
      // 1. Return cached global tags immediately
      // 2. Background fetch from server: GET /api/users/{userId}/tags/global
      // 3. Include system tags and user's personal tags
      // 4. Sync tag definitions and metadata
      
      return [] as Tag[]
    },
    enabled: !!userId,
    staleTime: 15 * 60 * 1000, // 15 minutes - global tags change rarely
  })
}

/**
 * Get individual tag by ID from localStorage
 */
export function useTag(tagId: string) {
  const { userId } = useUser()
  
  return useQuery({
    queryKey: tagKeys.detail(tagId),
    queryFn: async () => {
      if (!userId || !tagId) return null
      
      // TODO: Add getTag method to LocalDataProvider
      // For now, we'll implement a workaround
      
      return null as Tag | null
    },
    enabled: !!userId && !!tagId,
  })
}

/**
 * Create new tag with optimistic update
 */
export function useCreateTag() {
  const { userId } = useUser()
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (newTag: Omit<Tag, 'id' | 'createdAt' | 'updatedAt'>) => {
      if (!userId) throw new Error('User not authenticated')
      
      const provider = createLocalDataProvider(userId)
      const tag = await provider.createTag(newTag)
      
      // TODO: SERVER SYNC
      // When APIs are implemented:
      // 1. Create in localStorage immediately (above)
      // 2. Queue for server sync: POST /api/projects/{projectId}/tags
      // 3. Handle tag name conflicts and validation
      // 4. Sync tag definitions with other collaborators
      
      return tag
    },
    onSuccess: (newTag) => {
      // Invalidate tags list for the project
      if (newTag.projectId) {
        queryClient.invalidateQueries({ 
          queryKey: tagKeys.list(newTag.projectId) 
        })
      }
      
      // Invalidate global tags if it's a global tag
      if (newTag.isGlobal) {
        queryClient.invalidateQueries({ queryKey: tagKeys.global() })
      }
      
      // Add to cache for immediate access
      queryClient.setQueryData(tagKeys.detail(newTag.id), newTag)
    },
    onError: (error) => {
      console.error('Failed to create tag:', error)
      // TODO: Show user-friendly error message
    }
  })
}

/**
 * Update tag with optimistic update
 */
export function useUpdateTag(tagId: string) {
  const { userId } = useUser()
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (updates: Partial<Tag>) => {
      if (!userId) throw new Error('User not authenticated')
      
      const provider = createLocalDataProvider(userId)
      const updatedTag = await provider.updateTag(tagId, updates)
      
      // TODO: SERVER SYNC WITH CONFLICT RESOLUTION
      // When APIs are implemented:
      // 1. Update localStorage immediately (above)
      // 2. Queue for server sync: PATCH /api/tags/{id}
      // 3. Handle concurrent tag modifications
      // 4. Propagate changes to all content using this tag
      
      return updatedTag
    },
    onMutate: async (updates) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: tagKeys.detail(tagId) })
      
      // Snapshot previous value for rollback
      const previousTag = queryClient.getQueryData<Tag>(tagKeys.detail(tagId))
      
      // Optimistically update cache
      if (previousTag) {
        queryClient.setQueryData(tagKeys.detail(tagId), {
          ...previousTag,
          ...updates,
          updatedAt: new Date().toISOString()
        })
      }
      
      return { previousTag }
    },
    onError: (error, updates, context) => {
      // Rollback optimistic update
      if (context?.previousTag) {
        queryClient.setQueryData(tagKeys.detail(tagId), context.previousTag)
      }
      console.error('Failed to update tag:', error)
    },
    onSuccess: (updatedTag) => {
      // Update cache with actual result
      queryClient.setQueryData(tagKeys.detail(tagId), updatedTag)
      
      // Invalidate related queries
      if (updatedTag.projectId) {
        queryClient.invalidateQueries({ 
          queryKey: tagKeys.list(updatedTag.projectId) 
        })
      }
      
      if (updatedTag.isGlobal) {
        queryClient.invalidateQueries({ queryKey: tagKeys.global() })
      }
    }
  })
}

/**
 * Delete tag with optimistic update
 */
export function useDeleteTag() {
  const { userId } = useUser()
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (tagId: string) => {
      if (!userId) throw new Error('User not authenticated')
      
      const provider = createLocalDataProvider(userId)
      await provider.deleteTag(tagId)
      
      // TODO: SERVER SYNC WITH CASCADE OPERATIONS
      // When APIs are implemented:
      // 1. Delete from localStorage immediately (above)
      // 2. Queue for server sync: DELETE /api/tags/{id}
      // 3. Handle cascade operations (remove from all content)
      // 4. Update usage counts for related tags
      
      return tagId
    },
    onMutate: async (tagId) => {
      // Get tag info before deletion for cleanup
      const tag = queryClient.getQueryData<Tag>(tagKeys.detail(tagId))
      
      if (tag) {
        // Remove from appropriate tag lists
        if (tag.projectId) {
          const previousTags = queryClient.getQueryData<Tag[]>(tagKeys.list(tag.projectId))
          if (previousTags) {
            queryClient.setQueryData(
              tagKeys.list(tag.projectId),
              previousTags.filter(t => t.id !== tagId)
            )
          }
        }
        
        if (tag.isGlobal) {
          const previousGlobalTags = queryClient.getQueryData<Tag[]>(tagKeys.global())
          if (previousGlobalTags) {
            queryClient.setQueryData(
              tagKeys.global(),
              previousGlobalTags.filter(t => t.id !== tagId)
            )
          }
        }
        
        // Remove individual tag cache
        queryClient.removeQueries({ queryKey: tagKeys.detail(tagId) })
        
        return { tag }
      }
      
      return {}
    },
    onError: (error, tagId, context) => {
      console.error('Failed to delete tag:', error)
      // For simplicity, just invalidate all tag queries to refresh from source
      queryClient.invalidateQueries({ queryKey: tagKeys.all })
    },
    onSuccess: (tagId, variables, context) => {
      if (context?.tag) {
        // Invalidate related queries to ensure consistency
        if (context.tag.projectId) {
          queryClient.invalidateQueries({ 
            queryKey: tagKeys.list(context.tag.projectId) 
          })
        }
        
        if (context.tag.isGlobal) {
          queryClient.invalidateQueries({ queryKey: tagKeys.global() })
        }
      }
    }
  })
}

/**
 * Increment tag usage count when applied to content
 */
export function useIncrementTagUsage() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (tagId: string) => {
      // This is a local operation for now
      const tag = queryClient.getQueryData<Tag>(tagKeys.detail(tagId))
      
      if (tag) {
        const updatedTag = {
          ...tag,
          usageCount: tag.usageCount + 1,
          updatedAt: new Date().toISOString()
        }
        
        queryClient.setQueryData(tagKeys.detail(tagId), updatedTag)
        
        // TODO: SERVER SYNC
        // When APIs are implemented:
        // 1. Update usage count locally (above)
        // 2. Queue for server sync: PATCH /api/tags/{id}/usage
        // 3. Aggregate usage counts across all users
        // 4. Update tag popularity rankings
        
        return updatedTag
      }
      
      return null
    },
    onError: (error) => {
      console.error('Failed to increment tag usage:', error)
    }
  })
}

/*
 * TODO: ADVANCED TAG FEATURES FOR API INTEGRATION
 * 
 * When backend APIs are ready, these hooks will support:
 * 
 * 1. COLLABORATIVE TAGGING:
 *    - Real-time tag creation and updates across users
 *    - Tag suggestion based on content analysis
 *    - Team tag vocabularies and taxonomies
 *    - Tag merge and split operations
 * 
 * 2. INTELLIGENT TAG FEATURES:
 *    - Auto-tagging based on content analysis
 *    - Tag synonym detection and grouping
 *    - Usage pattern analysis for recommendations
 *    - Tag hierarchy and categorization
 * 
 * 3. CROSS-CONTENT TAG OPERATIONS:
 *    - Bulk tag assignment and removal
 *    - Tag-based content filtering and search
 *    - Tag relationship mapping
 *    - Tag usage analytics and insights
 * 
 * 4. INTEGRATION FEATURES:
 *    - External taxonomy imports
 *    - Tag-based access control
 *    - API for third-party tag management
 *    - Export tag data for analysis
 * 
 * 5. PERFORMANCE OPTIMIZATIONS:
 *    - Tag autocomplete with fuzzy search
 *    - Lazy loading of tag lists
 *    - Efficient tag filtering algorithms
 *    - Background tag usage synchronization
 */