import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { ProjectData, Document, CreateDocumentRequest, UpdateDocumentRequest } from '@/types/project';

// Query keys
export const queryKeys = {
  projects: ['projects'] as const,
  project: (id: string) => ['projects', id] as const,
  projectData: (id: string) => ['projects', id, 'data'] as const,
  documents: ['documents'] as const,
  document: (id: string) => ['documents', id] as const,
};

// Project hooks
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
        queryKey: queryKeys.projectData(newDocument.projectId),
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
      
      // Update project data to reflect changes
      queryClient.setQueryData(
        queryKeys.projectData(updatedDocument.projectId),
        (oldData: ProjectData | undefined) => {
          if (!oldData) return oldData;
          
          return {
            ...oldData,
            documents: oldData.documents.map(doc =>
              doc.id === updatedDocument.id ? updatedDocument : doc
            ),
            updatedAt: new Date().toISOString(),
          };
        }
      );
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
          queryKey: queryKeys.projectData(documentData.projectId),
        });
      }
    },
  });
}