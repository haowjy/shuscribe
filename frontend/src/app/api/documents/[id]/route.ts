import { NextRequest, NextResponse } from 'next/server';
import { getMockDocument } from '@/lib/api/mock-project-data';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: documentId } = await params;
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 50));
    
    const document = getMockDocument(documentId, '1'); // Using project ID 1
    
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
    
    const document = getMockDocument(documentId, '1');
    
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
    
    // TODO: Implement proper document storage/persistence
    // For now, just return the updated document without persisting
    
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
    
    const document = getMockDocument(documentId, '1');
    
    if (!document) {
      return NextResponse.json(
        { error: 'Document not found' },
        { status: 404 }
      );
    }
    
    // TODO: Implement proper document deletion
    // For now, just return success without actually deleting
    
    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json(
      { error: 'Failed to delete document' },
      { status: 500 }
    );
  }
}

// Helper function to count words in ProseMirror content
function countWords(content: any): number {
  if (!content || !content.content) return 0;
  
  let wordCount = 0;
  
  function countNode(node: any) {
    if (node.type === 'text' && node.text) {
      wordCount += String(node.text).split(/\s+/).filter(Boolean).length;
    }
    
    if (node.content && Array.isArray(node.content)) {
      node.content.forEach(countNode);
    }
  }
  
  if (Array.isArray(content.content)) {
    content.content.forEach(countNode);
  }
  return wordCount;
}