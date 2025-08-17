export interface FileNode {
  id: string
  name: string
  type: 'file' | 'folder'
  children?: FileNode[]
  tags?: string[]
  hasUnsavedChanges?: boolean
}

export interface FileTreeItemProps {
  node: FileNode
  level: number
  onFileSelect: (fileId: string, fileName: string) => void
  searchQuery?: string
}