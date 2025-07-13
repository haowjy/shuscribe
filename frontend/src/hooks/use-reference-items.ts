import { useMemo } from 'react';
import { FileTreeItem } from '@/types/api';
import { 
  ReferenceItem, 
  transformFileTreeToReferences, 
  filterReferences, 
  sortReferencesByRelevance 
} from '@/data/reference-items';

/**
 * Hook to get referenceable items from provided file tree
 */
export function useReferenceItems(fileTree: FileTreeItem[] = []) {
  const allReferences = useMemo(() => {
    if (fileTree.length === 0) return [];
    return transformFileTreeToReferences(fileTree);
  }, [fileTree]);

  const getFilteredReferences = useMemo(() => {
    return (query: string): ReferenceItem[] => {
      const filtered = filterReferences(allReferences, query);
      return sortReferencesByRelevance(filtered, query);
    };
  }, [allReferences]);

  return {
    allReferences,
    getFilteredReferences,
  };
}

/**
 * Hook to get suggestion items for Tiptap suggestion utility
 */
export function useSuggestionItems(fileTree: FileTreeItem[] = []) {
  const { getFilteredReferences } = useReferenceItems(fileTree);

  const getSuggestionItems = useMemo(() => {
    return ({ query }: { query: string }) => {
      // Remove the '@' character from the query
      const cleanQuery = query.replace(/^@/, '');
      
      // Get filtered references
      const references = getFilteredReferences(cleanQuery);
      
      // Limit to 10 suggestions for performance
      return references.slice(0, 10);
    };
  }, [getFilteredReferences]);

  return {
    getSuggestionItems,
  };
}