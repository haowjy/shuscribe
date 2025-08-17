// Helper function to highlight search matches
export function highlightMatch(text: string, query: string) {
  if (!query.trim()) return text
  
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
  const parts = text.split(regex)
  
  return (
    <span>
      {parts.map((part, index) => 
        regex.test(part) ? (
          <mark key={index} className="bg-accent/30 text-accent-foreground px-0 rounded-sm">
            {part}
          </mark>
        ) : (
          part
        )
      )}
    </span>
  )
}