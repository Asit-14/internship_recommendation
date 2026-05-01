import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
    
    // We want the root /health endpoint, so we strip out /api/v1 if it exists
    const baseUrl = apiBaseUrl.replace('/api/v1', '');
    const healthUrl = `${baseUrl}/health`;

    const response = await fetch(healthUrl, {
      // Don't cache this request, we want a real network call every time
      cache: 'no-store',
      headers: {
        'Cache-Control': 'no-cache',
      },
    });

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json({ success: true, message: 'Keep-alive ping successful', data });
    } else {
      return NextResponse.json(
        { success: false, message: `Keep-alive ping failed with status: ${response.status}` },
        { status: response.status }
      );
    }
  } catch (error: any) {
    return NextResponse.json(
      { success: false, message: 'Keep-alive ping failed', error: error.message },
      { status: 500 }
    );
  }
}
