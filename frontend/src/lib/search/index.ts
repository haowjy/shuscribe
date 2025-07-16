// Client-side search index for instant @-reference autocomplete

import { ProjectData, FileItem } from '@/types/project';

export interface SearchItem {
  id: string;
  title: string;
  path: string;
  type: 'file' | 'tag';
  documentId?: string;
  tags?: string[];
  score?: number; // For search result ranking
}

export interface SearchIndex {
  files: SearchItem[];
  tags: SearchItem[];
  all: SearchItem[];
}

// Build searchable index from project data
export function buildSearchIndex(projectData: ProjectData): SearchIndex {
  const files: SearchItem[] = [];
  const tagCounts: Record<string, number> = {};
  const tagDocuments: Record<string, string[]> = {};

  // Extract file references from file tree
  function extractFiles(nodes: FileItem[]) {
    for (const node of nodes) {
      if (node.type === 'file' && node.documentId) {
        const document = projectData.documents.find(d => d.id === node.documentId);
        files.push({
          id: node.id,
          title: document?.title || node.name,
          path: node.path || node.name,
          type: 'file',
          documentId: node.documentId,
          tags: document?.tags || [],
        });
      } else if (node.type === 'folder' && node.children) {
        extractFiles(node.children);
      }
    }
  }

  extractFiles(projectData.fileTree);

  // Count tags and track which documents have them
  for (const document of projectData.documents) {
    for (const tag of document.tags) {
      tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      if (!tagDocuments[tag]) {
        tagDocuments[tag] = [];
      }
      tagDocuments[tag].push(document.id);
    }
  }

  // Create tag search items
  const tags: SearchItem[] = Object.entries(tagCounts).map(([tag, count]) => ({
    id: `tag-${tag}`,
    title: `${tag} (${count} documents)`,
    path: `@${tag}`,
    type: 'tag' as const,
    tags: [tag],
  }));

  return {
    files,
    tags,
    all: [...files, ...tags],
  };
}

// Fuzzy search function with scoring
export function fuzzySearch(
  query: string,
  items: SearchItem[],
  maxResults: number = 10
): SearchItem[] {
  if (!query.trim()) return [];

  const searchQuery = query.toLowerCase();
  const results: SearchItem[] = [];

  for (const item of items) {
    const score = calculateScore(searchQuery, item);
    if (score > 0) {
      results.push({ ...item, score });
    }
  }

  // Sort by score (higher is better) and take top results
  return results
    .sort((a, b) => (b.score || 0) - (a.score || 0))
    .slice(0, maxResults);
}

// Calculate search score for an item
function calculateScore(query: string, item: SearchItem): number {
  const title = item.title.toLowerCase();
  const path = item.path.toLowerCase();
  let score = 0;

  // Exact title match gets highest score
  if (title === query) {
    score += 100;
  }
  // Title starts with query
  else if (title.startsWith(query)) {
    score += 80;
  }
  // Title contains query
  else if (title.includes(query)) {
    score += 60;
  }

  // Path matching (lower priority)
  if (path.includes(query)) {
    score += 30;
  }

  // Tag matching
  if (item.tags) {
    for (const tag of item.tags) {
      const tagLower = tag.toLowerCase();
      if (tagLower === query) {
        score += 70;
      } else if (tagLower.includes(query)) {
        score += 40;
      }
    }
  }

  // Bonus for file type (prefer files over tags for @-references)
  if (item.type === 'file') {
    score += 10;
  }

  // Fuzzy matching for partial character matches
  if (score === 0) {
    const fuzzyScore = calculateFuzzyScore(query, title);
    if (fuzzyScore > 0.5) {
      score = Math.floor(fuzzyScore * 30); // Max 30 points for fuzzy match
    }
  }

  return score;
}

// Simple fuzzy matching algorithm
function calculateFuzzyScore(query: string, text: string): number {
  if (query.length === 0) return 1;
  if (text.length === 0) return 0;

  let queryIndex = 0;
  let textIndex = 0;
  let matches = 0;

  while (queryIndex < query.length && textIndex < text.length) {
    if (query[queryIndex] === text[textIndex]) {
      matches++;
      queryIndex++;
    }
    textIndex++;
  }

  return matches / query.length;
}

// Search for @-references with prefix
export function searchReferences(
  query: string,
  index: SearchIndex,
  maxResults: number = 8
): SearchItem[] {
  // Remove @ prefix if present
  const cleanQuery = query.replace(/^@/, '');
  
  if (!cleanQuery.trim()) {
    // Return most common items when no query
    return [...index.files.slice(0, 4), ...index.tags.slice(0, 4)]
      .sort((a, b) => a.title.localeCompare(b.title))
      .slice(0, maxResults);
  }

  return fuzzySearch(cleanQuery, index.all, maxResults);
}

// Hook for managing search index
export function useSearchIndex(projectData: ProjectData | undefined) {
  const index = projectData ? buildSearchIndex(projectData) : null;
  
  return {
    index,
    search: (query: string, maxResults?: number) => 
      index ? searchReferences(query, index, maxResults) : [],
  };
}