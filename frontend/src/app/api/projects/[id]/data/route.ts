import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: projectId } = await params;
    
    // Get auth token from cookies
    const cookieStore = await cookies();
    const authToken = cookieStore.get('sb-access-token')?.value;
    
    if (!authToken) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }
    
    // Call backend API for project details
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Project not found' },
          { status: 404 }
        );
      }
      
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.error || 'Failed to fetch project data' },
        { status: response.status }
      );
    }
    
    const projectData = await response.json();
    return NextResponse.json(projectData);
  } catch (error) {
    console.error('Error fetching project data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch project data' },
      { status: 500 }
    );
  }
}