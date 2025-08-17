/**
 * Formats a tab label for ProseMirror docs: remove file extensions and
 * optional type prefixes to show a clean document title.
 */
export function formatTabLabel(name: string): string {
  if (!name) return name

  // Strip any extension-like suffix (e.g., .md, .txt) since these are not files
  
  let formatted = name.trim()
  
  formatted = formatted.replace(/\.[A-Za-z0-9_-]{1,8}$/i, '')
  
  // Handle any accidental type prefixes (e.g., "markdown:", "text:")
  const prefixMatch = formatted.match(/^[a-z]+:\s*(.+)$/i)
  if (prefixMatch) {
    formatted = prefixMatch[1]
  }
  
  return formatted.trim() || name // Fallback to original name if nothing remains
}