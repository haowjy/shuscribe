import { NextRequest, NextResponse } from 'next/server';
import { v4 as uuidv4 } from 'uuid';

// ProseMirror content type definitions
interface ProseMirrorTextNode {
  type: 'text';
  text: string;
}

interface ProseMirrorNode {
  type: string;
  content?: ProseMirrorNode[];
  text?: string;
}

interface ProseMirrorContent {
  type: 'doc';
  content: ProseMirrorNode[];
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Generate new document
    const documentId = uuidv4();
    const now = new Date().toISOString();
    
    const newDocument = {
      id: documentId,
      projectId: body.projectId,
      title: body.title || 'Untitled',
      path: body.path || `/${body.title || 'untitled'}.md`,
      content: body.content || {
        type: 'doc',
        content: [
          {
            type: 'paragraph',
            content: []
          }
        ]
      },
      tags: body.tags || [],
      wordCount: body.content ? countWords(body.content) : 0,
      createdAt: now,
      updatedAt: now,
      isTemp: body.isTemp || false
    };
    
    return NextResponse.json(newDocument);
  } catch {
    return NextResponse.json(
      { error: 'Failed to create document' },
      { status: 500 }
    );
  }
}

// Helper function to count words in ProseMirror content
function countWords(content: ProseMirrorContent | unknown): number {
  // Type guard to ensure we have valid ProseMirror content
  if (!content || typeof content !== 'object' || !('content' in content)) {
    return 0;
  }
  
  const proseMirrorContent = content as ProseMirrorContent;
  if (!Array.isArray(proseMirrorContent.content)) {
    return 0;
  }
  
  let wordCount = 0;
  
  function countNode(node: ProseMirrorNode): void {
    if (node.type === 'text' && typeof node.text === 'string') {
      wordCount += node.text.split(/\s+/).filter(Boolean).length;
    }
    
    if (node.content && Array.isArray(node.content)) {
      node.content.forEach(countNode);
    }
  }
  
  proseMirrorContent.content.forEach(countNode);
  return wordCount;
}