// Utility functions for formatting data

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