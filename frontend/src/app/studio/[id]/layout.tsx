'use client'

import { ProjectStateProvider } from '@/components/providers/ProjectStateProvider'

interface ProjectLayoutProps {
  children: React.ReactNode
}

export default function ProjectLayout({ children }: ProjectLayoutProps) {
  return (
    <ProjectStateProvider>
      {children}
    </ProjectStateProvider>
  )
}