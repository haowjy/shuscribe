'use client'

import { ReactNode } from 'react'

interface ProjectListProps {
  children: ReactNode
  className?: string
}

export function ProjectList({ children, className = '' }: ProjectListProps) {
  return (
    <div className={`space-y-1 ${className}`}>
      {children}
    </div>
  )
}