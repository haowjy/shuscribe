// Central export file for all mock data
export * from './projects';
export * from './ai-modes';
export * from './file-tree';
export * from './editor-tabs';

// Utility functions for formatting
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

export function formatNumber(num: number | undefined | null): string {
  if (num == null || num === undefined) {
    return '0';
  }
  return num.toLocaleString();
}