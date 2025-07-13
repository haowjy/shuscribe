"use client";

import { useState } from "react";
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
  FileText
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
import { useActiveFile, useFileTree } from "@/lib/query/hooks";
import { isFile, isFolder } from "@/data/file-tree";
import { cn } from "@/lib/utils";

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
    if (isFolder(item)) {
      setIsExpanded(!isExpanded);
    } else if (isFile(item)) {
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
          <DropdownMenuContent align="end" className="w-48">
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
}

export function FileExplorer({ projectId }: FileExplorerProps) {
  // Use centralized file tree and active file state
  const { data: fileTree = [], isLoading, error } = useFileTree(projectId);
  const { selectedFileId, openFile, setSelectedFile } = useActiveFile(projectId);

  const handleFileSelect = (file: TreeItem) => {
    if (isFile(file)) {
      // For files, open them (this will also update selectedFileId)
      openFile(file.id);
    } else {
      // For folders, just update the selected state for highlighting
      setSelectedFile(file.id);
    }
  };

  const handleFileAction = (action: string, file: TreeItem) => {
    // TODO: Implement file operations
    console.log(`Action: ${action} on file:`, file);
    
    switch (action) {
      case "open":
        handleFileSelect(file);
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
    <div className="h-full flex flex-col">
      {/* Header with actions */}
      <div className="flex items-center justify-between p-2 border-b">
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
      
      {/* File Tree */}
      <ScrollArea className="h-[calc(100vh-200px)] p-1">
        <div className="space-y-1">
          {fileTree.map((item) => (
            <FileTreeItem
              key={item.id}
              item={item}
              depth={0}
              selectedFileId={selectedFileId}
              onFileSelect={handleFileSelect}
              onFileAction={handleFileAction}
            />
          ))}
        </div>
        <ScrollBar orientation="vertical" />
      </ScrollArea>
      
      {/* File Info */}
      {(() => {
        if (!selectedFileId) return null;
        
        // Find the selected file in the tree
        const findFileInTree = (items: TreeItem[], id: string): TreeItem | null => {
          for (const item of items) {
            if (item.id === id) return item;
            if (item.children) {
              const found = findFileInTree(item.children, id);
              if (found) return found;
            }
          }
          return null;
        };
        
        const selectedFile = findFileInTree(fileTree, selectedFileId);
        if (!selectedFile) return null;
        
        return (
          <Card className="m-2 mt-0">
            <CardContent className="p-2">
              <div className="text-xs space-y-1">
                <div className="font-medium">{selectedFile.name}</div>
                <div className="text-muted-foreground">
                  {isFile(selectedFile) ? "Document" : "Folder"}
                </div>
                {selectedFile.tags && selectedFile.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedFile.tags.map((tag) => (
                      <Badge
                        key={tag}
                        variant="outline"
                        className="text-xs px-1 py-0 h-auto"
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        );
      })()}
    </div>
  );
}