export interface FileNode {
  id: string
  name: string
  type: 'file' | 'folder'
  children?: FileNode[]
  tags?: string[]
  hasUnsavedChanges?: boolean
  collapsed?: boolean
  documentId?: string // ID of associated document for files
}

export interface FileTreeItemProps {
  node: FileNode
  level: number
  onFileSelect: (fileId: string, fileName: string, documentId?: string) => void
  searchQuery?: string
}