import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Get the response
  const response = NextResponse.next();
  
  // Set the referrer policy header to allow cross-origin requests
  response.headers.set('Referrer-Policy', 'no-referrer-when-downgrade');
  
  return response;
}

export const config = {
  matcher: '/((?!api|_next/static|_next/image|favicon.ico).*)',
}; 