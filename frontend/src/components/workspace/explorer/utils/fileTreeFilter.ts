import type { FileNode } from '../types'

// Recursive function to filter file tree based on search query
export function filterFileTree(nodes: FileNode[], query: string): FileNode[] {
  if (!query.trim()) return nodes
  
  const filteredNodes: FileNode[] = []
  
  for (const node of nodes) {
    const nodeMatches = node.name.toLowerCase().includes(query.toLowerCase())
    
    if (node.type === 'folder' && node.children) {
      const filteredChildren = filterFileTree(node.children, query)
      
      // Include folder if it matches or has matching children
      if (nodeMatches || filteredChildren.length > 0) {
        filteredNodes.push({
          ...node,
          children: filteredChildren.length > 0 ? filteredChildren : node.children
        })
      }
    } else if (node.type === 'file' && nodeMatches) {
      filteredNodes.push(node)
    }
  }
  
  return filteredNodes
}

// Count total files in filtered tree
export function countFilesInTree(nodes: FileNode[]): number {
  return nodes.reduce((count, node) => {
    const countFiles = (n: FileNode): number => {
      if (n.type === 'file') return 1
      return n.children?.reduce((acc, child) => acc + countFiles(child), 0) || 0
    }
    return count + countFiles(node)
  }, 0)
}