import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const limit = searchParams.get('limit') || '10';
    const offset = searchParams.get('offset') || '0';
    const sort = searchParams.get('sort') || 'updated_at';
    const order = searchParams.get('order') || 'desc';

    // Proxy to backend API
    const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
    const backendEndpoint = `${backendUrl}/projects?limit=${limit}&offset=${offset}&sort=${sort}&order=${order}`;

    // Get auth token from request headers
    const authHeader = request.headers.get('authorization');
    
    const backendResponse = await fetch(backendEndpoint, {
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader && { 'Authorization': authHeader }),
      },
    });

    const backendData = await backendResponse.json();

    if (!backendResponse.ok) {
      return NextResponse.json(
        { error: backendData.error || backendData.message || 'Backend API error' },
        { status: backendResponse.status }
      );
    }

    return NextResponse.json(backendData);
  } catch (error) {
    console.error('Error proxying to backend API:', error);
    return NextResponse.json(
      { error: 'Failed to connect to backend API. Please ensure the backend server is running.' },
      { status: 503 }
    );
  }
}