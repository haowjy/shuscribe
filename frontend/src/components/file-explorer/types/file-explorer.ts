import { TreeItem } from "@/data/file-tree";

export interface FileExplorerProps {
  projectId: string;
  onFileClick: (fileId: string) => void;
  // Removed paneWidthPercentage - FileTreeItems now handle responsiveness internally
}

export interface FileTreeItemProps {
  item: TreeItem;
  depth: number;
  selectedFileId?: string | null;
  onFileSelect?: (file: TreeItem) => void;
  onFileAction?: (action: string, file: TreeItem) => void;
  onTagClick?: (tagName: string) => void;
  // Removed responsive props - now handled internally with ResizeObserver
}

export interface TagDisplayProps {
  tags: TreeItem['tags'];
  maxVisible?: number;
  onTagClick?: (tagName: string) => void;
}

export interface FileSearchState {
  query: string;
  tagFilters: string[];
  statusFilter: 'all' | 'published' | 'draft';
  contentTypeFilter: string[];
}

export interface FileTreeState {
  expandedFolders: Set<string>;
  selectedItemId: string | null;
  searchState: FileSearchState;
}

export type FileAction = 
  | 'open'
  | 'copy-reference'
  | 'add-to-chat'
  | 'rename'
  | 'edit-metadata'
  | 'copy'
  | 'paste'
  | 'delete'
  | 'new-file'
  | 'new-folder';

export interface FileContextMenuProps {
  item: TreeItem;
  isOpen: boolean;
  position?: { x: number; y: number };
  onClose: () => void;
  onAction: (action: FileAction) => void;
}