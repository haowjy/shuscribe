import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { ProjectData, Document } from '@/types/project';
import { CreateDocumentRequest, UpdateDocumentRequest } from '@/types/api';
import { 
  DocumentStorage, 
  DraftManager
} from '@/lib/editor/storage-utils';
import { DocumentState, EditorDocument } from '@/lib/editor/editor-types';
import { 
  createEmptyDocument, 
  sanitizeContent 
} from '@/lib/editor/content-utils';
import { createDebug } from '@/lib/utils/logger';

const debug = createDebug('app:hooks');

// Extended query keys for localStorage integration
export const enhancedQueryKeys = {
  projects: ['projects'] as const,
  project: (id: string) => ['projects', id] as const,
  projectData: (id: string) => ['projects', id, 'data'] as const,
  documents: ['documents'] as const,
  document: (id: string) => ['documents', id] as const,
  documentLocal: (id: string) => ['documents', id, 'local'] as const,
  documentDraft: (id: string) => ['documents', id, 'draft'] as const,
};

/**
 * Enhanced document hook with localStorage-first strategy
 */
export function useDocumentWithStorage(documentId: string) {
  return useQuery({
    queryKey: enhancedQueryKeys.documentLocal(documentId),
    queryFn: async () => {
      // 1. First check localStorage for document
      const localDocument = DocumentStorage.getDocument(documentId);
      if (localDocument && localDocument.content) {
        debug(`Loaded document ${documentId} from localStorage`);
        return {
          ...localDocument,
          source: 'localStorage' as const,
        };
      }

      // 2. Check for draft if no saved document
      const draft = DraftManager.getDraft(documentId);
      if (draft) {
        debug(`Loaded draft for document ${documentId}`);
        return {
          id: documentId,
          title: draft.title || `Untitled ${documentId}`,
          content: draft.content,
          isDirty: true,
          isTemp: true,
          lastModified: draft.timestamp,
          order: 0,
          source: 'draft' as const,
        };
      }

      // 3. Check if we have ANY local documents before falling back to API
      const allLocalDocs = DocumentStorage.getAllDocuments();
      const hasAnyLocalData = Object.keys(allLocalDocs).length > 0;

      // Only fetch from API if we have no local data at all
      if (!hasAnyLocalData) {
        try {
          const response = await apiClient.getDocument(documentId);
          if (response.error) {
            throw new Error(response.error);
          }

          const apiDocument = response.data!;
          
          // Convert API document to our format and store locally
          const documentState: DocumentState = {
            id: apiDocument.id,
            title: apiDocument.title,
            content: sanitizeContent(apiDocument.content),
            isDirty: false,
            isTemp: false,
            lastModified: Date.now(),
            order: 0,
          };

          // Save to localStorage for next time
          DocumentStorage.saveDocument(documentId, documentState);

          debug(`Loaded document ${documentId} from API and cached locally`);
          return {
            ...documentState,
            source: 'api' as const,
          };
        } catch (error) {
          console.error(`Failed to load document ${documentId}:`, error);
        }
      }
      
      // Return empty document as fallback
      return {
        id: documentId,
        title: `Document ${documentId}`,
        content: createEmptyDocument(),
        isDirty: false,
        isTemp: true,
        lastModified: Date.now(),
        order: 0,
        source: 'fallback' as const,
      };
    },
    enabled: !!documentId,
    staleTime: Infinity, // localStorage data is always fresh
    gcTime: 24 * 60 * 60 * 1000, // Keep in memory for 24 hours
  });
}

/**
 * Hook for checking if a document has unsaved changes
 */
export function useDocumentDraft(documentId: string) {
  return useQuery({
    queryKey: enhancedQueryKeys.documentDraft(documentId),
    queryFn: () => {
      const draft = DraftManager.getDraft(documentId);
      return draft;
    },
    enabled: !!documentId,
    staleTime: 0, // Always check for latest draft
    refetchInterval: 5000, // Check every 5 seconds for auto-save updates
  });
}

/**
 * Enhanced project data hook with offline support
 */
export function useProjectDataWithStorage(projectId: string) {
  return useQuery({
    queryKey: enhancedQueryKeys.projectData(projectId),
    queryFn: async () => {
      debug('Loading project data with storage for project:', projectId);
      
      // Try to get real project data from backend first
      let backendProjectData = null;
      try {
        const response = await apiClient.getProjectData(projectId);
        if (!response.error) {
          backendProjectData = response.data;
          debug('Real project data loaded from backend:', backendProjectData?.title);
        } else {
          console.warn('Backend project data failed:', response.error);
        }
      } catch (error) {
        console.warn('Failed to load project data from backend:', error);
      }
      
      // If no backend data available, create minimal project structure
      const projectData = backendProjectData || {
        id: projectId,
        title: `Project ${projectId}`,
        description: 'Project description',
        documents: [],
        fileTree: [],
        tags: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      // Get all local documents
      const allLocalDocs = DocumentStorage.getAllDocuments();
      const hasAnyLocalData = Object.keys(allLocalDocs).length > 0;
      debug('Local documents found:', Object.keys(allLocalDocs).length);
      
      // Create a map of documents starting with backend data
      const documentsMap = new Map<string, Document>();
      
      // Add backend documents to the map first (if any)
      if ('documents' in projectData && projectData.documents) {
        (projectData.documents as Document[]).forEach(doc => {
          documentsMap.set(doc.id, doc);
        });
      }
      
      // If we have local data, overlay it on top of backend data
      if (hasAnyLocalData) {
        const projectDocs = Object.values(allLocalDocs).filter(
          doc => doc.id.startsWith(projectId)
        );
        
        // Overlay local documents (they take precedence over backend data for same IDs)
        projectDocs.forEach(localDoc => {
          documentsMap.set(localDoc.id, {
            id: localDoc.id,
            title: localDoc.title,
            content: localDoc.content,
            path: localDoc.title.toLowerCase().replace(/\s+/g, '-'),
            projectId: projectId,
            createdAt: new Date(localDoc.lastModified).toISOString(),
            updatedAt: new Date(localDoc.lastModified).toISOString(),
            tags: [],
            wordCount: 0,
          });
        });
      }
      
      // Convert map back to array and enhance all documents with storage metadata
      const finalDocuments = Array.from(documentsMap.values()).map(doc => {
        const localDoc = DocumentStorage.getDocument(doc.id);
        const draft = DraftManager.getDraft(doc.id);
        
        return {
          ...doc,
          hasLocalChanges: !!localDoc && localDoc.isDirty,
          hasDraft: !!draft,
          lastLocalModified: localDoc?.lastModified || null,
        };
      });
      
      debug('Final project data contains', finalDocuments.length, 'documents with IDs:', finalDocuments.map(d => d.id));
      
      return {
        ...projectData,
        documents: finalDocuments,
      };
    },
    enabled: !!projectId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Save document with localStorage-first strategy
 */
export function useSaveDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ 
      documentId, 
      content, 
      title,
      saveToApi = true 
    }: { 
      documentId: string; 
      content: EditorDocument;
      title?: string;
      saveToApi?: boolean;
    }) => {
      // Always save to localStorage first (fast and reliable)
      const documentState: DocumentState = {
        id: documentId,
        title: title || `Document ${documentId}`,
        content: sanitizeContent(content),
        isDirty: !saveToApi, // Mark as dirty if not saving to API
        isTemp: false,
        lastModified: Date.now(),
        order: 0,
      };

      DocumentStorage.saveDocument(documentId, documentState);
      
      // Remove draft since we're saving
      DraftManager.removeDraft(documentId);

      let apiResult = null;
      
      if (saveToApi) {
        try {
          // Try to save to API
          const updates: UpdateDocumentRequest = {
            title: documentState.title,
            content: content,
          };

          const response = await apiClient.updateDocument(documentId, updates);
          if (response.error) {
            throw new Error(response.error);
          }

          apiResult = response.data!;
          
          // Mark as not dirty since API save succeeded
          documentState.isDirty = false;
          DocumentStorage.saveDocument(documentId, documentState);
          
          debug(`Document ${documentId} saved to API and localStorage`);
        } catch (error) {
          console.warn(`Failed to save document ${documentId} to API, kept in localStorage:`, error);
          // Keep as dirty for next sync attempt
          documentState.isDirty = true;
          DocumentStorage.saveDocument(documentId, documentState);
        }
      }

      return {
        localSave: documentState,
        apiSave: apiResult,
      };
    },
    onSuccess: ({ localSave, apiSave }, { documentId }) => {
      // Update local document cache
      queryClient.setQueryData(
        enhancedQueryKeys.documentLocal(documentId),
        {
          ...localSave,
          source: apiSave ? 'api' as const : 'localStorage' as const,
        }
      );

      // Clear draft cache
      queryClient.invalidateQueries({
        queryKey: enhancedQueryKeys.documentDraft(documentId),
      });

      // Update project data if API save succeeded
      if (apiSave) {
        queryClient.invalidateQueries({
          queryKey: enhancedQueryKeys.projectData(apiSave.project_id),
        });
      }
    },
  });
}

/**
 * Create new document with localStorage integration
 */
export function useCreateDocumentWithStorage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: CreateDocumentRequest & { 
      saveToApi?: boolean;
      isTemp?: boolean;
    }) => {
      const documentId = `temp-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      
      const documentState: DocumentState = {
        id: documentId,
        title: request.title,
        content: sanitizeContent(request.content || createEmptyDocument()),
        isDirty: !request.saveToApi,
        isTemp: request.isTemp || false,
        lastModified: Date.now(),
        order: 0,
      };

      // Always save locally first
      DocumentStorage.saveDocument(documentId, documentState);

      let apiResult = null;

      if (request.saveToApi) {
        try {
          const response = await apiClient.createDocument(request);
          if (response.error) {
            throw new Error(response.error);
          }

          apiResult = response.data!;
          
          // Update with real ID from API
          DocumentStorage.removeDocument(documentId);
          documentState.id = apiResult.id;
          documentState.isDirty = false;
          DocumentStorage.saveDocument(apiResult.id, documentState);
          
          debug(`Document created in API with ID ${apiResult.id}`);
        } catch (error) {
          console.warn('Failed to create document in API, kept locally:', error);
        }
      }

      return {
        localDocument: documentState,
        apiDocument: apiResult,
        finalId: apiResult?.id || documentId,
      };
    },
    onSuccess: ({ localDocument, apiDocument, finalId }) => {
      // Cache the new document
      queryClient.setQueryData(
        enhancedQueryKeys.documentLocal(finalId),
        {
          ...localDocument,
          id: finalId,
          source: apiDocument ? 'api' as const : 'localStorage' as const,
        }
      );

      // Invalidate project data to show new document
      if (apiDocument) {
        queryClient.invalidateQueries({
          queryKey: enhancedQueryKeys.projectData(apiDocument.project_id),
        });
      }
    },
  });
}

/**
 * Sync local changes to API (for background sync)
 */
export function useSyncLocalChanges() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const localDocuments = DocumentStorage.getAllDocuments();
      const dirtyDocuments = Object.values(localDocuments).filter(doc => doc.isDirty);
      
      const results = [];
      
      for (const doc of dirtyDocuments) {
        try {
          const updates: UpdateDocumentRequest = {
            title: doc.title,
            content: doc.content,
          };

          const response = await apiClient.updateDocument(doc.id, updates as any);
          if (!response.error) {
            // Mark as synced
            doc.isDirty = false;
            DocumentStorage.saveDocument(doc.id, doc);
            results.push({ id: doc.id, status: 'synced' });
          } else {
            results.push({ id: doc.id, status: 'error', error: response.error });
          }
        } catch (error) {
          results.push({ id: doc.id, status: 'error', error: String(error) });
        }
      }

      return results;
    },
    onSuccess: (results) => {
      const syncedIds = results.filter(r => r.status === 'synced').map(r => r.id);
      
      // Invalidate queries for synced documents
      syncedIds.forEach(id => {
        queryClient.invalidateQueries({
          queryKey: enhancedQueryKeys.documentLocal(id),
        });
      });

      debug(`Synced ${syncedIds.length} documents to API`);
    },
  });
}