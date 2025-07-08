"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, File, Folder, FolderOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { FileItem, mockFileTree } from "@/data/file-tree";
import { cn } from "@/lib/utils";

interface FileTreeItemProps {
  item: FileItem;
  depth: number;
  onFileSelect?: (file: FileItem) => void;
}

function FileTreeItem({ item, depth, onFileSelect }: FileTreeItemProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  const handleClick = () => {
    if (item.type === "folder") {
      setIsExpanded(!isExpanded);
    } else {
      onFileSelect?.(item);
    }
  };

  return (
    <div>
      <Button
        variant="ghost"
        className={cn(
          "w-full justify-start gap-1 px-1 py-1 h-auto text-sm group",
          "hover:bg-accent"
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
      {item.type === "folder" && isExpanded && item.children && (
        <div>
          {item.children.map((child) => (
            <FileTreeItem
              key={child.id}
              item={child}
              depth={depth + 1}
              onFileSelect={onFileSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function FileExplorer() {
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-auto">
        {mockFileTree.map((item) => (
          <FileTreeItem
            key={item.id}
            item={item}
            depth={0}
            onFileSelect={setSelectedFile}
          />
        ))}
      </div>
      {selectedFile && (
        <Card className="mt-2">
          <CardContent className="p-2">
            <div className="text-xs text-muted-foreground">
              Selected: {selectedFile.name}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}