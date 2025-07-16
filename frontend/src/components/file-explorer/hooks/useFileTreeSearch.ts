import { useMemo } from 'react';
import { TreeItem, isFile, isFolder, Tag } from '@/data/file-tree';
import { FileSearchState } from '../types/file-explorer';

interface SearchResult {
  filteredFileTree: TreeItem[];
  allTags: Tag[];
}

export function useFileTreeSearch(
  fileTree: TreeItem[],
  searchState: FileSearchState
): SearchResult {
  return useMemo(() => {
    // Extract all tags for filtering
    const tagMap: Record<string, { tag: Tag; count: number }> = {};
    
    const countTags = (items: TreeItem[]) => {
      items.forEach(item => {
        if (item.tags) {
          item.tags.forEach(tag => {
            if (!tagMap[tag.id]) {
              tagMap[tag.id] = { tag, count: 0 };
            }
            tagMap[tag.id].count += 1;
          });
        }
        if (isFolder(item) && item.children) {
          countTags(item.children);
        }
      });
    };
    
    countTags(fileTree);
    
    const allTags = Object.values(tagMap).map(({ tag }) => tag);

    // Filter file tree
    if (!searchState.query && 
        searchState.tagFilters.length === 0 && 
        searchState.statusFilter === 'all') {
      return { filteredFileTree: fileTree, allTags };
    }
    
    const filterItems = (items: TreeItem[]): TreeItem[] => {
      return items.reduce<TreeItem[]>((acc, item) => {
        const matchesSearch = !searchState.query || 
          item.name.toLowerCase().includes(searchState.query.toLowerCase());
        
        const matchesTags = searchState.tagFilters.length === 0 ||
          (item.tags && searchState.tagFilters.some(filter => 
            item.tags!.some(tag => tag.name === filter)
          ));

        // Filter by file/folder type
        const matchesType = searchState.statusFilter === 'all' ||
          (searchState.statusFilter === 'files' && isFile(item)) ||
          (searchState.statusFilter === 'folders' && isFolder(item));
        
        let filteredChildren: TreeItem[] = [];
        if (isFolder(item) && item.children) {
          filteredChildren = filterItems(item.children);
        }
        
        // Include item if it matches all criteria or has matching children
        if ((matchesSearch && matchesTags && matchesType) || filteredChildren.length > 0) {
          if (isFolder(item)) {
            acc.push({
              ...item,
              children: filteredChildren,
            });
          } else {
            // For files, ensure no 'children' property is added
            acc.push(item);
          }
        }
        
        return acc;
      }, []);
    };
    
    const filteredFileTree = filterItems(fileTree);
    
    return { filteredFileTree, allTags };
  }, [fileTree, searchState.query, searchState.tagFilters, searchState.statusFilter]);
}