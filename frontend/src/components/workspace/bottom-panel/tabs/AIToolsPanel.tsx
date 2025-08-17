'use client'

import { QuickActions } from '../components/QuickActions'
import { DocumentSummary } from '../components/DocumentSummary'

export function AIToolsPanel() {
  const handleQuickAction = (actionId: string) => {
    // TODO: Implement quick action handlers
    console.log('AI Tools quick action:', actionId)
  }

  const handleSummaryChange = (summary: string) => {
    // TODO: Implement summary persistence
    console.log('Summary changed:', summary)
  }

  return (
    <div className="p-4 space-y-4">
      <QuickActions onAction={handleQuickAction} />
      <DocumentSummary onSummaryChange={handleSummaryChange} />
    </div>
  )
}