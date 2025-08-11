'use client'

import { Badge } from '@/components/ui/badge'

interface ApiTag {
  id: string
  name: string
  icon?: string | null
  color?: string | null
}

interface StatusBadgeProps {
  tag: string | ApiTag
  className?: string
}

export function StatusBadge({ tag, className = '' }: StatusBadgeProps) {
  if (!tag) return null

  const tagName = typeof tag === 'string' ? tag : tag.name
  const tagColor = typeof tag === 'object' && tag.color ? tag.color : undefined

  const getBadgeVariant = (name: string) => {
    const lowerName = name.toLowerCase()
    if (lowerName.includes('complete') || lowerName.includes('done')) return 'default'
    if (lowerName.includes('draft') || lowerName.includes('wip')) return 'secondary'
    if (lowerName.includes('review')) return 'outline'
    return 'secondary'
  }

  return (
    <Badge 
      variant={getBadgeVariant(tagName)}
      className={`text-xs px-2 py-0.5 ${className}`}
      style={tagColor ? { backgroundColor: tagColor + '20', color: tagColor, borderColor: tagColor + '40' } : undefined}
    >
      {tagName}
    </Badge>
  )
}