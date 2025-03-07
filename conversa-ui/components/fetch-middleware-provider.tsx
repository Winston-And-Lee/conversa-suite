'use client';

import { ReactNode, useEffect } from 'react';
import { setupFetchMiddleware, cleanupFetchMiddleware } from '@/lib/fetch-middleware';

export function FetchMiddlewareProvider({ children }: { children: ReactNode }) {
  useEffect(() => {
    // Set up fetch middleware on component mount
    setupFetchMiddleware();
    
    // Clean up on unmount
    return () => {
      cleanupFetchMiddleware();
    };
  }, []);

  // Just render children
  return <>{children}</>;
} 