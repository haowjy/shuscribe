export interface Tag {
  id: string;
  name: string;
  color?: string;
  icon?: string;
}

export interface BaseFileItem {
  id: string;
  name: string;
  tags?: Tag[];
  icon?: string; // Icon name for the file/folder
}

export interface FileItem extends BaseFileItem {
  type: "file";
  document_id: string; // Files must have a document reference
  children?: never; // Files cannot have children
}

export interface FolderItem extends BaseFileItem {
  type: "folder";
  children?: TreeItem[];
  document_id?: never; // Folders cannot have document references
}

export type TreeItem = FileItem | FolderItem;

// Type guards
export function isFile(item: TreeItem | undefined): item is FileItem {
  return item?.type === "file";
}

export function isFolder(item: TreeItem | undefined): item is FolderItem {
  return item?.type === "folder";
}

// Validation functions
export function validateFileItem(item: any): item is FileItem {
  return (
    item &&
    typeof item === "object" &&
    item.type === "file" &&
    typeof item.document_id === "string" &&
    !item.children
  );
}

export function validateFolderItem(item: any): item is FolderItem {
  return (
    item &&
    typeof item === "object" &&
    item.type === "folder" &&
    !item.document_id &&
    (!item.children || Array.isArray(item.children))
  );
}

export function validateTag(tag: any): tag is Tag {
  return (
    tag &&
    typeof tag === "object" &&
    typeof tag.id === "string" &&
    typeof tag.name === "string" &&
    tag.name.length > 0 &&
    (tag.color === undefined || typeof tag.color === "string") &&
    (tag.icon === undefined || typeof tag.icon === "string")
  );
}

export function cleanTags(tags: any[]): Tag[] {
  if (!Array.isArray(tags)) {
    return [];
  }
  return tags.filter(validateTag);
}

export function validateTreeItem(item: any): item is TreeItem {
  const isValid = validateFileItem(item) || validateFolderItem(item);
  if (isValid && item.tags) {
    // Clean invalid tags
    item.tags = cleanTags(item.tags);
  }
  return isValid;
}

export function findItemById(id: string, items: TreeItem[]): TreeItem | undefined {
  for (const item of items) {
    if (item.id === id) {
      return item;
    }
    if (isFolder(item) && item.children) {
      const found = findItemById(id, item.children);
      if (found) return found;
    }
  }
  return undefined;
}

// Helper function to find only files
export function findFileById(id: string, items: TreeItem[]): FileItem | undefined {
  const item = findItemById(id, items);
  return isFile(item) ? item : undefined;
}

// Helper function to find only folders
export function findFolderById(id: string, items: TreeItem[]): FolderItem | undefined {
  const item = findItemById(id, items);
  return isFolder(item) ? item : undefined;
}