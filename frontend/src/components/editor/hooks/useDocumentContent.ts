/**
 * Document Content Hook - Load document content for editor tabs
 * 
 * WHY: The editor needs to load actual document content when tabs are opened.
 * This hook provides real document data from Dexie instead of mock content,
 * integrating the file selection with the document editing system.
 * 
 * Problem Context: Previously, the editor used mock content for all tabs.
 * Now that file selection opens real tabs, we need to load the actual
 * document content associated with each file.
 * 
 * Integration Points:
 * - Uses document data hooks for real-time content loading
 * - Connects file selection (fileId) to document loading
 * - Provides fallback content for new/empty documents
 */

import { useDocument } from '@/hooks/data'
import { useUser } from '@/hooks/useUser'
import { useMemo } from 'react'
import { marked } from 'marked'

// Configure marked to parse synchronously for simpler handling
marked.setOptions({
  async: false
})

interface UseDocumentContentOptions {
  fileId: string | null
  documentId?: string | null
  projectId: string
}

/**
 * Load document content for the active editor tab
 * Returns document content as HTML string (for mock files) or ProseMirror JSON (for real documents)
 */
export function useDocumentContent({ fileId, documentId, projectId }: UseDocumentContentOptions) {
  const { userId, isAuthenticated } = useUser()
  
  console.log('🔍 useDocumentContent: Called with', { 
    fileId, 
    documentId, 
    projectId, 
    isAuthenticated,
    userId: !!userId 
  })
  
  // Better detection: Real files have documentId, mock files don't
  const isRealDocument = !!documentId
  const isMockFile = !isRealDocument && fileId
  
  // For real documents, use documentId. For mock files, use fileId for content lookup
  const documentToLoad = documentId || fileId
  
  console.log('🔍 useDocumentContent: Detection logic', {
    isRealDocument,
    isMockFile,
    hasDocumentId: !!documentId,
    documentToLoad,
    willLoadDocument: isAuthenticated && isRealDocument && documentToLoad
  })
  
  // Only attempt document loading if user is authenticated and it's a real document
  const shouldLoadDocument = isAuthenticated && isRealDocument && documentToLoad
  
  // Get document data if this is a real document and user is authenticated
  const { 
    data: document, 
    isLoading,
    error 
  } = useDocument(shouldLoadDocument ? documentToLoad : '')


  // Convert document content to markdown string for editor
  const content = useMemo(() => {
    console.log('🔍 useDocumentContent: Content processing', {
      isMockFile,
      hasDocument: !!document,
      documentContentType: document?.content ? typeof document.content : 'undefined',
      documentContentPreview: document?.content ? 
        (typeof document.content === 'string' ? (document.content as string).substring(0, 100) + '...' : 'JSON object') : 
        'no content'
    })
    
    // Priority 1: Mock content for demo files (works without authentication)
    if (isMockFile) {
      console.log('📄 useDocumentContent: Using mock content for', fileId)
      // Check if fileId matches known mock content, otherwise provide fallback
      const knownMockFiles = ['elara', 'thomas', 'shadow-lord', 'characters', 'chapter-01', 'outline', 'thornfield-manor']
      const hasMockContent = knownMockFiles.includes(fileId)
      
      if (hasMockContent) {
        const mockMarkdown = getMockContentForFile(fileId)
        const mockHtml = marked(mockMarkdown) as string
        return mockHtml
      } else {
        // Generic mock content for unknown files
        const genericMockMarkdown = `# ${fileId?.replace('-', ' ') || 'Mock File'}\n\nThis is a mock file for demonstration purposes.`
        const genericMockHtml = marked(genericMockMarkdown) as string
        return genericMockHtml
      }
    }
    
    // Priority 2: Real document content (requires authentication)
    if (document?.content) {
      console.log('📄 useDocumentContent: Processing real document content')
      // Return content directly - TipTap can handle both HTML strings and ProseMirror JSON
      if (typeof document.content === 'string') {
        console.log('📄 useDocumentContent: Returning string content')
        const stringContent = document.content as string
        // Check if it's markdown and needs conversion to HTML
        if (stringContent.startsWith('#') || stringContent.includes('##')) {
          console.log('📄 useDocumentContent: Converting markdown string to HTML')
          const htmlContent = marked(stringContent) as string
          return htmlContent
        }
        // Content is already HTML string
        return stringContent
      }

      console.log('📄 useDocumentContent: Returning ProseMirror JSON')
      // Content is ProseMirror JSON - return directly, TipTap handles this natively
      return document.content
    }
    
    // Priority 3: Unauthenticated state - show helpful message
    if (!isAuthenticated) {
      const welcomeMarkdown = `# Welcome to ShuScribe!

This is a demonstration of the document editor. To access your real documents, please sign in.

## Demo Features Available:
- File tree navigation
- Tab management  
- Document editing interface
- @-reference system preview

## Try the Demo Files:
Click on files like "elara.md", "thomas.md", or "chapter-01.md" in the Explorer to see rich demo content.

Sign in to start creating your own universe of stories and characters!`
      return marked(welcomeMarkdown) as string
    }
    
    // Priority 4: Authenticated but no document found - return empty content
    // Let the editor handle empty state with placeholder text instead of template content
    return null
  }, [document, fileId, isMockFile, isAuthenticated])

  console.log('🔍 useDocumentContent: Final result', {
    contentType: typeof content,
    contentLength: typeof content === 'string' ? content.length : 'N/A',
    contentPreview: typeof content === 'string' ? content.substring(0, 100) + '...' : 'JSON object',
    isLoading: shouldLoadDocument ? isLoading : false,
    title: document?.title || (isMockFile ? fileId?.replace('-', ' ') : 'Untitled')
  })

  return {
    content,
    document,
    isLoading: shouldLoadDocument ? isLoading : false, // Don't show loading for mock files
    error,
    // Additional metadata
    title: document?.title || (isMockFile ? fileId?.replace('-', ' ') : 'Untitled'),
    wordCount: document?.wordCount || 0,
    hasUnsavedChanges: false // TODO: Implement unsaved changes detection
  }
}

/**
 * Get mock content for demonstration files
 * This allows the file opening to work with mock file tree data
 */
function getMockContentForFile(fileId: string): string {
  switch (fileId) {
    case 'elara':
      return `# Elara Mitchell

## Character Profile

**Age**: 28  
**Occupation**: Historian  
**Key Traits**: Curious, determined, intuitive  

## Background

Recently inherited the Thornfield Manor from a distant relative she never knew existed. Her analytical mind and love for history make her the perfect person to uncover the manor's secrets.

## Character Arc

Elara begins as a skeptical academic but gradually learns to trust her intuition as supernatural events unfold around the manor.`

    case 'thomas':
      return `# Thomas Grey

## Character Profile

**Age**: 35  
**Role**: Local historian and Sarah's research partner  
**Personality**: Methodical, skeptical, protective  

## Background

A lifelong resident of the town, Thomas knows more about the local history than anyone. He serves as both a research partner and a grounding force for the protagonist.

## Relationship Dynamics

Thomas provides a rational counterpoint to the supernatural elements of the story, often skeptical until evidence becomes undeniable.`

    case 'shadow-lord':
      return `# The Shadow Lord

## Antagonist Profile

**Nature**: Ancient supernatural entity  
**Powers**: Shadow manipulation, dark magic  
**Motivation**: Reclaim what was taken from him centuries ago  

## Backstory

Once a powerful sorcerer who made a deal with dark forces, now exists as a being of pure shadow and malice. His connection to Thornfield Manor runs deep.

## Threat Level

The primary antagonist whose influence grows stronger as the story progresses, culminating in a final confrontation.`

    case 'chapter-01':
      return `# Chapter 1: The Inheritance

The rain fell steadily against the windows of the old manor, each drop tracing intricate patterns down the glass. Elara pressed her face closer to the pane, watching the storm rage outside while the warmth of the fireplace danced across her back.

## The Discovery

In the attic, beneath layers of dust and forgotten memories, she found the journal. Its leather binding was worn smooth by countless hands, and the pages yellowed with age.

> "Every story has a beginning, but not every beginning leads to the same end." - *From the journal of Margaret Thornfield*

The first entry was dated fifty years ago, written in a delicate script that spoke of secrets and shadows.`

    case 'outline':
      return `# Story Outline

## Act I: Arrival
- Elara inherits Thornfield Manor
- Discovery of the journal
- First supernatural encounters
- Meeting Thomas Grey

## Act II: Investigation
- Research into the manor's history
- Uncovering the Shadow Lord's past
- Growing supernatural threats
- Character development and relationships

## Act III: Confrontation
- Final battle with the Shadow Lord
- Resolution of the mystery
- Character transformation
- New beginnings`

    case 'thornfield-manor':
      return `# Thornfield Manor

## Location Details

**Built**: 1847  
**Style**: Gothic Revival  
**Current State**: Partially restored  

## History

The manor has been abandoned for over two decades, with only local caretakers maintaining basic upkeep. Previous owners have reported strange occurrences, leading to its reputation as haunted.

## Key Features

- Grand staircase with intricate woodwork
- Library with hidden passages
- Attic containing family records
- Basement with mysterious sealed rooms

## Supernatural Activity

The manor serves as a focal point for supernatural energy, with activity increasing during storms and at specific times of the year.`

    default:
      return `# ${fileId.replace('-', ' ').toUpperCase()}

This is a mock document for development and demonstration purposes.

You can edit this content and see how the editor handles different types of content. This helps demonstrate the file opening functionality while real project data is being set up.

## Features Demonstrated

- File tree navigation
- Tab management
- Document loading
- Content editing

The @-reference system and other advanced features will work once connected to real project data.`
  }
}

/*
 * TODO: ENHANCED DOCUMENT CONTENT INTEGRATION
 * 
 * When ProseMirror editor is fully integrated:
 * 
 * 1. PROSEMIRROR INTEGRATION:
 *    - Convert ProseMirror JSON to/from markdown for editing
 *    - Handle rich text formatting and @-references
 *    - Preserve document structure and metadata
 * 
 * 2. REAL-TIME SYNC:
 *    - Auto-save document changes to Dexie
 *    - Track unsaved changes state
 *    - Handle concurrent editing conflicts
 * 
 * 3. PERFORMANCE OPTIMIZATIONS:
 *    - Cache document content for open tabs
 *    - Lazy load content for inactive tabs
 *    - Debounce content updates
 * 
 * 4. ERROR HANDLING:
 *    - Handle missing documents gracefully
 *    - Provide content recovery options
 *    - Show meaningful error states
 */