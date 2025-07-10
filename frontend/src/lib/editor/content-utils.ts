import { EditorDocument, TiptapContent } from './editor-types';

/**
 * Create an empty Tiptap document
 */
export function createEmptyDocument(): EditorDocument {
  return {
    type: 'doc',
    content: [
      {
        type: 'paragraph',
        content: []
      }
    ]
  };
}

/**
 * Validate if content is a valid Tiptap document
 */
export function isValidTiptapDocument(content: any): content is EditorDocument {
  if (!content || typeof content !== 'object') {
    return false;
  }

  if (content.type !== 'doc' || !Array.isArray(content.content)) {
    return false;
  }

  return true;
}

/**
 * Sanitize and validate content from external sources
 */
export function sanitizeContent(content: any): EditorDocument {
  if (!content) {
    return createEmptyDocument();
  }

  // If it's already a valid document, return it
  if (isValidTiptapDocument(content)) {
    return content;
  }

  // Try to parse as JSON if it's a string
  if (typeof content === 'string') {
    try {
      const parsed = JSON.parse(content);
      if (isValidTiptapDocument(parsed)) {
        return parsed;
      }
    } catch {
      // If parsing fails, create a document with the string as text
      return {
        type: 'doc',
        content: [
          {
            type: 'paragraph',
            content: [
              {
                type: 'text',
                text: content
              }
            ]
          }
        ]
      };
    }
  }

  // Fallback to empty document
  return createEmptyDocument();
}

/**
 * Convert content to JSON string for storage
 */
export function serializeContent(content: EditorDocument): string {
  try {
    return JSON.stringify(content);
  } catch (error) {
    console.error('Failed to serialize content:', error);
    return JSON.stringify(createEmptyDocument());
  }
}

/**
 * Parse content from JSON string
 */
export function deserializeContent(contentString: string): EditorDocument {
  try {
    const parsed = JSON.parse(contentString);
    return sanitizeContent(parsed);
  } catch (error) {
    console.error('Failed to deserialize content:', error);
    return createEmptyDocument();
  }
}

/**
 * Check if document is empty (only empty paragraph)
 */
export function isEmptyDocument(content: EditorDocument): boolean {
  if (!content.content || content.content.length === 0) {
    return true;
  }

  // Check if it's just a single empty paragraph
  if (content.content.length === 1) {
    const firstNode = content.content[0];
    if (firstNode.type === 'paragraph') {
      return !firstNode.content || firstNode.content.length === 0;
    }
  }

  return false;
}

/**
 * Get text content from document (no formatting)
 */
export function getTextContent(content: EditorDocument): string {
  function extractText(node: TiptapContent): string {
    if (node.text) {
      return node.text;
    }

    if (node.content) {
      return node.content.map(extractText).join('');
    }

    return '';
  }

  return content.content?.map(extractText).join('\n') || '';
}

/**
 * Get word count from document
 */
export function getWordCount(content: EditorDocument): number {
  const text = getTextContent(content);
  if (!text.trim()) {
    return 0;
  }
  
  return text.trim().split(/\s+/).length;
}

/**
 * Get character count from document
 */
export function getCharacterCount(content: EditorDocument): number {
  return getTextContent(content).length;
}

/**
 * Create a document from plain text
 */
export function createDocumentFromText(text: string): EditorDocument {
  if (!text) {
    return createEmptyDocument();
  }

  const paragraphs = text.split('\n').map(line => ({
    type: 'paragraph',
    content: line ? [{ type: 'text', text: line }] : []
  }));

  return {
    type: 'doc',
    content: paragraphs
  };
}

/**
 * Merge two documents (append second to first)
 */
export function mergeDocuments(doc1: EditorDocument, doc2: EditorDocument): EditorDocument {
  return {
    type: 'doc',
    content: [...(doc1.content || []), ...(doc2.content || [])]
  };
}

/**
 * Get document summary for display
 */
export function getDocumentSummary(content: EditorDocument, maxLength: number = 100): string {
  const text = getTextContent(content);
  if (text.length <= maxLength) {
    return text;
  }
  
  return text.substring(0, maxLength).trim() + '...';
}