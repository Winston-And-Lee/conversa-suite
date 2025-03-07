'use client';

import { ReactNode } from 'react';
import { FetchMiddlewareProvider } from "@/components/fetch-middleware-provider";

export function ClientLayout({ children }: { children: ReactNode }) {
  return (
    <FetchMiddlewareProvider>
      {children}
    </FetchMiddlewareProvider>
  );
} 