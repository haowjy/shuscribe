import { TreeItem } from "@/data/file-tree";

export interface FileExplorerProps {
  projectId: string;
  onFileClick: (fileId: string) => void;
  paneWidthPercentage?: number; // Real-time pane width as percentage of screen
}

export interface FileTreeItemProps {
  item: TreeItem;
  depth: number;
  selectedFileId?: string | null;
  onFileSelect?: (file: TreeItem) => void;
  onFileAction?: (action: string, file: TreeItem) => void;
  onTagClick?: (tagName: string) => void;
  maxVisibleTags?: number; // Number of tags to show (calculated by parent)
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