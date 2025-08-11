'use client'

import { useRouter } from 'next/navigation'
import { ProjectMetrics } from './ProjectMetrics'
import { StatusBadge } from './StatusBadge'
import { RelativeTime } from './RelativeTime'

interface ApiTag {
  id: string
  name: string
  icon?: string | null
  color?: string | null
}

interface ProjectListItemProps {
  id: string
  title: string
  description?: string
  wordCount: number
  documentCount: number
  tags: (string | ApiTag)[]
  updatedAt?: string
  onClick?: (id: string) => void
  className?: string
}

export function ProjectListItem({
  id,
  title,
  description,
  wordCount,
  documentCount,
  tags,
  updatedAt,
  onClick,
  className = ''
}: ProjectListItemProps) {
  const router = useRouter()

  const handleClick = () => {
    if (onClick) {
      onClick(id)
    } else {
      router.push(`/projects/${id}`)
    }
  }

  const truncateDescription = (text: string | undefined, maxLength: number = 100): string => {
    if (!text) return ''
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength).trim() + '...'
  }

  const primaryTag = tags?.[0]

  return (
    <div
      className={`group p-4 rounded-md border border-transparent hover:border-border hover:bg-accent/50 cursor-pointer transition-all duration-200 ${className}`}
      onClick={handleClick}
    >
      <div className="space-y-2">
        {/* Title and Description */}
        <div>
          <h3 className="font-medium text-foreground group-hover:text-primary transition-colors">
            {title}
          </h3>
          {description && (
            <p className="text-sm text-muted-foreground mt-1">
              {truncateDescription(description)}
            </p>
          )}
        </div>

        {/* Metrics, Status, and Time */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <ProjectMetrics 
              wordCount={wordCount} 
              documentCount={documentCount}
            />
            {primaryTag && (
              <StatusBadge tag={primaryTag} />
            )}
          </div>
          
          {updatedAt && (
            <RelativeTime date={updatedAt} />
          )}
        </div>
      </div>
    </div>
  )
}