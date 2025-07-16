"use client";

import React, { useState } from "react";
import { TooltipProvider } from "@/components/ui/tooltip";
import { useFileTree } from "@/lib/query/hooks";
import { TreeItem } from "@/data/file-tree";
import { FileExplorerProps, FileTreeState } from "./types/file-explorer";
import { FileTreeItem } from "./components/FileTreeItem";
import { SearchBar } from "./components/SearchBar";
import { MetadataEditor } from "./components/MetadataEditor";
import { useFileTreeSearch } from "./hooks/useFileTreeSearch";
import { useUpdateDocument } from "@/lib/query/hooks";
import { UpdateDocumentRequest } from "@/types/api";

export function FileExplorer({ projectId, onFileClick }: FileExplorerProps) {
  // Data loading
  const { data: fileTree = [], isLoading, error } = useFileTree(projectId);
  const updateDocumentMutation = useUpdateDocument();
  
  // Local file explorer state
  const [fileTreeState, setFileTreeState] = useState<FileTreeState>({
    expandedFolders: new Set(),
    selectedItemId: null,
    searchState: {
      query: '',
      tagFilters: [],
      statusFilter: 'all',
      contentTypeFilter: []
    }
  });

  // Metadata editor state
  const [metadataEditorOpen, setMetadataEditorOpen] = useState(false);
  const [metadataEditorItem, setMetadataEditorItem] = useState<TreeItem | null>(null);

  // Search and filtering logic
  const { filteredFileTree, allTags } = useFileTreeSearch(fileTree, fileTreeState.searchState);

  // FileTreeItems now handle their own responsiveness with ResizeObserver

  // Handle file selection
  const handleFileSelect = (file: TreeItem) => {
    console.log('📁 [FileExplorer] handleFileSelect called:', {
      fileId: file.id,
      fileName: file.name,
      fileType: file.type
    });
    
    // Update local selection state
    setFileTreeState(prev => ({
      ...prev,
      selectedItemId: file.id
    }));

    // Call parent's onFileClick if it's a file
    if (file.type === 'file') {
      console.log('📁 [FileExplorer] Calling onFileClick:', file.id);
      onFileClick(file.id);
    }
  };

  // Handle file actions (context menu, etc.)
  const handleFileAction = (action: string, file: TreeItem) => {
    console.log(`Action: ${action} on file:`, file);
    
    switch (action) {
      case "open":
        handleFileSelect(file);
        break;
      case "edit-metadata":
        setMetadataEditorItem(file);
        setMetadataEditorOpen(true);
        break;
      case "quick-tag-edit":
        // TODO: Show quick tag editor
        break;
      case "new-file":
        // TODO: Show create file dialog
        break;
      case "new-folder":
        // TODO: Show create folder dialog
        break;
      case "rename":
        // TODO: Show rename dialog
        break;
      case "copy-reference":
        handleCopyReference(file);
        break;
      case "copy":
        // TODO: Copy file/folder
        break;
      case "delete":
        // TODO: Show delete confirmation
        break;
      default:
        console.warn('Unknown action:', action);
        break;
    }
  };

  // Handle metadata save
  const handleMetadataSave = async (updates: UpdateDocumentRequest) => {
    if (!metadataEditorItem || metadataEditorItem.type !== 'file') {
      throw new Error('Cannot update metadata for non-file items');
    }

    // For files, we need the document_id to update the document
    const documentId = metadataEditorItem.document_id;
    if (!documentId) {
      throw new Error('File has no associated document_id');
    }

    await updateDocumentMutation.mutateAsync({
      documentId,
      updates
    });
  };

  // Handle copy reference
  const handleCopyReference = async (file: TreeItem) => {
    try {
      // Create @reference syntax based on file type and name
      let reference = '';
      if (file.type === 'file') {
        // For files, use @filename syntax
        const fileName = file.name.replace(/\.[^/.]+$/, ""); // Remove extension
        reference = `@${fileName}`;
      } else {
        // For folders, use @folder/name syntax
        reference = `@${file.name}/`;
      }
      
      await navigator.clipboard.writeText(reference);
      console.log(`📋 Copied reference: ${reference}`);
      // TODO: Show success toast
    } catch (error) {
      console.error('Failed to copy reference:', error);
      // TODO: Show error toast
    }
  };

  // Handle search state updates
  const updateSearchState = (updates: Partial<FileTreeState['searchState']>) => {
    setFileTreeState(prev => ({
      ...prev,
      searchState: { ...prev.searchState, ...updates }
    }));
  };

  // Handle tag click for filtering
  const handleTagClick = (tagName: string) => {
    console.log('📋 [FileExplorer] Tag clicked for filtering:', tagName);
    
    // Add tag to filter if not already present
    const currentFilters = fileTreeState.searchState.tagFilters;
    if (!currentFilters.includes(tagName)) {
      updateSearchState({
        tagFilters: [...currentFilters, tagName]
      });
    }
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto mb-2"></div>
          <p className="text-xs text-muted-foreground">Loading files...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return (
      <div className="h-full flex items-center justify-center p-4">
        <div className="text-center">
          <p className="text-xs text-destructive mb-1">Failed to load files</p>
          <p className="text-xs text-muted-foreground">{errorMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <TooltipProvider>
      <div className="h-full flex flex-col w-full overflow-hidden">
      {/* Search and Filter Controls */}
      <SearchBar
        searchState={fileTreeState.searchState}
        allTags={allTags}
        onSearchStateChange={updateSearchState}
      />
      
      {/* File Tree */}
      <div className="flex-1 p-1 w-full overflow-auto">
        <div className="space-y-1">
          {filteredFileTree.map((item) => (
            <FileTreeItem
              key={item.id}
              item={item}
              depth={0}
              selectedFileId={fileTreeState.selectedItemId}
              onFileSelect={handleFileSelect}
              onFileAction={handleFileAction}
              onTagClick={handleTagClick}
            />
          ))}
          {filteredFileTree.length === 0 && (
            <div className="text-center py-8">
              <p className="text-xs text-muted-foreground">
                {fileTreeState.searchState.query || fileTreeState.searchState.tagFilters.length > 0
                  ? 'No files match your filters' 
                  : 'No files in this project'
                }
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Metadata Editor Dialog */}
      {metadataEditorItem && (
        <MetadataEditor
          item={metadataEditorItem}
          isOpen={metadataEditorOpen}
          onClose={() => {
            setMetadataEditorOpen(false);
            setMetadataEditorItem(null);
          }}
          onSave={handleMetadataSave}
        />
      )}
      </div>
    </TooltipProvider>
  );
}