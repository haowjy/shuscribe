"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, File, Folder, FolderOpen } from "lucide-react";
import { cn } from "@/lib/utils";

interface FileItem {
  id: string;
  name: string;
  type: "file" | "folder";
  children?: FileItem[];
  tags?: string[];
}

const mockFileTree: FileItem[] = [
  {
    id: "1",
    name: "characters",
    type: "folder",
    children: [
      {
        id: "2",
        name: "protagonists",
        type: "folder",
        children: [
          { id: "3", name: "elara.md", type: "file", tags: ["fire-magic", "trauma"] },
          { id: "4", name: "marcus.md", type: "file", tags: ["earth-magic", "mentor"] },
        ],
      },
      {
        id: "5",
        name: "antagonists",
        type: "folder",
        children: [
          { id: "6", name: "shadow-lord.md", type: "file", tags: ["dark-magic", "villain"] },
        ],
      },
    ],
  },
  {
    id: "7",
    name: "locations",
    type: "folder",
    children: [
      { id: "8", name: "capital-city.md", type: "file", tags: ["urban", "politics"] },
      { id: "9", name: "ancient-temple.md", type: "file", tags: ["mystical", "ruins"] },
    ],
  },
  {
    id: "10",
    name: "timeline",
    type: "folder",
    children: [
      { id: "11", name: "main-story.md", type: "file" },
      { id: "12", name: "backstory.md", type: "file" },
    ],
  },
  {
    id: "13",
    name: "chapters",
    type: "folder",
    children: [
      { id: "14", name: "chapter-01.md", type: "file" },
      { id: "15", name: "chapter-02.md", type: "file" },
      { id: "16", name: "chapter-03.md", type: "file" },
    ],
  },
];

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
      <div
        className={cn(
          "flex items-center gap-1 px-1 py-1 text-sm cursor-pointer hover:bg-accent rounded",
          "group"
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
        <span className="flex-1 truncate">{item.name}</span>
        {item.tags && item.tags.length > 0 && (
          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {item.tags.slice(0, 2).map((tag) => (
              <span
                key={tag}
                className="text-xs bg-secondary text-secondary-foreground px-1 rounded"
              >
                {tag}
              </span>
            ))}
            {item.tags.length > 2 && (
              <span className="text-xs text-muted-foreground">+{item.tags.length - 2}</span>
            )}
          </div>
        )}
      </div>
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
        <div className="mt-2 p-2 bg-secondary/50 rounded text-xs text-muted-foreground">
          Selected: {selectedFile.name}
        </div>
      )}
    </div>
  );
}