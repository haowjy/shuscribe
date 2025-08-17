'use client'

import { Button } from '@/components/ui/button'

const quickActions = [
  { id: 'analyze-tone', label: 'Analyze Tone' },
  { id: 'check-grammar', label: 'Check Grammar' },
  { id: 'suggest-improvements', label: 'Suggest Improvements' },
  { id: 'extract-characters', label: 'Extract Characters' },
]

interface QuickActionsProps {
  onAction?: (actionId: string) => void
}

export function QuickActions({ onAction }: QuickActionsProps) {
  const handleAction = (actionId: string) => {
    console.log('Quick action:', actionId)
    onAction?.(actionId)
  }

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium">Quick Actions</h3>
      <div className="flex gap-2 flex-wrap">
        {quickActions.map((action) => (
          <Button
            key={action.id}
            size="sm"
            variant="outline"
            onClick={() => handleAction(action.id)}
          >
            {action.label}
          </Button>
        ))}
      </div>
    </div>
  )
}