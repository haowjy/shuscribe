/**
 * Data Hooks - Centralized exports for localStorage-first architecture
 * 
 * WHY: This index provides a clean API for components to access all data hooks.
 * The localStorage-first pattern ensures instant UI responses while preparing
 * for future server synchronization with conflict resolution.
 * 
 * Usage:
 * import { useProjects, useDocuments } from '@/hooks/data'
 * 
 * Architecture:
 * - All hooks return cached data immediately from Dexie
 * - Background server verification will be added when APIs are ready
 * - Optimistic updates provide instant UI feedback
 * - TanStack Query handles cache management and invalidation
 */

// Project management hooks
export {
  useProjects,
  useProject,
  useCreateProject,
  useUpdateProject,
  useDeleteProject,
  projectKeys
} from './useProjects'

// Document management hooks
export {
  useDocuments,
  useDocument,
  useCreateDocument,
  useUpdateDocument,
  useDeleteDocument,
  documentKeys
} from './useDocuments'

// File tree management hooks
export {
  useFileTree,
  useFileTreeItem,
  useCreateFileTreeItem,
  useUpdateFileTreeItem,
  useDeleteFileTreeItem,
  useToggleFileTreeItem,
  fileTreeKeys
} from './useFileTree'

// Tag management hooks
export {
  useTags,
  useGlobalTags,
  useTag,
  useCreateTag,
  useUpdateTag,
  useDeleteTag,
  useIncrementTagUsage,
  tagKeys
} from './useTags'

// TODO: Add more specialized hooks as needed:
// - useReferenceIndex (for @-mentions)
// - useSearch (full-text search across content)
// - useCollaborators (project collaborator management)
// - useActivity (project activity feed)
// - useVersions (document version history)