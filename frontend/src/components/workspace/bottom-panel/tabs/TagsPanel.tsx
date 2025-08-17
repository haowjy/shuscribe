'use client'

import { TagManager } from '../components/TagManager'

export function TagsPanel() {
  const handleTagsChange = (tags: string[]) => {
    // TODO: Implement tag persistence
    console.log('Tags changed:', tags)
  }

  return (
    <div className="p-4">
      <TagManager onTagsChange={handleTagsChange} />
    </div>
  )
}