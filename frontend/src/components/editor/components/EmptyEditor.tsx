'use client'

interface EmptyEditorProps {
  message?: string
  subMessage?: string
}

export function EmptyEditor({ 
  message = "No document open",
  subMessage = "Select a document from the sidebar or create a new one"
}: EmptyEditorProps) {
  return (
    <div className="h-full flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <div className="text-muted-foreground">
          {message}
        </div>
        <p className="text-sm text-muted-foreground">
          {subMessage}
        </p>
      </div>
    </div>
  )
}