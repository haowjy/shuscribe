'use client'

import { useState } from 'react'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

interface TagManagerProps {
  initialTags?: string[]
  suggestedTags?: string[]
  onTagsChange?: (tags: string[]) => void
}

export function TagManager({ 
  initialTags = ['mystery', 'gothic', 'supernatural'],
  suggestedTags = ['atmospheric', 'journal', 'storm', 'manor'],
  onTagsChange 
}: TagManagerProps) {
  const [tags, setTags] = useState(initialTags)
  const [newTag, setNewTag] = useState('')

  const handleAddTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      const updatedTags = [...tags, newTag.trim()]
      setTags(updatedTags)
      onTagsChange?.(updatedTags)
      setNewTag('')
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    const updatedTags = tags.filter(tag => tag !== tagToRemove)
    setTags(updatedTags)
    onTagsChange?.(updatedTags)
  }

  const handleAddSuggestedTag = (tag: string) => {
    if (!tags.includes(tag)) {
      const updatedTags = [...tags, tag]
      setTags(updatedTags)
      onTagsChange?.(updatedTags)
    }
  }

  return (
    <div className="space-y-4">
      {/* Add Tag Input */}
      <div className="space-y-2">
        <h3 className="text-sm font-medium">Document Tags</h3>
        <div className="flex gap-1">
          <Input
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            placeholder="Add tag..."
            className="h-8"
            onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
          />
          <Button 
            size="sm" 
            onClick={handleAddTag} 
            disabled={!newTag.trim()}
          >
            Add
          </Button>
        </div>
      </div>

      {/* Current Tags */}
      <div className="space-y-2">
        <div className="text-xs text-muted-foreground">
          Current Tags ({tags.length})
        </div>
        <div className="flex gap-2 flex-wrap">
          {tags.map((tag) => (
            <div 
              key={tag} 
              className="flex items-center gap-1 px-2 py-1 bg-muted rounded text-xs"
            >
              <span>{tag}</span>
              <Button 
                size="sm" 
                variant="ghost" 
                className="h-4 w-4 p-0 hover:bg-destructive hover:text-destructive-foreground"
                onClick={() => handleRemoveTag(tag)}
              >
                <X className="h-2 w-2" />
              </Button>
            </div>
          ))}
        </div>
      </div>

      {/* Suggested Tags */}
      <div className="space-y-2">
        <div className="text-xs text-muted-foreground">Suggested Tags</div>
        <div className="flex gap-2 flex-wrap">
          {suggestedTags.map((tag) => (
            <Button 
              key={tag}
              size="sm" 
              variant="outline" 
              className="h-6 text-xs"
              onClick={() => handleAddSuggestedTag(tag)}
              disabled={tags.includes(tag)}
            >
              + {tag}
            </Button>
          ))}
        </div>
      </div>
    </div>
  )
}