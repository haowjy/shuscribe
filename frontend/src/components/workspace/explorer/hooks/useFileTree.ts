import { useMemo } from 'react'
import type { FileNode } from '../types'

// Mock file tree data - in a real app this would come from an API or state management
const mockFileTree: FileNode[] = [
  {
    id: 'characters',
    name: 'characters',
    type: 'folder',
    children: [
      {
        id: 'protagonists',
        name: 'protagonists',
        type: 'folder',
        children: [
          {
            id: 'elara',
            name: 'elara.md',
            type: 'file',
            tags: ['fire-magic'],
            hasUnsavedChanges: true
          },
          {
            id: 'thomas',
            name: 'thomas.md',
            type: 'file',
            tags: ['mentor']
          }
        ]
      },
      {
        id: 'antagonists',
        name: 'antagonists',
        type: 'folder',
        children: [
          {
            id: 'shadow-lord',
            name: 'shadow-lord.md',
            type: 'file',
            tags: ['dark-magic', 'final-boss']
          }
        ]
      }
    ]
  },
  {
    id: 'world',
    name: 'world',
    type: 'folder',
    children: [
      {
        id: 'locations',
        name: 'locations',
        type: 'folder',
        children: [
          {
            id: 'thornfield-manor',
            name: 'thornfield-manor.md',
            type: 'file',
            tags: ['gothic', 'mysterious']
          }
        ]
      }
    ]
  },
  {
    id: 'documents',
    name: 'documents',
    type: 'folder',
    children: [
      {
        id: 'chapter-01',
        name: 'chapter-01.md',
        type: 'file',
        hasUnsavedChanges: true
      },
      {
        id: 'outline',
        name: 'outline.md',
        type: 'file'
      }
    ]
  }
]

export function useFileTree() {
  return useMemo(() => mockFileTree, [])
}