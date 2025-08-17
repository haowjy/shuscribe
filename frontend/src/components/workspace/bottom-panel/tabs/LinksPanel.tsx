'use client'

import { DocumentLinks } from '../components/DocumentLinks'

export function LinksPanel() {
  const handleAddLink = () => {
    // TODO: Implement add link functionality
    console.log('Add link clicked')
  }

  const handleRemoveLink = (linkId: string) => {
    // TODO: Implement remove link functionality
    console.log('Remove link:', linkId)
  }

  return (
    <div className="p-4">
      <DocumentLinks 
        onAddLink={handleAddLink}
        onRemoveLink={handleRemoveLink}
      />
    </div>
  )
}