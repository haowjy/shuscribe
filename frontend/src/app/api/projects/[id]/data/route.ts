import { NextRequest, NextResponse } from 'next/server';
import { mockProjectData } from '@/lib/api/mock-data-tiptap';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: projectId } = await params;
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Return mock project data
    const projectData = mockProjectData[projectId];
    
    if (!projectData) {
      return NextResponse.json(
        { error: 'Project not found' },
        { status: 404 }
      );
    }
    
    return NextResponse.json(projectData);
  } catch {
    return NextResponse.json(
      { error: 'Failed to fetch project data' },
      { status: 500 }
    );
  }
}