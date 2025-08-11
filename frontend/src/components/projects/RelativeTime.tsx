'use client'

interface RelativeTimeProps {
  date: string | Date
  className?: string
}

export function RelativeTime({ date, className = '' }: RelativeTimeProps) {
  const getRelativeTime = (date: string | Date): string => {
    const now = new Date()
    const targetDate = typeof date === 'string' ? new Date(date) : date
    const diffInMs = now.getTime() - targetDate.getTime()
    const diffInMinutes = Math.floor(diffInMs / 60000)
    const diffInHours = Math.floor(diffInMinutes / 60)
    const diffInDays = Math.floor(diffInHours / 24)

    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`
    if (diffInHours < 24) return `${diffInHours}h ago`
    if (diffInDays === 1) return 'Yesterday'
    if (diffInDays < 7) return `${diffInDays}d ago`
    if (diffInDays < 30) {
      const weeks = Math.floor(diffInDays / 7)
      return `${weeks}w ago`
    }
    if (diffInDays < 365) {
      const months = Math.floor(diffInDays / 30)
      return `${months}mo ago`
    }
    
    const years = Math.floor(diffInDays / 365)
    return `${years}y ago`
  }

  return (
    <span className={`text-xs text-muted-foreground ${className}`}>
      Updated {getRelativeTime(date)}
    </span>
  )
}