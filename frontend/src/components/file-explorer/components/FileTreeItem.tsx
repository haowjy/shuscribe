"use client";

import React, { useState } from "react";
import { 
  ChevronDown, 
  ChevronRight, 
  File, 
  Folder, 
  FolderOpen 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { isFile, isFolder } from "@/data/file-tree";
import { cn } from "@/lib/utils";
import { FileTreeItemProps } from "../types/file-explorer";
import { TagDisplay } from "./TagDisplay";
import { FileContextMenu } from "./FileContextMenu";

export function FileTreeItem({ 
  item, 
  depth, 
  selectedFileId, 
  onFileSelect, 
  onFileAction,
  onTagClick,
  maxVisibleTags = 2 // Default to 2 tags if not specified
}: FileTreeItemProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [contextMenuOpen, setContextMenuOpen] = useState(false);
  const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });
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
    setContextMenuPosition({ x: e.clientX, y: e.clientY });
    setContextMenuOpen(true);
  };

  const handleTagClick = (tagName: string) => {
    console.log('🏷️ [FileTreeItem] Tag clicked:', tagName);
    onTagClick?.(tagName);
  };

  return (
    <div>
      <div className="group w-full overflow-hidden" onContextMenu={handleRightClick}>
        <Button
          variant="ghost"
          className={cn(
            "w-full max-w-full justify-between items-center gap-2 px-1 py-1 h-auto text-sm",
            "hover:bg-accent relative overflow-hidden",
            isSelected && "bg-accent"
          )}
          style={{ paddingLeft: `${depth * 12 + 4}px` }}
          onClick={handleClick}
        >
          {/* Left section: Icons and filename */}
          <div className="flex items-center gap-1 flex-1 min-w-0 overflow-hidden">
            {/* File/Folder Icon */}
            {isFolder(item) ? (
              <>
                {isExpanded ? (
                  <ChevronDown className="h-3 w-3 text-muted-foreground flex-shrink-0" />
                ) : (
                  <ChevronRight className="h-3 w-3 text-muted-foreground flex-shrink-0" />
                )}
                {isExpanded ? (
                  <FolderOpen className="h-4 w-4 text-blue-500 flex-shrink-0" />
                ) : (
                  <Folder className="h-4 w-4 text-blue-500 flex-shrink-0" />
                )}
              </>
            ) : (
              <>
                <div className="w-3 flex-shrink-0" />
                <File className="h-4 w-4 text-muted-foreground flex-shrink-0" />
              </>
            )}
            
            {/* File Name with smart truncation and metadata tooltip */}
            <Tooltip>
              <TooltipTrigger asChild>
                <span className="flex-1 truncate text-left min-w-0 cursor-inherit">
                  {item.name}
                </span>
              </TooltipTrigger>
              <TooltipContent side="bottom" align="start" className="max-w-80">
                <div className="space-y-1">
                  <div className="font-medium">{item.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {item.path}
                  </div>
                  {item.tags && item.tags.length > 0 && (
                    <div className="text-xs">
                      <span className="text-muted-foreground">Tags: </span>
                      {item.tags.map(tag => tag.name).filter(Boolean).join(', ')}
                    </div>
                  )}
                  {isFile(item) && (
                    <div className="text-xs text-muted-foreground">
                      File • Click to open
                    </div>
                  )}
                  {isFolder(item) && (
                    <div className="text-xs text-muted-foreground">
                      Folder • {item.children?.length || 0} items
                    </div>
                  )}
                </div>
              </TooltipContent>
            </Tooltip>
          </div>
          
          {/* Right section: Tags - always floats right with consistent spacing */}
          <div className="flex-shrink-0 max-w-[40%] overflow-hidden">
            <TagDisplay
              tags={item.tags}
              maxVisible={maxVisibleTags}
              onTagClick={handleTagClick}
            />
          </div>
        </Button>
      </div>
      
      {/* Context Menu */}
      <FileContextMenu
        item={item}
        isOpen={contextMenuOpen}
        position={contextMenuPosition}
        onClose={() => setContextMenuOpen(false)}
        onAction={handleAction}
      />
      
      {/* Render children for folders */}
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
              onTagClick={onTagClick}
              maxVisibleTags={maxVisibleTags}
            />
          ))}
        </>
      )}
    </div>
  );
}