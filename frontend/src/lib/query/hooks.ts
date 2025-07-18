import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { apiClient } from '@/lib/api/client';
import { 
  Document, 
  CreateDocumentRequest, 
  UpdateDocumentRequest,
  ProjectListParams,
  TreeItem,
  CreateFileRequest,
  CreateFolderRequest,
  UpdateFileTreeItemRequest
} from '@/types/api';
import { loadFileTree } from '@/lib/api/file-tree-service';
import { validateTreeItem, isFile, isFolder } from '@/data/file-tree';

// Query keys
export const queryKeys = {
  projects: ['projects'] as const,
  projectsList: (params?: ProjectListParams) => ['projects', 'list', params] as const,
  project: (id: string) => ['projects', id] as const,
  projectData: (id: string) => ['projects', id, 'data'] as const,
  documents: ['documents'] as const,
  document: (id: string) => ['documents', id] as const,
  fileTree: (projectId: string) => ['projects', projectId, 'fileTree'] as const,
  activeFile: (projectId: string) => ['projects', projectId, 'activeFile'] as const,
};

// Project hooks
export function useProjects(params: ProjectListParams = {}) {
  return useQuery({
    queryKey: queryKeys.projectsList(params),
    queryFn: async () => {
      const response = await apiClient.listProjects(params);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes - project list doesn't change often
  });
}

export function useProjectData(projectId: string) {
  return useQuery({
    queryKey: queryKeys.projectData(projectId),
    queryFn: async () => {
      const response = await apiClient.getProjectData(projectId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    enabled: !!projectId,
    staleTime: 10 * 60 * 1000, // 10 minutes - project data doesn't change often
  });
}

// Document hooks
export function useDocument(documentId: string) {
  return useQuery({
    queryKey: queryKeys.document(documentId),
    queryFn: async () => {
      const response = await apiClient.getDocument(documentId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    enabled: !!documentId,
    staleTime: 2 * 60 * 1000, // 2 minutes - documents change more frequently
  });
}

// Document mutations
export function useCreateDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (document: CreateDocumentRequest) => {
      const response = await apiClient.createDocument(document);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    onSuccess: (newDocument) => {
      // Invalidate project data to refresh file tree
      queryClient.invalidateQueries({
        queryKey: queryKeys.projectData(newDocument.project_id),
      });
      
      queryClient.invalidateQueries({
        queryKey: queryKeys.fileTree(newDocument.project_id),
      });
      
      // Add document to cache
      queryClient.setQueryData(
        queryKeys.document(newDocument.id),
        newDocument
      );
    },
  });
}

export function useUpdateDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ 
      documentId, 
      updates 
    }: { 
      documentId: string; 
      updates: UpdateDocumentRequest;
    }) => {
      const response = await apiClient.updateDocument(documentId, updates);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    onSuccess: (updatedDocument) => {
      // Update document in cache
      queryClient.setQueryData(
        queryKeys.document(updatedDocument.id),
        updatedDocument
      );
      
      // Invalidate project data to refresh file tree and metadata
      queryClient.invalidateQueries({
        queryKey: queryKeys.projectData(updatedDocument.project_id),
      });
      
      queryClient.invalidateQueries({
        queryKey: queryKeys.fileTree(updatedDocument.project_id),
      });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (documentId: string) => {
      const response = await apiClient.deleteDocument(documentId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    onSuccess: (_, documentId) => {
      // Remove document from cache
      queryClient.removeQueries({
        queryKey: queryKeys.document(documentId),
      });
      
      // Invalidate project data to refresh file tree
      // We need to get project ID from cached document data
      const documentData = queryClient.getQueryData(queryKeys.document(documentId)) as Document;
      if (documentData) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.projectData(documentData.project_id),
        });
      }
    },
  });
}

// File Tree hook
export function useFileTree(projectId: string) {
  return useQuery<TreeItem[]>({
    queryKey: queryKeys.fileTree(projectId),
    queryFn: async (): Promise<TreeItem[]> => {
      const result = await loadFileTree(projectId);
      if (result.error) {
        throw new Error(result.error);
      }
      // Service now validates data, so we can trust it's properly typed
      return result.fileTree;
    },
    enabled: !!projectId,
    staleTime: 5 * 60 * 1000, // 5 minutes - file tree doesn't change often
  });
}

// Simple file selection state (for highlighting in file tree)
export function useSelectedFile(projectId: string) {
  const queryClient = useQueryClient();
  const queryKey = [...queryKeys.activeFile(projectId), 'selectedFile'];
  
  const { data: selectedFileId = null } = useQuery({
    queryKey,
    queryFn: () => Promise.resolve(null as string | null),
    enabled: !!projectId,
    staleTime: Infinity,
    gcTime: Infinity,
  });

  const setSelectedFile = useCallback((fileId: string | null) => {
    queryClient.setQueryData(queryKey, fileId);
  }, [queryClient, queryKey]);

  return {
    selectedFileId,
    setSelectedFile,
  };
}

// ============================================================================
// File Tree CRUD Operations
// ============================================================================

/**
 * Create a new folder in the file tree
 */
export function useCreateFolder() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (request: CreateFolderRequest & { project_id: string }) => {
      // Validate folder data before sending
      if (!request.name || request.name.trim() === '') {
        throw new Error('Folder name is required');
      }
      
      if ('document_id' in request && (request as any).document_id) {
        throw new Error('Folders cannot have a document_id');
      }

      const response = await apiClient.createFolder(request);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    onSuccess: (newFolder, variables) => {
      // Invalidate file tree cache to trigger reload
      queryClient.invalidateQueries({
        queryKey: queryKeys.fileTree(variables.project_id),
      });
    },
  });
}

/**
 * Create a new file in the file tree
 */
export function useCreateFile() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (request: CreateFileRequest & { project_id: string }) => {
      // Validate file data before sending
      if (!request.name || request.name.trim() === '') {
        throw new Error('File name is required');
      }
      
      if (!request.document_id) {
        throw new Error('Files must have a document_id');
      }

      const response = await apiClient.createFile(request);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    onSuccess: (newFile, variables) => {
      // Invalidate file tree cache to trigger reload
      queryClient.invalidateQueries({
        queryKey: queryKeys.fileTree(variables.project_id),
      });
    },
  });
}

/**
 * Update a file tree item
 */
export function useUpdateFileTreeItem() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (params: { 
      itemId: string; 
      projectId: string; 
      updates: UpdateFileTreeItemRequest 
    }) => {
      const { itemId, updates } = params;
      
      // Basic validation
      if (updates.name !== undefined && (!updates.name || updates.name.trim() === '')) {
        throw new Error('Name cannot be empty');
      }

      const response = await apiClient.updateFileTreeItem(itemId, updates);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    onSuccess: (updatedItem, variables) => {
      // Invalidate file tree cache to trigger reload
      queryClient.invalidateQueries({
        queryKey: queryKeys.fileTree(variables.projectId),
      });
    },
  });
}

/**
 * Delete a file tree item
 */
export function useDeleteFileTreeItem() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (params: { itemId: string; projectId: string }) => {
      const { itemId } = params;
      
      const response = await apiClient.deleteFileTreeItem(itemId);
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data!;
    },
    onSuccess: (deletedItem, variables) => {
      // Invalidate file tree cache to trigger reload
      queryClient.invalidateQueries({
        queryKey: queryKeys.fileTree(variables.projectId),
      });
    },
  });
}