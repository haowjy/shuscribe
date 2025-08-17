'use client'

import { useState } from 'react'
import { Edit, Save, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface DocumentSummaryProps {
  initialSummary?: string
  onSummaryChange?: (summary: string) => void
}

export function DocumentSummary({ 
  initialSummary = '', 
  onSummaryChange 
}: DocumentSummaryProps) {
  const [summary, setSummary] = useState(initialSummary)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [tempSummary, setTempSummary] = useState('')

  const handleGenerateSummary = () => {
    setIsGenerating(true)
    // Mock summary generation
    setTimeout(() => {
      const generatedSummary = "This chapter introduces the protagonist in a mysterious manor during a storm. Key elements include the discovery of an ancient journal and the beginning of a supernatural mystery. The atmospheric setting establishes the gothic tone while the journal serves as a plot device for upcoming revelations."
      setSummary(generatedSummary)
      onSummaryChange?.(generatedSummary)
      setIsGenerating(false)
    }, 2000)
  }

  const handleEditSummary = () => {
    setTempSummary(summary)
    setIsEditing(true)
  }

  const handleSaveSummary = () => {
    setSummary(tempSummary)
    onSummaryChange?.(tempSummary)
    setIsEditing(false)
  }

  const handleCancelEdit = () => {
    setTempSummary('')
    setIsEditing(false)
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Document Summary</h3>
        <div className="flex items-center gap-2">
          {isEditing ? (
            <>
              <Button 
                size="sm" 
                variant="outline"
                onClick={handleSaveSummary}
                disabled={!tempSummary.trim()}
              >
                <Save className="h-3 w-3 mr-1" />
                Save
              </Button>
              <Button 
                size="sm" 
                variant="ghost"
                onClick={handleCancelEdit}
              >
                <XCircle className="h-3 w-3 mr-1" />
                Cancel
              </Button>
            </>
          ) : (
            <>
              <Button 
                size="sm" 
                variant="outline"
                onClick={handleGenerateSummary}
                disabled={isGenerating}
              >
                {isGenerating ? 'Generating...' : 'Generate Summary'}
              </Button>
              {summary && (
                <Button 
                  size="sm" 
                  variant="ghost"
                  onClick={handleEditSummary}
                >
                  <Edit className="h-3 w-3 mr-1" />
                  Edit
                </Button>
              )}
            </>
          )}
        </div>
      </div>
      <textarea
        value={isEditing ? tempSummary : summary}
        onChange={isEditing ? (e) => setTempSummary(e.target.value) : undefined}
        placeholder={isEditing ? "Edit the summary..." : "AI-generated summary will appear here..."}
        className="w-full min-h-20 p-2 text-sm border border-border rounded-md resize-none bg-background"
        readOnly={!isEditing && !isGenerating}
      />
    </div>
  )
}