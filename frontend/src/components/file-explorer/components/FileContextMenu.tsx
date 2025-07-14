"use client";

import React, { useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { 
  File, 
  FileText,
  Settings,
  Tag,
  Edit,
  Copy,
  Trash2,
  Link,
  MessageSquare,
  FolderPlus
} from "lucide-react";
import { isFolder } from "@/data/file-tree";
import { FileContextMenuProps, FileAction } from "../types/file-explorer";

interface Position {
  x: number;
  y: number;
}

export function FileContextMenu({ item, isOpen, position: initialPosition, onClose, onAction }: FileContextMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = React.useState<Position>(initialPosition || { x: 0, y: 0 });

  const handleAction = (action: string) => {
    onAction(action as FileAction);
    onClose();
  };

  // Update position when props change and handle clicks outside
  useEffect(() => {
    if (initialPosition) {
      setPosition(initialPosition);
    }
  }, [initialPosition]);

  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('click', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('click', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const menuContent = (
    <div
      ref={menuRef}
      className="fixed z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95"
      style={{
        left: position.x,
        top: position.y,
        maxWidth: '14rem',
      }}
    >
      {isFolder(item) ? (
        // Folder context menu
        <>
          <div 
            className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
            onClick={() => handleAction("new-file")}
          >
            <FileText className="mr-2 h-4 w-4" />
            New File
          </div>
          <div 
            className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
            onClick={() => handleAction("new-folder")}
          >
            <FolderPlus className="mr-2 h-4 w-4" />
            New Folder
          </div>
          <div className="-mx-1 my-1 h-px bg-muted" />
        </>
      ) : (
        // File context menu
        <>
          <div 
            className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
            onClick={() => handleAction("open")}
          >
            <File className="mr-2 h-4 w-4" />
            Open
          </div>
          <div 
            className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
            onClick={() => handleAction("copy-reference")}
          >
            <Link className="mr-2 h-4 w-4" />
            Copy Reference
          </div>
          <div 
            className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
            onClick={() => handleAction("add-to-chat")}
          >
            <MessageSquare className="mr-2 h-4 w-4" />
            Add to Chat
          </div>
          <div className="-mx-1 my-1 h-px bg-muted" />
        </>
      )}
      
      {/* Common actions for both files and folders */}
      <div 
        className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
        onClick={() => handleAction("edit-metadata")}
      >
        <Settings className="mr-2 h-4 w-4" />
        Edit Metadata
      </div>
      <div 
        className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
        onClick={() => handleAction("quick-tag-edit")}
      >
        <Tag className="mr-2 h-4 w-4" />
        Quick Tag Edit
      </div>
      <div className="-mx-1 my-1 h-px bg-muted" />
      <div 
        className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
        onClick={() => handleAction("rename")}
      >
        <Edit className="mr-2 h-4 w-4" />
        Rename
      </div>
      <div 
        className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
        onClick={() => handleAction("copy")}
      >
        <Copy className="mr-2 h-4 w-4" />
        Copy
      </div>
      <div className="-mx-1 my-1 h-px bg-muted" />
      <div 
        className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground text-destructive focus:text-destructive"
        onClick={() => handleAction("delete")}
      >
        <Trash2 className="mr-2 h-4 w-4" />
        Delete
      </div>
    </div>
  );

  // Use portal to render outside the scrollable area
  return typeof window !== 'undefined' ? createPortal(menuContent, document.body) : null;
}