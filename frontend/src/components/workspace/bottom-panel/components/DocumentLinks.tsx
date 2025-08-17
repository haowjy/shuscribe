'use client'

import { Link, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { DocumentLink } from '../types'

interface DocumentLinksProps {
  links?: DocumentLink[]
  incomingLinksCount?: number
  onAddLink?: () => void
  onRemoveLink?: (linkId: string) => void
}

const mockLinks: DocumentLink[] = [
  { id: '1', target: '/characters/elara', text: 'Elara Moonwhisper', type: 'character' },
  { id: '2', target: '/locations/thornfield-manor', text: 'Thornfield Manor', type: 'location' },
  { id: '3', target: '/items/ancient-journal', text: 'Margaret\'s Journal', type: 'item' }
]

const getLinkTypeColor = (type: DocumentLink['type']) => {
  switch (type) {
    case 'character': return 'bg-primary'
    case 'location': return 'bg-success'
    case 'item': return 'bg-warning'
    default: return 'bg-muted-foreground'
  }
}

export function DocumentLinks({ 
  links = mockLinks,
  incomingLinksCount = 2,
  onAddLink,
  onRemoveLink 
}: DocumentLinksProps) {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Document References</h3>
        <Button size="sm" variant="outline" onClick={onAddLink}>
          <Link className="h-3 w-3 mr-1" />
          Add Reference
        </Button>
      </div>
      
      {/* Outgoing Links */}
      <div className="space-y-2">
        <div className="text-xs text-muted-foreground">
          Outgoing Links ({links.length})
        </div>
        <div className="space-y-1">
          {links.map((link) => (
            <div 
              key={link.id} 
              className="flex items-center justify-between p-2 border border-border rounded text-sm"
            >
              <div className="flex items-center gap-2 min-w-0">
                <div className={cn(
                  "w-2 h-2 rounded-full flex-shrink-0",
                  getLinkTypeColor(link.type)
                )} />
                <span className="truncate">{link.text}</span>
              </div>
              <Button 
                size="sm" 
                variant="ghost" 
                className="h-6 w-6 p-0"
                onClick={() => onRemoveLink?.(link.id)}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      </div>

      {/* Incoming Links */}
      <div className="space-y-2">
        <div className="text-xs text-muted-foreground">
          Incoming Links ({incomingLinksCount})
        </div>
        <div className="space-y-1">
          <div className="p-2 border border-border rounded text-sm text-muted-foreground">
            Referenced by: ch-02.md, character-notes.md
          </div>
        </div>
      </div>
    </div>
  )
}