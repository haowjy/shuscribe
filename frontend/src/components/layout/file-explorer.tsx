"use client";

import React, { useState } from "react";
import { 
  ChevronDown, 
  ChevronRight, 
  File, 
  Folder, 
  FolderOpen, 
  MoreHorizontal,
  Plus,
  Edit,
  Trash2,
  Copy,
  FileText,
  Settings,
  Tag,
  Search,
  Filter
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator
} from "@/components/ui/dropdown-menu";
import { TreeItem } from "@/types/api";
import { useSelectedFile, useFileTree } from "@/lib/query/hooks";
import { isFile, isFolder } from "@/data/file-tree";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { TagFilterDropdown } from "@/components/metadata/TagFilterDropdown";
import { DraggableMetadataPanel } from "@/components/metadata/DraggableMetadataPanel";
import { DndContext } from '@dnd-kit/core';

// No conversion needed - API already returns FileItem format

interface FileTreeItemProps {
  item: TreeItem;
  depth: number;
  selectedFileId?: string;
  onFileSelect?: (file: TreeItem) => void;
  onFileAction?: (action: string, file: TreeItem) => void;
}

function FileTreeItem({ item, depth, selectedFileId, onFileSelect, onFileAction }: FileTreeItemProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const isSelected = selectedFileId === item.id;

  const handleClick = () => {
    console.log('🔄 [FileTreeItem] handleClick:', {
      itemId: item.id,
      itemName: item.name,
      itemType: item.type,
      isFile: isFile(item),
      isFolder: isFolder(item)
    });
    
    if (isFolder(item)) {
      console.log('🔄 [FileTreeItem] Toggling folder expansion:', item.name);
      setIsExpanded(!isExpanded);
    } else if (isFile(item)) {
      console.log('🔄 [FileTreeItem] Calling onFileSelect for file:', item.name);
      onFileSelect?.(item);
    }
  };

  const handleAction = (action: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onFileAction?.(action, item);
  };

  return (
    <div>
      <div className="flex items-center group">
        <Button
          variant="ghost"
          className={cn(
            "flex-1 justify-start gap-1 px-1 py-1 h-auto text-sm",
            "hover:bg-accent",
            isSelected && "bg-accent"
          )}
          style={{ paddingLeft: `${depth * 12 + 4}px` }}
          onClick={handleClick}
        >
        {isFolder(item) ? (
          <>
            {isExpanded ? (
              <ChevronDown className="h-3 w-3 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-3 w-3 text-muted-foreground" />
            )}
            {isExpanded ? (
              <FolderOpen className="h-4 w-4 text-blue-500" />
            ) : (
              <Folder className="h-4 w-4 text-blue-500" />
            )}
          </>
        ) : (
          <>
            <div className="w-3" />
            <File className="h-4 w-4 text-muted-foreground" />
          </>
        )}
          <span className="flex-1 truncate text-left">{item.name}</span>
          {item.tags && item.tags.length > 0 && (
            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              {item.tags.slice(0, 2).map((tag) => (
                <Badge
                  key={tag}
                  variant="secondary"
                  className="text-xs px-1 py-0 h-auto"
                >
                  {tag}
                </Badge>
              ))}
              {item.tags.length > 2 && (
                <Badge variant="outline" className="text-xs px-1 py-0 h-auto">
                  +{item.tags.length - 2}
                </Badge>
              )}
            </div>
          )}
        </Button>
        
        {/* Context Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="opacity-0 group-hover:opacity-100 transition-opacity p-1 h-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <MoreHorizontal className="h-3 w-3" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            {isFolder(item) ? (
              <>
                <DropdownMenuItem onClick={(e) => handleAction("new-file", e)}>
                  <FileText className="mr-2 h-4 w-4" />
                  New File
                </DropdownMenuItem>
                <DropdownMenuItem onClick={(e) => handleAction("new-folder", e)}>
                  <Folder className="mr-2 h-4 w-4" />
                  New Folder
                </DropdownMenuItem>
                <DropdownMenuSeparator />
              </>
            ) : (
              <>
                <DropdownMenuItem onClick={(e) => handleAction("open", e)}>
                  <File className="mr-2 h-4 w-4" />
                  Open
                </DropdownMenuItem>
                <DropdownMenuSeparator />
              </>
            )}
            <DropdownMenuItem onClick={(e) => handleAction("edit-metadata", e)}>
              <Settings className="mr-2 h-4 w-4" />
              Edit Metadata...
            </DropdownMenuItem>
            <DropdownMenuItem onClick={(e) => handleAction("quick-tag-edit", e)}>
              <Tag className="mr-2 h-4 w-4" />
              Quick Tag Edit
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={(e) => handleAction("rename", e)}>
              <Edit className="mr-2 h-4 w-4" />
              Rename
            </DropdownMenuItem>
            <DropdownMenuItem onClick={(e) => handleAction("duplicate", e)}>
              <Copy className="mr-2 h-4 w-4" />
              Duplicate
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem 
              onClick={(e) => handleAction("delete", e)}
              className="text-destructive focus:text-destructive"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      {isFolder(item) && isExpanded && item.children && (
        <div>
          {item.children.map((child) => (
            <FileTreeItem
              key={child.id}
              item={child}
              depth={depth + 1}
              selectedFileId={selectedFileId}
              onFileSelect={onFileSelect}
              onFileAction={onFileAction}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface FileExplorerProps {
  projectId: string;
  onFileClick: (fileId: string) => void;
}

export function FileExplorer({ projectId, onFileClick }: FileExplorerProps) {
  // Use file tree and simple selection state
  const { data: fileTree = [], isLoading, error } = useFileTree(projectId);
  const { selectedFileId, setSelectedFile } = useSelectedFile(projectId);
  
  // Metadata panel state
  const [metadataPanelOpen, setMetadataPanelOpen] = useState(false);
  const [selectedItemForMetadata, setSelectedItemForMetadata] = useState<TreeItem | null>(null);
  
  // Search and filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTagFilters, setActiveTagFilters] = useState<string[]>([]);
  
  // Extract all tags for filtering
  const allTags = React.useMemo(() => {
    const tagCounts: Record<string, number> = {};
    
    const countTags = (items: TreeItem[]) => {
      items.forEach(item => {
        if (item.tags) {
          item.tags.forEach(tag => {
            tagCounts[tag] = (tagCounts[tag] || 0) + 1;
          });
        }
        if (isFolder(item) && item.children) {
          countTags(item.children);
        }
      });
    };
    
    countTags(fileTree);
    
    return Object.entries(tagCounts).map(([name, count]) => ({
      name,
      count,
      color: undefined // TODO: Add color support
    }));
  }, [fileTree]);
  
  // Filter file tree based on search and tags
  const filteredFileTree = React.useMemo(() => {
    if (!searchQuery && activeTagFilters.length === 0) return fileTree;
    
    const filterItems = (items: TreeItem[]): TreeItem[] => {
      return items.reduce<TreeItem[]>((acc, item) => {
        const matchesSearch = !searchQuery || 
          item.name.toLowerCase().includes(searchQuery.toLowerCase());
        
        const matchesTags = activeTagFilters.length === 0 ||
          (item.tags && activeTagFilters.some(filter => item.tags!.includes(filter)));
        
        let filteredChildren: TreeItem[] = [];
        if (isFolder(item) && item.children) {
          filteredChildren = filterItems(item.children);
        }
        
        // Include item if it matches or has matching children
        if ((matchesSearch && matchesTags) || filteredChildren.length > 0) {
          acc.push({
            ...item,
            children: isFolder(item) ? filteredChildren : undefined
          });
        }
        
        return acc;
      }, []);
    };
    
    return filterItems(fileTree);
  }, [fileTree, searchQuery, activeTagFilters]);

  const handleFileSelect = (file: TreeItem) => {
    console.log('📁 [FileExplorer] handleFileSelect called:', {
      fileId: file.id,
      fileName: file.name,
      fileType: file.type,
      isFile: isFile(file)
    });
    
    if (isFile(file)) {
      // For files, call the parent's onFileClick handler
      console.log('📁 [FileExplorer] Calling onFileClick:', file.id);
      onFileClick(file.id);
      setSelectedFile(file.id); // Also update selection for highlighting
    } else {
      // For folders, just update the selected state for highlighting
      console.log('📁 [FileExplorer] Setting selected folder:', file.id);
      setSelectedFile(file.id);
    }
  };

  const handleFileAction = (action: string, file: TreeItem) => {
    console.log(`Action: ${action} on file:`, file);
    
    switch (action) {
      case "open":
        handleFileSelect(file);
        break;
      case "edit-metadata":
        setSelectedItemForMetadata(file);
        setMetadataPanelOpen(true);
        break;
      case "quick-tag-edit":
        setSelectedItemForMetadata(file);
        setMetadataPanelOpen(true);
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
      case "duplicate":
        // TODO: Duplicate file/folder
        break;
      case "delete":
        // TODO: Show delete confirmation
        break;
      default:
        break;
    }
  };
  
  const handleMetadataSave = async (metadata: any) => {
    console.log('Saving metadata:', metadata);
    // TODO: Implement actual metadata save API call
    // For now, just close the panel
    setMetadataPanelOpen(false);
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
    <DndContext>
      <div className="h-full flex flex-col">
        {/* Header with search and filters */}
        <div className="space-y-2 p-2 border-b">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">
              Project Files
            </span>
            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleFileAction("new-file", { id: "root", name: "root", type: "folder" })}
                className="p-1 h-auto"
              >
                <Plus className="h-3 w-3" />
              </Button>
            </div>
          </div>
          
          {/* Search and Filter Bar */}
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2 h-3 w-3 text-muted-foreground" />
              <Input
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="h-7 pl-7 text-sm"
              />
            </div>
            <TagFilterDropdown
              allTags={allTags}
              activeFilters={activeTagFilters}
              onFiltersChange={setActiveTagFilters}
            />
          </div>
          
          {/* Active filters display */}
          {(searchQuery || activeTagFilters.length > 0) && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-muted-foreground">Filtered:</span>
              {searchQuery && (
                <Badge variant="outline" className="text-xs">
                  "{searchQuery}"
                </Badge>
              )}
              {activeTagFilters.map(filter => (
                <Badge key={filter} variant="secondary" className="text-xs">
                  {filter}
                </Badge>
              ))}
            </div>
          )}
        </div>
        
        {/* File Tree */}
        <ScrollArea className="flex-1 p-1">
          <div className="space-y-1">
            {filteredFileTree.map((item) => (
              <FileTreeItem
                key={item.id}
                item={item}
                depth={0}
                selectedFileId={selectedFileId}
                onFileSelect={handleFileSelect}
                onFileAction={handleFileAction}
              />
            ))}
            {filteredFileTree.length === 0 && (
              <div className="text-center py-8">
                <p className="text-xs text-muted-foreground">
                  {searchQuery || activeTagFilters.length > 0 
                    ? 'No files match your filters' 
                    : 'No files in this project'
                  }
                </p>
              </div>
            )}
          </div>
          <ScrollBar orientation="vertical" />
        </ScrollArea>
        
        {/* Draggable Metadata Panel */}
        <DraggableMetadataPanel
          item={selectedItemForMetadata}
          isOpen={metadataPanelOpen}
          onClose={() => setMetadataPanelOpen(false)}
          onSave={handleMetadataSave}
        />
      </div>
    </DndContext>
  );
}