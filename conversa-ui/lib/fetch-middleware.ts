/**
 * Enhances the global fetch API to handle backend requests with proper CORS and referrer policy
 */

// Store the original fetch function
const originalFetch = globalThis.fetch;

// The backend URL (will be used to identify backend requests)
const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

// Enhance the fetch function
function enhancedFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  // Check if this is a request to our backend
  const url = typeof input === 'string' ? input : input.toString();
  
  if (url.startsWith(backendUrl)) {
    // This is a backend request, enhance it with proper headers
    const enhancedInit: RequestInit = {
      ...init,
      headers: {
        ...init?.headers,
        'Content-Type': 'application/json',
      },
      // Set CORS mode
      mode: 'cors',
      // Include credentials (cookies, etc)
      credentials: 'include',
    };
    
    // Use the original fetch with enhanced options
    return originalFetch(input, enhancedInit);
  }
  
  // For other requests, use the original fetch without modifications
  return originalFetch(input, init);
}

// Override the global fetch
export function setupFetchMiddleware() {
  // Only run in the browser
  if (typeof window !== 'undefined') {
    // @ts-ignore - Override the global fetch
    globalThis.fetch = enhancedFetch;
    console.log('Fetch middleware installed');
  }
}

// Function to restore the original fetch (for cleanup)
export function cleanupFetchMiddleware() {
  if (typeof window !== 'undefined') {
    // @ts-ignore - Restore the original fetch
    globalThis.fetch = originalFetch;
    console.log('Fetch middleware removed');
  }
} 