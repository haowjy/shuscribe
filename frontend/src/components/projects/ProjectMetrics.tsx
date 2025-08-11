'use client'

interface ProjectMetricsProps {
  wordCount: number
  documentCount: number
  className?: string
}

export function ProjectMetrics({ wordCount, documentCount, className = '' }: ProjectMetricsProps) {
  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M'
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K'
    }
    return num.toString()
  }

  return (
    <div className={`flex items-center gap-3 text-xs text-muted-foreground ${className}`}>
      <span>{formatNumber(wordCount)} words</span>
      <span>•</span>
      <span>{formatNumber(documentCount)} docs</span>
    </div>
  )
}