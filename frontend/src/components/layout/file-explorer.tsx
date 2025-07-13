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
  selectedFileId?: string | null; // Allow null for selectedFileId
  onFileSelect?: (file: TreeItem) => void;
  onFileAction?: (action: string, file: TreeItem) => void;
}

function FileTreeItem({ item, depth, selectedFileId, onFileSelect, onFileAction }: FileTreeItemProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [contextMenuOpen, setContextMenuOpen] = useState(false);
  const isSelected = selectedFileId === item.id;

  const handleClick = () => {
    console.log('🔄 [FileTreeItem] handleClick:', item);
    
    if (isFolder(item)) {
      console.log('🔄 [FileTreeItem] Toggling folder expansion:', item.name);
      setIsExpanded(!isExpanded);
    } else if (isFile(item)) {
      console.log('🔄 [FileTreeItem] Calling onFileSelect for file:', item.name);
      onFileSelect?.(item);
    }
  };

  const handleAction = (action: string) => {
    setContextMenuOpen(false);
    onFileAction?.(action, item);
  };

  const handleRightClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setContextMenuOpen(true);
  };

  return (
    <div>
      <div className="group w-full" onContextMenu={handleRightClick}>
        <Button
          variant="ghost"
          className={cn(
            "w-full justify-start gap-1 px-1 py-1 h-auto text-sm",
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
            <div className="flex gap-1 transition-opacity">
              {item.tags.slice(0, 2).map((tag, index) => (
                <Badge
                  key={tag.id}
                  variant="secondary"
                  className="text-xs px-1 py-0 h-auto"
                  style={tag.color ? { backgroundColor: tag.color, color: '#fff' } : undefined}
                >
                  {tag.icon && <span className="mr-1">{tag.icon}</span>}
                  {tag.name}
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
      </div>
      
      {/* Simple Context Menu */}
      <DropdownMenu open={contextMenuOpen} onOpenChange={setContextMenuOpen}>
        <DropdownMenuContent className="w-56">
          {isFolder(item) ? (
            <>
              <DropdownMenuItem onClick={() => handleAction("new-file")}>
                <FileText className="mr-2 h-4 w-4" />
                New File
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleAction("new-folder")}>
                <Folder className="mr-2 h-4 w-4" />
                New Folder
              </DropdownMenuItem>
              <DropdownMenuSeparator />
            </>
          ) : (
            <>
              <DropdownMenuItem onClick={() => handleAction("open")}>
                <File className="mr-2 h-4 w-4" />
                Open
              </DropdownMenuItem>
              <DropdownMenuSeparator />
            </>
          )}
          <DropdownMenuItem onClick={() => handleAction("edit-metadata")}>
            <Settings className="mr-2 h-4 w-4" />
            Edit Metadata...
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => handleAction("quick-tag-edit")}>
            <Tag className="mr-2 h-4 w-4" />
            Quick Tag Edit
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => handleAction("rename")}>
            <Edit className="mr-2 h-4 w-4" />
            Rename
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => handleAction("duplicate")}>
            <Copy className="mr-2 h-4 w-4" />
            Duplicate
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem 
            onClick={() => handleAction("delete")}
            className="text-destructive focus:text-destructive"
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      {isFolder(item) && isExpanded && item.children && (
        <>
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
        </>
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
    const tagMap: Record<string, { tag: any; count: number }> = {};
    
    const countTags = (items: TreeItem[]) => {
      items.forEach(item => {
        if (item.tags) {
          item.tags.forEach(tag => {
            if (!tagMap[tag.id]) {
              tagMap[tag.id] = { tag, count: 0 };
            }
            tagMap[tag.id].count += 1;
          });
        }
        if (isFolder(item) && item.children) {
          countTags(item.children);
        }
      });
    };
    
    countTags(fileTree);
    
    return Object.values(tagMap).map(({ tag, count }) => ({
      id: tag.id,
      name: tag.name,
      icon: tag.icon,
      color: tag.color,
      usage_count: count,
      // Add default/placeholder values for ProjectTag properties
      is_system: false, // Assuming tags from fileTree are not system tags unless specified
      is_archived: false, // Assuming tags from fileTree are not archived unless specified
      created_at: new Date().toISOString(), // Placeholder
      updated_at: new Date().toISOString(), // Placeholder
      description: tag.description || '',
      category: tag.category || '',
      last_used: tag.last_used || new Date().toISOString(),
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
          (item.tags && activeTagFilters.some(filter => item.tags!.some(tag => tag.name === filter)));
        
        let filteredChildren: TreeItem[] = [];
        if (isFolder(item) && item.children) {
          filteredChildren = filterItems(item.children);
        }
        
        // Include item if it matches or has matching children
        if ((matchesSearch && matchesTags) || filteredChildren.length > 0) {
          if (isFolder(item)) {
            acc.push({
              ...item,
              children: filteredChildren,
            });
          } else {
            // For files, ensure no 'children' property is added
            acc.push(item);
          }
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