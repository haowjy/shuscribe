import { useMemo } from 'react';
import { TreeItem } from '@/types/api';
import { 
  ReferenceItem, 
  transformFileTreeToReferences, 
  filterReferences, 
  sortReferencesByRelevance 
} from '@/data/reference-items';

/**
 * Hook to get referenceable items from provided file tree
 */
export function useReferenceItems(fileTree: TreeItem[] = []) {
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
 * Hook to get suggestion items for Tiptap suggestion utility with debouncing
 */
export function useSuggestionItems(fileTree: TreeItem[] = []) {
  const { getFilteredReferences } = useReferenceItems(fileTree);

  const getSuggestionItems = useMemo(() => {
    let lastQuery = '';
    let lastResults: ReferenceItem[] = [];
    
    return ({ query }: { query: string }) => {
      // Remove the '@' character from the query
      const cleanQuery = query.replace(/^@/, '');
      
      // Cache results for same query to reduce processing
      if (cleanQuery === lastQuery) {
        return lastResults;
      }
      
      // Short queries should return fewer results for performance
      const maxResults = cleanQuery.length < 2 ? 5 : 10;
      
      // Get filtered references
      const references = getFilteredReferences(cleanQuery);
      
      // Limit suggestions for performance
      const results = references.slice(0, maxResults);
      
      // Cache results
      lastQuery = cleanQuery;
      lastResults = results;
      
      return results;
    };
  }, [getFilteredReferences]);

  return {
    getSuggestionItems,
  };
}