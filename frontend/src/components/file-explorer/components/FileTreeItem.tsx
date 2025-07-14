"use client";

import React, { useState, useRef } from "react";
import useResizeObserver from "@react-hook/resize-observer";
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
  onTagClick
}: FileTreeItemProps) {
  // Button width tracking with ResizeObserver hook - watch actual flex container
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [containerWidth, setContainerWidth] = useState(200);
  
  const [isExpanded, setIsExpanded] = useState(true);
  const [contextMenuOpen, setContextMenuOpen] = useState(false);
  const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });
  const isSelected = selectedFileId === item.id;
  
  // Watch the Button element directly - where flex competition happens
  useResizeObserver(buttonRef, (entry) => {
    const width = entry.contentRect.width;
    setContainerWidth(width);
  });

  const handleClick = () => {
    if (isFolder(item)) {
      setIsExpanded(!isExpanded);
    } else if (isFile(item)) {
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
    onTagClick?.(tagName);
  };

  // Calculate responsive styles - prioritize tag visibility over text
  const getResponsiveState = () => {
    // Tags get priority - reduce count early to avoid panel collapse oscillation
    // Start collapsing well before panel collapse threshold (~80-120px)
    // Note: maxVisible=3 can show up to 4 tags when there are exactly 4
    if (containerWidth > 260) {
      return { maxVisibleTags: 3, breakpoint: 'lg' as const, indentScale: 1.0 };
    } else if (containerWidth > 180) {
      return { maxVisibleTags: 2, breakpoint: 'md' as const, indentScale: 0.9 };
    } else if (containerWidth > 140) {
      return { maxVisibleTags: 1, breakpoint: 'sm' as const, indentScale: 0.8 };
    } else {
      // Hide tags well before panel collapse to prevent oscillation
      return { maxVisibleTags: 0, breakpoint: 'xs' as const, indentScale: 0.7 };
    }
  };
  
  const { maxVisibleTags, breakpoint, indentScale } = getResponsiveState();
  const baseIndent = depth * 12 + 4;
  const scaledIndent = baseIndent * indentScale;
  const showTags = maxVisibleTags > 0;
  const isNarrow = breakpoint === 'xs' || breakpoint === 'sm';
  
  
  return (
    <div>
      <div className="group w-full overflow-hidden" onContextMenu={handleRightClick}>
        <Button
          ref={buttonRef}
          variant="tree-item"
          className={cn(
            "w-full h-auto text-sm flex items-center justify-start overflow-hidden",
            "transition-colors gap-0",
            isSelected && "bg-accent",
            isNarrow ? "px-0.5 py-0.5" : "px-1 py-1"
          )}
          style={{ paddingLeft: `${scaledIndent}px` }}
          onClick={handleClick}
        >
          {/* File/Folder Icons - fixed width, never shrink */}
          <div className="flex items-center flex-shrink-0">
            {isFolder(item) ? (
              <>
                {isExpanded ? (
                  <ChevronDown className={cn(
                    "text-muted-foreground flex-shrink-0",
                    isNarrow ? "h-2.5 w-2.5 mr-0.5" : "h-3 w-3 mr-1"
                  )} />
                ) : (
                  <ChevronRight className={cn(
                    "text-muted-foreground flex-shrink-0",
                    isNarrow ? "h-2.5 w-2.5 mr-0.5" : "h-3 w-3 mr-1"
                  )} />
                )}
                {isExpanded ? (
                  <FolderOpen className={cn(
                    "text-blue-500 flex-shrink-0",
                    isNarrow ? "h-3 w-3" : "h-4 w-4"
                  )} />
                ) : (
                  <Folder className={cn(
                    "text-blue-500 flex-shrink-0",
                    isNarrow ? "h-3 w-3" : "h-4 w-4"
                  )} />
                )}
              </>
            ) : (
              <>
                <div className={cn(
                  "flex-shrink-0",
                  isNarrow ? "w-2.5 mr-0.5" : "w-3 mr-1"
                )} />
                <File className={cn(
                  "text-muted-foreground flex-shrink-0",
                  isNarrow ? "h-3 w-3" : "h-4 w-4"
                )} />
              </>
            )}
          </div>
          
          {/* File Name - gets compressed when tags need space */}
          <Tooltip>
            <TooltipTrigger asChild>
              <span className={cn(
                "flex-1 text-left cursor-inherit overflow-hidden",
                "whitespace-nowrap text-ellipsis min-w-0",
                "shrink-[999]",
                isNarrow && "text-xs"
              )}
              style={{ 
                minWidth: "0px",
                flexShrink: 999
              }}
              >
                {item.name}
              </span>
            </TooltipTrigger>
            <TooltipContent side="bottom" align="start" className="max-w-80">
              <div className="space-y-1">
                <div className="font-medium">{item.name}</div>
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
          
          {/* Tags section - ALWAYS visible, pushes filename to truncate */}
          {showTags && (
            <div className="ml-2">
              <TagDisplay
                tags={item.tags}
                maxVisible={maxVisibleTags}
                onTagClick={handleTagClick}
              />
            </div>
          )}
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
            />
          ))}
        </>
      )}
    </div>
  );
}