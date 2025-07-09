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
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator
} from "@/components/ui/dropdown-menu";
import { FileItem } from "@/data/file-tree";
import { useProjectData } from "@/lib/query/hooks";
import { ProjectData } from "@/types/project";
import { cn } from "@/lib/utils";

// No conversion needed - API already returns FileItem format

interface FileTreeItemProps {
  item: FileItem;
  depth: number;
  selectedFileId?: string;
  onFileSelect?: (file: FileItem) => void;
  onFileAction?: (action: string, file: FileItem) => void;
}

function FileTreeItem({ item, depth, selectedFileId, onFileSelect, onFileAction }: FileTreeItemProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const isSelected = selectedFileId === item.id;

  const handleClick = () => {
    if (item.type === "folder") {
      setIsExpanded(!isExpanded);
    } else {
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
        {item.type === "folder" ? (
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
            {item.type === "folder" ? (
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
      {item.type === "folder" && isExpanded && item.children && (
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
  onFileSelect?: (file: FileItem) => void;
}

export function FileExplorer({ projectId, onFileSelect }: FileExplorerProps) {
  const { data: projectData, isLoading, error } = useProjectData(projectId);
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);
  

  const handleFileSelect = (file: FileItem) => {
    setSelectedFile(file);
    onFileSelect?.(file);
  };

  const handleFileAction = (action: string, file: FileItem) => {
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
    return (
      <div className="h-full flex items-center justify-center p-4">
        <div className="text-center">
          <p className="text-xs text-destructive mb-1">Failed to load files</p>
          <p className="text-xs text-muted-foreground">{error.message}</p>
        </div>
      </div>
    );
  }

  // FileTree is already in the correct format
  const fileTree = projectData?.fileTree || [];

  return (
    <div className="h-full flex flex-col">
      {/* Header with actions */}
      <div className="flex items-center justify-between p-2 border-b">
        <span className="text-sm font-medium text-muted-foreground">
          {projectData?.title || 'Project Files'}
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
      <div className="flex-1 overflow-y-auto overflow-x-hidden p-1">
        {fileTree.map((item) => (
          <FileTreeItem
            key={item.id}
            item={item}
            depth={0}
            selectedFileId={selectedFile?.id}
            onFileSelect={handleFileSelect}
            onFileAction={handleFileAction}
          />
        ))}
      </div>
      
      {/* File Info */}
      {selectedFile && (
        <Card className="m-2 mt-0">
          <CardContent className="p-2">
            <div className="text-xs space-y-1">
              <div className="font-medium">{selectedFile.name}</div>
              <div className="text-muted-foreground">
                {selectedFile.type === "file" ? "Document" : "Folder"}
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
      )}
    </div>
  );
}