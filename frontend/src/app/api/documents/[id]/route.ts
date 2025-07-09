import { NextRequest, NextResponse } from 'next/server';
import { mockDocuments } from '@/lib/api/mock-data';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: documentId } = await params;
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 50));
    
    const document = mockDocuments[documentId];
    
    if (!document) {
      return NextResponse.json(
        { error: 'Document not found' },
        { status: 404 }
      );
    }
    
    return NextResponse.json(document);
  } catch {
    return NextResponse.json(
      { error: 'Failed to fetch document' },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: documentId } = await params;
    const body = await request.json();
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const document = mockDocuments[documentId];
    
    if (!document) {
      return NextResponse.json(
        { error: 'Document not found' },
        { status: 404 }
      );
    }
    
    // Update document
    const updatedDocument = {
      ...document,
      ...body,
      updatedAt: new Date().toISOString(),
      wordCount: body.content ? countWords(body.content) : document.wordCount
    };
    
    mockDocuments[documentId] = updatedDocument;
    
    return NextResponse.json(updatedDocument);
  } catch {
    return NextResponse.json(
      { error: 'Failed to update document' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: documentId } = await params;
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 150));
    
    const document = mockDocuments[documentId];
    
    if (!document) {
      return NextResponse.json(
        { error: 'Document not found' },
        { status: 404 }
      );
    }
    
    delete mockDocuments[documentId];
    
    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json(
      { error: 'Failed to delete document' },
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