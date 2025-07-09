import { NextRequest, NextResponse } from 'next/server';
import { mockDocuments } from '@/lib/api/mock-data';
import { v4 as uuidv4 } from 'uuid';

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
    
    mockDocuments[documentId] = newDocument;
    
    return NextResponse.json(newDocument);
  } catch {
    return NextResponse.json(
      { error: 'Failed to create document' },
      { status: 500 }
    );
  }
}

// Helper function to count words in ProseMirror content
function countWords(content: unknown): number {
  if (!content || !content.content) return 0;
  
  let wordCount = 0;
  
  function countNode(node: Record<string, unknown>) {
    if (node.type === 'text' && node.text) {
      wordCount += node.text.split(/\s+/).filter(Boolean).length;
    }
    
    if (node.content) {
      node.content.forEach(countNode);
    }
  }
  
  content.content.forEach(countNode);
  return wordCount;
}