'use client'

import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { 
  Tooltip, 
  TooltipContent, 
  TooltipTrigger 
} from '@/components/ui/tooltip'

interface NewTabButtonProps {
  onNewTab: () => void
}

export function NewTabButton({ onNewTab }: NewTabButtonProps) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          onClick={onNewTab}
          className="h-8 w-8 rounded-t-md transition-colors flex items-center justify-center border border-transparent border-b-0 hover:bg-muted/30"
        >
          <Plus className="h-3 w-3" />
        </Button>
      </TooltipTrigger>
      <TooltipContent side="bottom">
        <p>New Document</p>
      </TooltipContent>
    </Tooltip>
  )
}