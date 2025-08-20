/**
 * Project Data Hooks - localStorage-first with future API sync
 * 
 * WHY: These hooks provide instant UI responses from Dexie cache while preparing
 * for background server synchronization. Content creators need zero-latency
 * interactions with their project data.
 * 
 * Problem Context: Traditional web apps wait for server responses before updating UI.
 * For creative tools, this breaks user flow. These hooks enable immediate responses
 * from local cache with future server verification.
 * 
 * Architecture Pattern:
 * 1. Return cached data immediately from Dexie
 * 2. TODO: Background verification with server when APIs are ready
 * 3. TODO: Conflict resolution for out-of-sync data
 * 4. Optimistic updates for mutations
 * 
 * Usage Patterns:
 * - Replace direct LocalDataProvider calls in components
 * - Automatic cache invalidation on mutations
 * - Type-safe with existing domain models
 * 
 * Integration Points:
 * - Uses LocalDataProvider for immediate implementation
 * - Compatible with existing ProjectStateProvider
 * - Prepares for future API integration with server sync
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useUser } from '@/hooks/useUser'
import { createLocalDataProvider } from '@/lib/data/local-provider'
import type { Project } from '@/lib/localdb/types'

// Query keys for consistent cache management
export const projectKeys = {
  all: ['projects'] as const,
  lists: () => [...projectKeys.all, 'list'] as const,
  list: (userId?: string) => [...projectKeys.lists(), userId] as const,
  details: () => [...projectKeys.all, 'detail'] as const,
  detail: (id: string) => [...projectKeys.details(), id] as const,
}

/**
 * Get all projects for current user from localStorage
 * Returns cached data immediately, prepares for server sync
 */
export function useProjects() {
  const { userId } = useUser()
  
  return useQuery({
    queryKey: projectKeys.list(userId),
    queryFn: async () => {
      if (!userId) return []
      
      const provider = createLocalDataProvider(userId)
      const projects = await provider.getProjects()
      
      // TODO: BACKGROUND SERVER VERIFICATION
      // When APIs are implemented, add background verification:
      // 1. Return cached data immediately (above)
      // 2. Background fetch from server API
      // 3. Compare timestamps/versions for conflicts
      // 4. Auto-resolve or prompt user for conflicts
      // 5. Update cache with resolved data
      
      return projects
    },
    enabled: !!userId,
    staleTime: 10 * 60 * 1000, // 10 minutes - trust cache for longer
  })
}

/**
 * Get individual project by ID from localStorage
 * Returns cached data immediately, prepares for server sync
 */
export function useProject(projectId: string) {
  const { userId } = useUser()
  
  return useQuery({
    queryKey: projectKeys.detail(projectId),
    queryFn: async () => {
      if (!userId) return null
      
      const provider = createLocalDataProvider(userId)
      const project = await provider.getProject(projectId)
      
      // TODO: BACKGROUND SERVER VERIFICATION
      // When APIs are implemented:
      // 1. Return cached project immediately (above)
      // 2. Background fetch from server: GET /api/projects/{id}
      // 3. Compare project.updatedAt with server version
      // 4. Handle conflicts with resolution strategy
      
      return project
    },
    enabled: !!userId && !!projectId,
  })
}

/**
 * Create new project with optimistic update
 */
export function useCreateProject() {
  const { userId } = useUser()
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (newProject: Omit<Project, 'id' | 'createdAt' | 'updatedAt'>) => {
      if (!userId) throw new Error('User not authenticated')
      
      const provider = createLocalDataProvider(userId)
      const project = await provider.createProject(newProject)
      
      // TODO: SERVER SYNC
      // When APIs are implemented:
      // 1. Create in localStorage immediately (above)
      // 2. Queue for server sync: POST /api/projects
      // 3. Handle server validation errors
      // 4. Update local cache with server-assigned IDs if needed
      
      return project
    },
    onSuccess: (newProject) => {
      // Invalidate projects list to trigger refetch
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() })
      
      // Add to cache for immediate access
      queryClient.setQueryData(projectKeys.detail(newProject.id), newProject)
    },
    onError: (error) => {
      console.error('Failed to create project:', error)
      // TODO: Show user-friendly error message
    }
  })
}

/**
 * Update existing project with optimistic update
 */
export function useUpdateProject(projectId: string) {
  const { userId } = useUser()
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (updates: Partial<Project>) => {
      if (!userId) throw new Error('User not authenticated')
      
      const provider = createLocalDataProvider(userId)
      const updatedProject = await provider.updateProject(projectId, updates)
      
      // TODO: SERVER SYNC
      // When APIs are implemented:
      // 1. Update localStorage immediately (above)
      // 2. Queue for server sync: PATCH /api/projects/{id}
      // 3. Handle version conflicts (server version newer)
      // 4. Implement conflict resolution UI for user input
      
      return updatedProject
    },
    onMutate: async (updates) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: projectKeys.detail(projectId) })
      
      // Snapshot previous value for rollback
      const previousProject = queryClient.getQueryData<Project>(projectKeys.detail(projectId))
      
      // Optimistically update cache
      if (previousProject) {
        queryClient.setQueryData(projectKeys.detail(projectId), {
          ...previousProject,
          ...updates,
          updatedAt: new Date().toISOString()
        })
      }
      
      return { previousProject }
    },
    onError: (error, updates, context) => {
      // Rollback optimistic update
      if (context?.previousProject) {
        queryClient.setQueryData(projectKeys.detail(projectId), context.previousProject)
      }
      console.error('Failed to update project:', error)
    },
    onSuccess: (updatedProject) => {
      // Update cache with actual result
      queryClient.setQueryData(projectKeys.detail(projectId), updatedProject)
      
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() })
    }
  })
}

/**
 * Delete project with optimistic update
 */
export function useDeleteProject() {
  const { userId } = useUser()
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (projectId: string) => {
      if (!userId) throw new Error('User not authenticated')
      
      const provider = createLocalDataProvider(userId)
      await provider.deleteProject(projectId)
      
      // TODO: SERVER SYNC
      // When APIs are implemented:
      // 1. Delete from localStorage immediately (above)
      // 2. Queue for server sync: DELETE /api/projects/{id}
      // 3. Handle server-side cascade deletes
      // 4. Sync related data (documents, file tree, etc.)
      
      return projectId
    },
    onMutate: async (projectId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: projectKeys.all })
      
      // Remove from projects list cache
      const previousProjects = queryClient.getQueryData<Project[]>(projectKeys.lists())
      if (previousProjects) {
        queryClient.setQueryData(
          projectKeys.lists(), 
          previousProjects.filter(p => p.id !== projectId)
        )
      }
      
      // Remove individual project cache
      queryClient.removeQueries({ queryKey: projectKeys.detail(projectId) })
      
      return { previousProjects }
    },
    onError: (error, projectId, context) => {
      // Rollback optimistic update
      if (context?.previousProjects) {
        queryClient.setQueryData(projectKeys.lists(), context.previousProjects)
      }
      console.error('Failed to delete project:', error)
    },
    onSuccess: () => {
      // Invalidate to ensure consistency
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() })
    }
  })
}

/*
 * TODO: COMPREHENSIVE API INTEGRATION ROADMAP
 * 
 * When backend APIs are ready, these hooks will evolve to support:
 * 
 * 1. DUAL-SOURCE DATA STRATEGY:
 *    - Immediate return from Dexie cache (zero latency)
 *    - Background server verification
 *    - Smart conflict detection and resolution
 * 
 * 2. CONFLICT RESOLUTION MECHANISMS:
 *    - Timestamp comparison for automatic resolution
 *    - Version field checking for conflict detection
 *    - User-prompted resolution for content conflicts
 *    - Three-way merge for compatible changes
 * 
 * 3. OFFLINE OPERATION QUEUE:
 *    - Queue mutations when offline
 *    - Automatic sync when connection restored
 *    - Exponential backoff for failed requests
 *    - Batch operations for efficiency
 * 
 * 4. REAL-TIME SYNCHRONIZATION:
 *    - WebSocket integration for live updates
 *    - Operational transforms for concurrent editing
 *    - Presence indicators for collaborators
 *    - Live cursor positions and selections
 * 
 * 5. PERFORMANCE OPTIMIZATIONS:
 *    - Intelligent prefetching based on navigation patterns
 *    - Partial updates for large documents
 *    - Background sync prioritization
 *    - Memory management for large datasets
 * 
 * 6. ERROR RECOVERY STRATEGIES:
 *    - Graceful degradation during API failures
 *    - Local data corruption detection and repair
 *    - User notification for sync conflicts
 *    - Manual conflict resolution interfaces
 */