'use client'

import { useParams } from 'next/navigation'
import { ActivityContainer } from '@/components/workspace/layout/ActivityContainer'

export default function ProjectSettingsPage() {
  const params = useParams()
  const projectId = params.id as string

  return <ActivityContainer projectId={projectId} />
}